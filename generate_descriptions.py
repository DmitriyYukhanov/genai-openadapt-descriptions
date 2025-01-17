import logging
from pathlib import Path
from typing import List, Optional, NoReturn
from openadapt.db import crud
from openadapt.models import ActionEvent, Recording
from datetime import datetime
import re
from dataclasses import dataclass
import yaml
import click
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DescriptionGenerationError(Exception):
    """Base exception for description generation errors"""
    pass

class ConfigError(DescriptionGenerationError):
    """Configuration related errors"""
    pass

class DatabaseError(DescriptionGenerationError):
    """Database operation errors"""
    pass

class ProcessingError(DescriptionGenerationError):
    """Action processing errors"""
    pass

@dataclass
class Config:
    output_dir: Path
    log_level: str

    def validate(self) -> None:
        """Validate configuration values"""
        if not isinstance(self.output_dir, Path):
            raise ConfigError("output_dir must be a Path object")
        if self.log_level not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            raise ConfigError(f"Invalid log level: {self.log_level}")

def load_config(config_path: Optional[Path] = None) -> Config:
    try:
        if config_path and config_path.exists():
            with config_path.open() as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ConfigError("Invalid config format")
                config['output_dir'] = Path(config.get('output_dir', 'prompts'))
                logger.info(f"Using config from {config_path}: {config}")
                cfg = Config(**config)
                cfg.validate()
                return cfg
        
        default_config_path = Path(__file__).parent / 'configs' / 'default_config.yaml'
        if default_config_path.exists():
            with default_config_path.open() as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ConfigError("Invalid default config format")
                config['output_dir'] = Path(config.get('output_dir', 'prompts'))
                logger.info(f"Using default config: {config}")
                cfg = Config(**config)
                cfg.validate()
                return cfg
        
        logger.info("No config file found, using hardcoded defaults")
        cfg = Config(
            output_dir=Path('prompts'),
            log_level='INFO'
        )
        cfg.validate()
        return cfg
    except yaml.YAMLError as e:
        raise ConfigError(f"Error parsing config file: {e}")
    except Exception as e:
        raise ConfigError(f"Error loading config: {e}")

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

def process_action_events(recording: Recording) -> List[str]:
    if not recording.processed_action_events:
        raise ProcessingError("No processed action events available")

    action_events = recording.processed_action_events
    total_events = len(action_events)
    
    if total_events == 0:
        logger.warning("No events to process")
        return []

    logger.info(f"Found {total_events} events to process in recording {recording.id}:{recording.task_description}")
    confirmation = input(f"Do you want to generate descriptions for {total_events} events? (y/n): ").lower()
    if confirmation != 'y':
        logger.info("Operation cancelled by user")
        return []

    descriptions = []
    action_count = 0
    errors_count = 0
    
    logger.info(f"Processing {total_events} events from the recording")
    for idx, action in enumerate(action_events, 1):
        if not isinstance(action, ActionEvent):
            logger.warning(f"Skipping event {idx}: not an ActionEvent")
            continue
            
        action_count += 1
        logger.debug(f"Processing action {action_count} (Event {idx}/{total_events})")
        
        try:
            description = action.prompt_for_description()
            if not description:
                logger.warning(f"Empty description for action {action_count}")
                continue
            logger.debug(f"Generated description: {description}")
            descriptions.append(description)
        except Exception as e:
            errors_count += 1
            logger.error(f"Error processing action {action_count}: {str(e)}")
            if errors_count > total_events // 2:
                raise ProcessingError("Too many errors during processing")

    if not descriptions:
        logger.warning("No descriptions were generated")
        return []

    logger.info(f"Generated {len(descriptions)} descriptions from {action_count} actions ({errors_count} errors)")
    return descriptions

def sanitize_filename(name: str) -> str:
    if not name:
        return "unnamed"
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    return sanitized[:255]  # Maximum filename length

def save_descriptions(cfg: Config, descriptions: List[str], recording: Recording, force: bool) -> None:
    if not descriptions:
        raise ValueError("No descriptions to save")

    try:
        cfg.output_dir.mkdir(exist_ok=True, parents=True)
        safe_name = sanitize_filename(recording.task_description or "unnamed")
        base_path = cfg.output_dir / f"prompt_recording_{recording.id}_{safe_name}"
        prompt_file_path = base_path.with_suffix('.txt')
        
        if prompt_file_path.exists() and not force:
            confirmation = input(f"File {prompt_file_path} already exists. Do you want to overwrite it? (y/n): ").lower()
            if confirmation != 'y':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                prompt_file_path = base_path.with_name(f"{base_path.name}_{timestamp}").with_suffix('.txt')
                logger.info(f"Saving to new file: {prompt_file_path}")
        
        numbered_descriptions = [f"{i+1}. {desc}" for i, desc in enumerate(descriptions)]
        prompt_file_path.write_text("\n".join(numbered_descriptions) + "\n", encoding='utf-8')
        logger.info(f"Successfully saved descriptions to {prompt_file_path}")
    except OSError as e:
        raise ProcessingError(f"Error saving descriptions to file: {e}")

def generate_action_descriptions(cfg: Config, recording_id: Optional[int] = None, force: bool = False) -> None:
    logger.info("Starting action description generation")
    
    try:
        with database_session() as session:
            recording = get_recording(session, recording_id)
            if not recording:
                return
                
            descriptions = process_action_events(recording)
            if not descriptions:
                return
            save_descriptions(cfg, descriptions, recording, force)
    except DescriptionGenerationError as e:
        logger.error(str(e))
        raise

@click.command()
@click.option('--config', type=click.Path(exists=True, path_type=Path), help='Path to optional config file')
@click.option('--recording-id', type=int, help='Process specific recording instead of latest')
@click.option('--force', is_flag=True, help='Overwrite existing files without asking')
def main(config: Optional[Path], recording_id: Optional[int], force: bool):
    """Generate natural language descriptions from OpenAdapt recordings."""
    try:
        cfg = load_config(config)
        generate_action_descriptions(cfg, recording_id, force)
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {str(e)}")
        raise click.ClickException(str(e))

if __name__ == "__main__":
    main()