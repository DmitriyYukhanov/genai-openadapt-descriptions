"""OpenAdapt Descriptions - Generate natural language descriptions for OpenAdapt recordings."""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from .config import Config, load_config, ConfigError
from .processors import DescriptionGenerator, DefaultGenerator, process_action_events, ProcessingError
from .storage import save_descriptions, sanitize_filename
from .database import database_session, get_recording, DatabaseError

__version__ = "0.1.0"

__all__ = [
    "Config",
    "load_config",
    "ConfigError",
    "DescriptionGenerator",
    "DefaultGenerator",
    "process_action_events",
    "ProcessingError",
    "save_descriptions",
    "sanitize_filename",
    "database_session",
    "get_recording",
    "DatabaseError",
] 