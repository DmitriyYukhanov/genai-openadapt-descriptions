"""File storage operations for generated descriptions.

This module handles saving generated descriptions to files with proper
naming, organization, and error handling. Includes retry logic for
file system operations.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Sequence
import logging
from .config import Config
from .processors import ProcessingError
from . import DescriptionT
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from . import constants

logger = logging.getLogger(__name__)

def sanitize_filename(name: str) -> str:
    """Create a filesystem-safe filename.
    
    Args:
        name: Original filename or description
        
    Returns:
        Sanitized filename safe for all filesystems
    """
    if not name:
        return "unnamed"
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    return sanitized[:constants.MAX_FILENAME_LENGTH]

def file_retry():
    return retry(
        retry=retry_if_exception_type((OSError, IOError)),
        stop=stop_after_attempt(constants.FILE_MAX_RETRIES),
        wait=wait_exponential(
            multiplier=0.5,
            min=constants.FILE_MIN_RETRY_DELAY,
            max=constants.FILE_MAX_RETRY_DELAY
        ),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"File operation failed, retrying in {retry_state.next_action.sleep} seconds..."
        )
    )

@file_retry()
def write_descriptions(path: Path, content: str) -> None:
    """Write descriptions to file with retry logic.
    
    Args:
        path: Path where to write the file
        content: String content to write
        
    Raises:
        OSError: If file operations fail after retries
    """
    path.write_text(content, encoding='utf-8')

def save_descriptions(
    cfg: Config,
    descriptions: Sequence[DescriptionT],
    recording_id: int,
    task_description: str,
    force: bool = False
) -> Path:
    """Save descriptions to a file.
    
    Args:
        cfg: Configuration object
        descriptions: Sequence of descriptions to save
        recording_id: ID of the recording
        task_description: Description of the task
        force: Whether to force overwrite existing file
        
    Returns:
        Path to the saved file
        
    Raises:
        ProcessingError: If file operations fail
    """
    logger.info("Saving descriptions", extra={
        "description_count": len(descriptions),
        "recording_id": recording_id,
        "force_overwrite": force,
        "output_dir": str(cfg.output_dir)
    })

    if not descriptions:
        raise ValueError("No descriptions to save")

    content = "\n".join(f"{i+1}. {desc}" for i, desc in enumerate(descriptions)) + "\n"
    if len(content.encode('utf-8')) > cfg.max_file_size:
        raise ProcessingError(f"Output file would be too large (>{cfg.max_file_size/1_000_000:.1f}MB)")

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
        
        write_descriptions(prompt_file_path, content)
        logger.info(f"Successfully saved descriptions to {prompt_file_path}")
        content_size = len(content.encode('utf-8'))
        logger.debug("Content statistics", extra={
            "size_bytes": content_size,
            "size_mb": content_size / 1_000_000
        })
        return prompt_file_path
    except Exception as e:
        raise ProcessingError(f"Error saving descriptions to file: {e}") 