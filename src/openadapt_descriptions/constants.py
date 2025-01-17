"""Constants used throughout the OpenAdapt Descriptions package."""

from pathlib import Path

# File paths and directories
DEFAULT_OUTPUT_DIR = Path('prompts')
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / 'configs' / 'default_config.yaml'

# Logging levels
DEFAULT_LOG_LEVEL = 'INFO'
VALID_LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Processing limits
MAX_FILENAME_LENGTH = 255
MAX_EVENTS_WITHOUT_CONFIRM = 100  # Number of events before requiring confirmation
MAX_FILE_SIZE = 10_000_000  # 10MB in bytes
MAX_ERROR_RATIO = 0.5  # Maximum ratio of errors before failing

# Database settings
DB_TIMEOUT = 60  # seconds
DB_MAX_RETRIES = 3
DB_RETRY_DELAY = 4  # seconds

# API settings
API_MAX_RETRIES = 3
API_MIN_RETRY_DELAY = 2  # seconds
API_MAX_RETRY_DELAY = 8  # seconds

# File operation settings
FILE_MAX_RETRIES = 3
FILE_MIN_RETRY_DELAY = 1  # seconds
FILE_MAX_RETRY_DELAY = 5  # seconds

# Progress estimation
SECONDS_PER_EVENT = 2  # Rough estimate for time per event processing 