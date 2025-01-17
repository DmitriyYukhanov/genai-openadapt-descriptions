"""OpenAdapt Descriptions - Generate natural language descriptions for OpenAdapt recordings."""

from typing import Protocol, Sequence, Iterator, TypeVar, List
from pathlib import Path
from openadapt.models import ActionEvent, Recording

# Type variables
DescriptionT = str  # For clarity of what strings represent
ActionT = TypeVar('ActionT', bound=ActionEvent)

# Protocols
class DescriptionGenerator(Protocol):
    """Protocol for description generators"""
    def generate_description(self, action: ActionEvent) -> DescriptionT: ...

class ActionProcessor(Protocol):
    """Protocol for action processors"""
    def process(self, events: Sequence[ActionEvent]) -> Iterator[DescriptionT]: ...

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