import logging
import os
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_descriptions(descriptions: list) -> bool:
    """Validate the generated descriptions using Claude LLM.

    Args:
        descriptions: List of generated descriptions.

    Returns:
        True if the descriptions are valid, False otherwise.

    Raises:
        ValidationError: If the validation request fails.
    """
    prompt = (
        "Please analyze the following list of descriptions:\n"
        + "\n".join(f"{i + 1}. {desc}" for i, desc in enumerate(descriptions)) + "\n"
        "Do these descriptions look like expected human-readable numerated items which can be used to replay some actions in systems like Claude Computrer Use? "
        "Reply strictly with 'true' or 'false' only."
    )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValidationError("API key for Anthropic is not set.")
    
    try:
        client = Anthropic(
            api_key=api_key,  # This is the default and can be omitted
        )

        message = client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="claude-3-5-sonnet-latest",
        )

        result = message.content[0].text

        if result == "true":
            return True
        elif result == "false":
            return False
        else:
            raise ValidationError(f"Unexpected response from Claude: {result}")
    except anthropic.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
    except anthropic.RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
    except anthropic.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
    except Exception as e:
        logger.error(f"Validation request failed: {e}")
        raise ValidationError("Failed to validate descriptions.") 