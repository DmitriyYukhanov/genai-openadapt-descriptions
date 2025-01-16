import logging
from pathlib import Path
from typing import List, Optional
from openadapt.db import crud
from openadapt.models import ActionEvent, Recording
from datetime import datetime
import re
from dataclasses import dataclass
import yaml
import click

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    output_dir: Path
    log_level: str

def load_config(config_path: Optional[Path] = None) -> Config:
    if config_path and config_path.exists():
        with config_path.open() as f:
            config = yaml.safe_load(f)
            config['output_dir'] = Path(config['output_dir'])
            logger.info(f"Using config from {config_path}: {config}")
            return Config(**config)
    
    default_config_path = Path(__file__).parent / 'configs' / 'default_config.yaml'
    if default_config_path.exists():
        with default_config_path.open() as f:
            config = yaml.safe_load(f)
            config['output_dir'] = Path(config['output_dir'])
            logger.info(f"Using default config: {config}")
            return Config(**config)
    
    logger.info("No config file found, using hardcoded defaults")
    return Config(
        output_dir=Path('prompts'),
        log_level='INFO'
    )

def get_recording(session, recording_id: Optional[int] = None) -> Optional[Recording]:
    if recording_id:
        recording = crud.get_recording_by_id(session, recording_id)
    else:
        recording = crud.get_latest_recording(session)
    if not recording:
        logger.warning("No recordings found in the database")
        return None
    session.refresh(recording, attribute_names=['action_events'])
    logger.info(f"Found recording {recording.id}:{recording.task_description}")
    return recording

def process_action_events(recording: Recording) -> List[str]:
    action_events = recording.processed_action_events
    total_events = len(action_events)
    
    logger.info(f"Found {total_events} events to process in recording {recording.id}:{recording.task_description}")
    confirmation = input(f"Do you want to generate descriptions for {total_events} events? (y/n): ").lower()
    if confirmation != 'y':
        logger.info("Operation cancelled by user")
        return []

    descriptions = []
    action_count = 0
    
    logger.info(f"Processing {total_events} events from the recording")
    for idx, action in enumerate(action_events, 1):
        if not isinstance(action, ActionEvent):
            continue
            
        action_count += 1
        logger.debug(f"Processing action {action_count} (Event {idx}/{total_events})")
        
        try:
            description = action.prompt_for_description()
            logger.debug(f"Generated description: {description}")
            descriptions.append(description)
        except Exception as e:
            logger.error(f"Error processing action {action_count}: {str(e)}")

    logger.info(f"Generated {len(descriptions)} descriptions from {action_count} actions")
    return descriptions

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def save_descriptions(cfg: Config, descriptions: List[str], recording: Recording, force: bool) -> None:
    if not descriptions:
        return

    cfg.output_dir.mkdir(exist_ok=True)
    safe_name = sanitize_filename(recording.task_description)
    base_path = cfg.output_dir / f"prompt_recording_{recording.id}_{safe_name}"
    prompt_file_path = base_path.with_suffix('.txt')
    
    if prompt_file_path.exists() and not force:
        confirmation = input(f"File {prompt_file_path} already exists. Do you want to overwrite it? (y/n): ").lower()
        if confirmation != 'y':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_file_path = base_path.with_name(f"{base_path.name}_{timestamp}").with_suffix('.txt')
            logger.info(f"Saving to new file: {prompt_file_path}")
    
    try:
        numbered_descriptions = [f"{i+1}. {desc}" for i, desc in enumerate(descriptions)]
        prompt_file_path.write_text("\n".join(numbered_descriptions) + "\n")
        logger.info(f"Successfully saved descriptions to {prompt_file_path}")
    except Exception as e:
        logger.error(f"Error saving descriptions to file: {str(e)}")

def generate_action_descriptions(cfg: Config, recording_id: Optional[int] = None, force: bool = False) -> None:
    logger.info("Starting action description generation")
    
    session = crud.get_new_session(read_only=True)
    recording = get_recording(session, recording_id)
    if not recording:
        return
            
    descriptions = process_action_events(recording)
    if not descriptions:
        return
    save_descriptions(cfg, descriptions, recording, force)

@click.command()
@click.option('--config', type=click.Path(exists=True, path_type=Path), help='Path to optional config file')
@click.option('--recording-id', type=int, help='Process specific recording instead of latest')
@click.option('--batch-size', type=int, help='Override batch size from config')
@click.option('--force', is_flag=True, help='Overwrite existing files without asking')
def main(config: Optional[Path], recording_id: Optional[int], batch_size: Optional[int], force: bool):
    """Generate natural language descriptions from OpenAdapt recordings."""
    cfg = load_config(config)
    if batch_size:
        cfg.batch_size = batch_size
    
    try:
        generate_action_descriptions(cfg, recording_id, force)
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {str(e)}")

if __name__ == "__main__":
    main()