from contextlib import contextmanager
from typing import Optional
import logging
from sqlalchemy.exc import SQLAlchemyError
from openadapt.db import crud
from openadapt.models import Recording

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Database operation errors"""
    pass

@contextmanager
def database_session():
    """Context manager for database sessions with proper error handling"""
    session = None
    try:
        session = crud.get_new_session(read_only=True)
        yield session
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database error: {e}")
    finally:
        if session:
            session.close()

def get_recording(session, recording_id: Optional[int] = None) -> Optional[Recording]:
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