"""Database operations for OpenAdapt recordings.

This module handles database connections and recording retrieval with proper
error handling and retry logic for transient failures.
"""

from contextlib import contextmanager
from typing import Optional, Iterator
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from openadapt.db import crud
from openadapt.models import Recording
from openadapt_descriptions.config import Config
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError, TimeoutError
from . import constants

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Database operation errors"""
    pass

# Retry decorator for database operations
def db_retry():
    return retry(
        retry=retry_if_exception_type((OperationalError, TimeoutError)),
        stop=stop_after_attempt(constants.DB_MAX_RETRIES),
        wait=wait_exponential(
            multiplier=1,
            min=constants.DB_RETRY_DELAY,
            max=constants.DB_RETRY_DELAY * 2
        ),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"Database operation failed, retrying in {retry_state.next_action.sleep} seconds..."
        )
    )

@contextmanager
def database_session(cfg: Config) -> Iterator[Session]:
    """Provide a database session context.
    
    Yields:
        SQLAlchemy session object
        
    Raises:
        DatabaseError: If database operations fail
    """
    session = None
    try:
        session = crud.get_new_session(read_only=True)
        session.get_bind().execution_options(timeout=cfg.db_timeout)
        yield session
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database error: {e}")
    finally:
        if session:
            session.close()

@db_retry()
def get_recording(session: Session, recording_id: Optional[int] = None) -> Optional[Recording]:
    """Retrieve a recording from the database with retry logic.
    
    If no recording_id is provided, retrieves the latest recording.
    Includes retry logic for transient database failures.
    
    Args:
        session: Active database session
        recording_id: Optional specific recording ID to retrieve
        
    Returns:
        Recording if found and valid, None otherwise
        
    Raises:
        DatabaseError: If database operations fail after retries
    """
    try:
        logger.info("Retrieving recording", extra={
            "recording_id": recording_id or "latest",
            "session_id": id(session)
        })
        if recording_id:
            recording = crud.get_recording_by_id(session, recording_id)
            if not recording:
                logger.warning(f"Recording with ID {recording_id} not found")
                return None
        else:
            recording = crud.get_latest_recording(session)
            if not recording:
                logger.warning("No recordings found in the database")
                return None

        session.refresh(recording, attribute_names=['action_events'])
        if not recording.action_events:
            logger.warning(f"No action events found in recording {recording.id}")
            return None

        logger.info("Found recording", extra={
            "recording_id": recording.id,
            "task": recording.task_description,
            "event_count": len(recording.action_events)
        })
        return recording
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving recording: {e}") 