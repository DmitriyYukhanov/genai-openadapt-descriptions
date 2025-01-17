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
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
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
    
    def __init__(self, generator: DescriptionGenerator) -> None:
        self.generator = generator

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
        
        logger.info("Starting event processing", extra={
            "total_events": total_events,
            "processor": self.__class__.__name__
        })
        
        for idx, action in enumerate(events, 1):
            logger.debug("Processing action", extra={
                "action_index": idx,
                "total_events": total_events,
                "action_type": type(action).__name__
            })
            if not isinstance(action, ActionEvent):
                logger.warning(f"Skipping event {idx}: not an ActionEvent")
                continue
                
            action_count += 1
            logger.debug(f"Processing action {action_count} (Event {idx}/{total_events})")
            
            try:
                description = self.generator.generate_description(action)
                if not description:
                    logger.warning(f"Empty description for action {action_count}")
                    continue
                logger.debug(f"Generated description: {description}")
                yield description
            except Exception as e:
                errors_count += 1
                logger.error(f"Error processing action {action_count}: {str(e)}")
                if errors_count > total_events // 2:
                    raise ProcessingError("Too many errors during processing")

def process_action_events(recording: Recording) -> List[DescriptionT]:
    """Process action events from a recording.
    
    Args:
        recording: Recording containing action events
        
    Returns:
        List of generated descriptions
        
    Raises:
        ProcessingError: If processing fails
    """
    if not recording.processed_action_events:
        raise ProcessingError("No processed action events available")

    logger.info(f"Loading processed action events from the recording...")
    action_events = recording.processed_action_events # long-running operation
    total_events = len(action_events)
    
    if total_events == 0:
        logger.warning("No events to process")
        return []
    
    # Confirm descriptions generation before processing large recordings
    cfg = Config()
    if total_events > cfg.max_events:
        logger.info(f"About to generate descriptions for {total_events} events. This will emit {total_events} Anthropic API calls under the hood.")
        confirmation = input("Do you want to proceed? (y/n): ").lower()
        if confirmation != 'y':
            logger.info("Description generation cancelled by user")
            return []

    generator = DefaultGenerator()
    processor = DefaultProcessor(generator)
    
    descriptions = list(processor.process(action_events))

    if not descriptions:
        logger.warning("No descriptions were generated")
        return []

    logger.info(f"Generated {len(descriptions)} descriptions")
    return descriptions 