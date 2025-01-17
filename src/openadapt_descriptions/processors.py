"""Action event processing and description generation.

This module provides the core functionality for converting OpenAdapt
action events into natural language descriptions. It includes retry logic
for API calls and proper error handling.
"""

from typing import List, Iterator, Sequence
from . import DescriptionGenerator, DescriptionT, ActionProcessor
from openadapt.models import Recording, ActionEvent
import logging
from openadapt_descriptions.config import Config
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import click
from . import constants

logger = logging.getLogger(__name__)

class ProcessingError(Exception):
    """Action processing errors"""
    pass

class APIError(Exception):
    """API call errors"""
    pass

def api_retry():
    return retry(
        retry=retry_if_exception_type(APIError),
        stop=stop_after_attempt(constants.API_MAX_RETRIES),
        wait=wait_exponential(
            multiplier=1,
            min=constants.API_MIN_RETRY_DELAY,
            max=constants.API_MAX_RETRY_DELAY
        ),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"API call failed, retrying in {retry_state.next_action.sleep} seconds..."
        )
    )

class DefaultGenerator(DescriptionGenerator):
    """Default implementation of description generation using OpenAdapt's built-in method."""
    
    @api_retry()
    def generate_description(self, action: ActionEvent) -> DescriptionT:
        """Generate description with retry logic for API calls.
        
        Args:
            action: The action event to describe
            
        Returns:
            Generated description
            
        Raises:
            APIError: If API call fails after retries
        """
        return action.prompt_for_description()

class DefaultProcessor(ActionProcessor):
    """Process action events using a provided generator."""
    
    def __init__(self, generator: DescriptionGenerator, progress_bar=None) -> None:
        self.generator = generator
        self.progress_bar = progress_bar

    def process(self, events: Sequence[ActionEvent]) -> Iterator[DescriptionT]:
        """Process a sequence of action events into descriptions.
        
        Args:
            events: Sequence of action events to process
            
        Yields:
            Generated descriptions for valid actions
            
        Raises:
            ProcessingError: If too many errors occur during processing
        """
        total_events = len(events)
        action_count = 0  # Initialize counter
        errors_count = 0  # Initialize counter
        last_progress = 0  # Track last progress update
        
        logger.info("Starting event processing", extra={
            "total_events": total_events,
            "processor": self.__class__.__name__
        })
        
        for idx, action in enumerate(events, 1):
            if not isinstance(action, ActionEvent):
                logger.warning(f"Skipping event {idx}: not an ActionEvent")
                continue
                
            action_count += 1
            
            try:
                description = self.generator.generate_description(action)
                if description:
                    yield description
                
                # Update progress bar
                if self.progress_bar:
                    current_progress = int((idx / total_events) * 100)
                    if current_progress > last_progress:
                        self.progress_bar.update(current_progress - last_progress)
                        last_progress = current_progress
                        
            except Exception as e:
                errors_count += 1
                logger.error(f"Error processing action {action_count}: {str(e)}")
                if errors_count > total_events * constants.MAX_ERROR_RATIO:
                    raise ProcessingError("Too many errors during processing")

def process_action_events(cfg: Config, recording: Recording, progress_bar=None) -> List[DescriptionT]:
    """Process action events from a recording.
    
    Args:
        cfg: Configuration object
        recording: Recording containing action events
        progress_bar: Optional Click progress bar for overall progress
        
    Returns:
        List of generated descriptions
        
    Raises:
        ProcessingError: If processing fails
    """
    if not recording.processed_action_events:
        raise ProcessingError("No processed action events available")

    logger.info(f"Loading processed action events from the recording...")
    action_events = recording.processed_action_events
    total_events = len(action_events)
    
    if total_events > cfg.max_events:
        click.echo("\nWarning: Large number of events detected")
        click.echo(f"Found {total_events} events to process")
        click.echo(f"This will make {total_events} API calls to generate descriptions")
        click.echo(f"\nEstimated time: ~{(total_events * constants.SECONDS_PER_EVENT) / 60:.1f} minutes")
        
        if not click.confirm("Do you want to continue?"):
            logger.info("Operation cancelled by user")
            return []

    generator = DefaultGenerator()
    processor = DefaultProcessor(generator, progress_bar)
    
    descriptions = list(processor.process(action_events))

    # Add a newline after progress bar completes
    if progress_bar:
        click.echo("")  # This will add the needed newline

    if not descriptions:
        logger.warning("No descriptions were generated")
        return []

    logger.info(f"Generated {len(descriptions)} descriptions")
    return descriptions 