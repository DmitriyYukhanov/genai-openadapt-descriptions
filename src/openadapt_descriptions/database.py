from contextlib import contextmanager
from typing import Optional, Iterator
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from openadapt.db import crud
from openadapt.models import Recording
from openadapt_descriptions.config import Config

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Database operation errors"""
    pass

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

def get_recording(session: Session, recording_id: Optional[int] = None) -> Optional[Recording]:
    """Retrieve a recording from the database.
    
    Args:
        session: Database session
        recording_id: Optional ID of specific recording
        
    Returns:
        Recording if found, None otherwise
        
    Raises:
        DatabaseError: If database operations fail
    """
    try:
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

        logger.info(f"Found recording {recording.id}:{recording.task_description}")
        return recording
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving recording: {e}") 