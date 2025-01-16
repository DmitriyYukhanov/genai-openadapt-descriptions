import logging
from pathlib import Path
from typing import List, Optional
from openadapt.db import crud
from openadapt.models import ActionEvent, Recording
from datetime import datetime
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

PROMPTS_DIR = Path("prompts")

def get_recording(session) -> Optional[Recording]:
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

def save_descriptions(descriptions: List[str], recording: Recording) -> None:
    if not descriptions:
        return

    PROMPTS_DIR.mkdir(exist_ok=True)
    safe_name = sanitize_filename(recording.task_description)
    base_path = PROMPTS_DIR / f"prompt_recording_{recording.id}_{safe_name}"
    prompt_file_path = base_path.with_suffix('.txt')
    
    if prompt_file_path.exists():
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

def generate_action_descriptions() -> None:
    logger.info("Starting action description generation")
    
    session = crud.get_new_session(read_only=True)
    recording = get_recording(session)
    if not recording:
        return
            
    descriptions = process_action_events(recording)
    if not descriptions:
        return
    save_descriptions(descriptions, recording)

if __name__ == "__main__":
    try:
        generate_action_descriptions()
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {str(e)}")