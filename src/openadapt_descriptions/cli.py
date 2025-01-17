import click
from pathlib import Path
from typing import Optional
import logging
from . import config as config_module
from . import processors, storage, database
from openadapt_descriptions.config import Config
logger = logging.getLogger(__name__)
from .post_processing import validate_descriptions 

def generate_action_descriptions(cfg: Config, recording_id: Optional[int] = None, force: bool = False, progress_bar=None) -> None:
    
    try:
        with database.database_session(cfg) as session:
            recording = database.get_recording(session, recording_id)
            if not recording:
                return
                
            descriptions = processors.process_action_events(cfg, recording, progress_bar)
            if not descriptions:
                return
            
            if not validate_descriptions(descriptions):
                logger.warning("Generated descriptions seem to be not valid!")
            else:
                logger.info("Generated descriptions seem to be valid")

            storage.save_descriptions(cfg, descriptions, recording.id, recording.task_description, force)
    except Exception as e:
        logger.error(str(e))
        raise

@click.command(help="""
Generate natural language descriptions from OpenAdapt recordings.

This tool processes OpenAdapt recordings and generates human-readable descriptions
of the recorded actions. It can process either the latest recording or a specific
recording by ID.

The generated descriptions are saved to text files in the configured output
directory, with options to handle file naming and overwriting.
""")
@click.option(
    '--config',
    type=click.Path(exists=True, path_type=Path),
    help='Path to config file (optional, will use defaults if not provided)'
)
@click.option(
    '--recording-id',
    type=int,
    help='ID of specific recording to process (uses latest if not provided)'
)
@click.option(
    '--force',
    is_flag=True,
    help='Overwrite existing files without asking for confirmation'
)
@click.option(
    '--quiet',
    is_flag=True,
    help='Reduce output verbosity (only show errors and critical information)'
)
def main(config: Optional[Path], recording_id: Optional[int], force: bool, quiet: bool):
    """CLI entry point."""
    try:
        if quiet:
            logging.getLogger().setLevel(logging.WARNING)
            
        cfg = config_module.load_config(config)
        if not quiet:
            logging.getLogger().setLevel(cfg.log_level)
            
        with click.progressbar(
            length=100,
            label='Generating action descriptions'
        ) as progress_bar:
            click.echo("")
            generate_action_descriptions(cfg, recording_id, force, progress_bar=progress_bar)
            
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