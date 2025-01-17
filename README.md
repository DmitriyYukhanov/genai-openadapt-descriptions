# openadapt-descriptions

A utility script for generating natural language descriptions from OpenAdapt recordings.

## Overview

This script processes OpenAdapt recordings and generates natural language descriptions for each recorded action. It works with the OpenAdapt database to retrieve recordings and their associated actions, with robust error handling and configuration options.

## Features

- Retrieves recordings from OpenAdapt database (latest or by ID)
- Processes action events to generate natural language descriptions
- Saves numbered descriptions to individual files per recording
- Smart file naming with recording ID and task description
- Automatic timestamp-based versioning to prevent overwriting
- Comprehensive error handling and logging
- Configuration management via YAML files
- Command-line interface with multiple options

## Installation

You can use this tool in three ways:

1. **Direct Usage (No Installation)**
   ```bash
   # From the project root directory
   python run.py [OPTIONS]
   ```

2. **Development Installation**
   ```bash
   pip install -e .
   openadapt-descriptions [OPTIONS]
   ```

3. **Regular Installation**
   ```bash
   pip install .
   openadapt-descriptions [OPTIONS]
   ```

## Usage

1. Ensure you have OpenAdapt installed and configured
2. Run the script with optional parameters:
```bash
python run.py [OPTIONS]

Options:
  --config PATH        Path to optional config file
  --recording-id INT   Process specific recording instead of latest
  --force             Overwrite existing files without asking
  --help              Show this message and exit
```
3. Follow prompts to confirm actions and save descriptions

## Configuration

The script can be configured using a YAML file with the following options:
```yaml
output_dir: "prompts"  # Directory for output files
log_level: "INFO"      # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

## Output

Descriptions are saved to the configured output directory with one of these filename formats:
- `prompt_recording_<id>_<task_description>.txt` (if file doesn't exist or user chooses to overwrite)
- `prompt_recording_<id>_<task_description>_YYYYMMDD_HHMMSS.txt` (if file exists and user chooses not to overwrite)

Each description is numbered and saved on a new line in the output file.  
Output example:

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

## Requirements

- Python 3.x
- OpenAdapt
- PyYAML
- Click