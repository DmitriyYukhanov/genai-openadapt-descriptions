# openadapt-descriptions

A utility script for generating natural language descriptions from OpenAdapt recordings.

## Overview

This script processes OpenAdapt recordings and generates natural language descriptions for each recorded action. It works with the OpenAdapt database to retrieve recordings and their associated actions, with robust error handling and configuration options.

## Prerequisites

- Python 3.x
- At least one existing OpenAdapt recording in the database
- Anthropic API key (set in `.env` file as `ANTHROPIC_API_KEY`)

## Installation

1. **Install Required Tools & Services**
   ```bash
   pip install openadapt click pyyaml tenacity python-dotenv anthropic
   ```

2. **Install the Package (optionally)**
   ```bash
   # Development Installation
   pip install -e .
   
   # or Regular Installation
   pip install .
   ```

## Usage

You can run the script in two ways:

1. **Directly from source**:
```bash
python run.py [OPTIONS]
```

2. **As installed package**:
```bash
openadapt-descriptions [OPTIONS]
```

Available options:
```bash
Options:
  --config PATH        Path to optional config file
  --recording-id INT   Process specific recording instead of latest
  --force             Overwrite existing files without asking
  --help              Show this message and exit
  --quiet             Reduce output verbosity
```

Follow prompts to confirm actions and save descriptions.

## Configuration

The script can be configured using a YAML file with the following options:
```yaml
# Output settings
output_dir: "prompts"  # Directory where prompt files will be saved

# Logging settings
log_level: "INFO"      # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Processing limits
max_events: 100          # Maximum events to process without confirmation
max_file_size: 10000000  # Maximum output file size in bytes
db_timeout: 60           # Database operation timeout in seconds
```

You can specify a custom config file using the `--config` option, otherwise the default configuration from `configs/default_config.yaml` will be used.

## Output

Descriptions are saved to the configured output directory with one of these filename formats:
- `prompt_recording_<id>_<task_description>.txt` (if file doesn't exist or user chooses to overwrite)
- `prompt_recording_<id>_<task_description>_YYYYMMDD_HHMMSS.txt` (if file exists and user chooses not to overwrite)

Example output:
```
1. Move mouse to 'Calculator icon'
2. Left singleclick 'Calculator icon'
3. Move mouse to 'Number 6 key'
4. Left singleclick 'Number 6 key'
5. Move mouse to 'Plus (+) button'
6. Left singleclick 'Plus button'
7. Move mouse to 'Number 3 button'
8. Left singleclick 'Number 3 button'
9. Move mouse to 'Equals (=) button'
10. Left singleclick 'Equals (=) button'
```