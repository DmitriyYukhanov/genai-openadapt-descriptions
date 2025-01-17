"""OpenAdapt Descriptions - Generate natural language descriptions for OpenAdapt recordings.

This package provides functionality to:
1. Load recordings from OpenAdapt database
2. Process action events into natural language descriptions
3. Save descriptions to files with proper organization

Main components:
- Config: Configuration management
- DescriptionGenerator: Interface for generating descriptions
- ActionProcessor: Interface for processing action events
- Database utilities: Session management and recording retrieval
- Storage utilities: File operations and naming"""

from typing import Protocol, Sequence, Iterator, TypeVar, Any, Dict
from openadapt.models import ActionEvent
from .logging_config import setup_logging

setup_logging()

# Type variables
DescriptionT = str  # For clarity of what strings represent
ActionT = TypeVar('ActionT', bound=ActionEvent)

# Protocols
class DescriptionGenerator(Protocol):
    """Protocol for description generators.
    
    Implementations of this protocol should provide logic to convert
    individual ActionEvents into natural language descriptions.
    """
    def generate_description(self, action: ActionEvent) -> DescriptionT:
        """Generate a description for a single action.
        
        Args:
            action: The action event to describe
            
        Returns:
            A natural language description of the action
        """
        ...

class ActionProcessor(Protocol):
    """Protocol for action processors"""
    def process(self, events: Sequence[ActionEvent]) -> Iterator[DescriptionT]: ...

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