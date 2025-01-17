import re
from datetime import datetime
from pathlib import Path
from typing import List
import logging
from .config import Config
from .processors import ProcessingError

logger = logging.getLogger(__name__)

def sanitize_filename(name: str) -> str:
    if not name:
        return "unnamed"
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    return sanitized[:255]  # Maximum filename length

def save_descriptions(cfg: Config, descriptions: List[str], recording_id: int, task_description: str, force: bool = False) -> None:
    if not descriptions:
        raise ValueError("No descriptions to save")

    try:
        cfg.output_dir.mkdir(exist_ok=True, parents=True)
        safe_name = sanitize_filename(task_description or "unnamed")
        base_path = cfg.output_dir / f"prompt_recording_{recording_id}_{safe_name}"
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