import click
from pathlib import Path
from typing import Optional
import logging
from . import config as config_module
from . import processors, storage, database
from openadapt_descriptions.config import Config
logger = logging.getLogger(__name__)

def generate_action_descriptions(cfg: Config, recording_id: Optional[int] = None, force: bool = False) -> None:
    logger.info("Starting action description generation")
    
    try:
        with database.database_session(cfg) as session:
            recording = database.get_recording(session, recording_id)
            if not recording:
                return
                
            descriptions = processors.process_action_events(recording)
            if not descriptions:
                return
            storage.save_descriptions(cfg, descriptions, recording.id, recording.task_description, force)
    except Exception as e:
        logger.error(str(e))
        raise

@click.command()
@click.option('--config', type=click.Path(exists=True, path_type=Path), help='Path to optional config file')
@click.option('--recording-id', type=int, help='Process specific recording instead of latest')
@click.option('--force', is_flag=True, help='Overwrite existing files without asking')
def main(config: Optional[Path], recording_id: Optional[int], force: bool):
    """Generate natural language descriptions from OpenAdapt recordings."""
    logger.info("Starting description generation", extra={
        "config_path": str(config) if config else None,
        "recording_id": recording_id,
        "force": force
    })
    try:
        cfg = config_module.load_config(config)
        logging.getLogger().setLevel(cfg.log_level)
        generate_action_descriptions(cfg, recording_id, force)
    except config_module.ConfigError as e:
        raise click.ClickException(f"Configuration error: {e}")
    except database.DatabaseError as e:
        raise click.ClickException(f"Database error: {e}")
    except processors.ProcessingError as e:
        raise click.ClickException(f"Processing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise click.ClickException("An unexpected error occurred. Check logs for details.")

if __name__ == "__main__":
    main() 