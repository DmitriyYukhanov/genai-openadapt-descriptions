# genai-openadapt-descriptions

A utility script for generating natural language descriptions from OpenAdapt recordings.

## Overview

This script processes OpenAdapt recordings and generates natural language descriptions for each recorded action.

## Features

- Retrieves the latest recording from OpenAdapt database
- Processes action events to generate natural language descriptions
- Saves descriptions to individual files per recording
- Automatic timestamp-based file naming to prevent overwriting
- Comprehensive logging
- Error handling and user confirmation at key steps

## Usage

1. Ensure you have OpenAdapt installed and configured
2. Run the script:
`python generate_descriptions.py`

The script will:
1. Find the latest recording
2. Ask for confirmation to process the events
3. Generate descriptions for each action
4. Save the results to `prompts/prompt_recording_<id>.txt` or `prompts/prompt_recording_<id>_YYYYMMDD_HHMMSS.txt` if file exists

## Interactive Prompts

The script will ask for confirmation at several points:
- Before generating descriptions
- Before overwriting existing files (with option to save to a new timestamped file)

## Output

Descriptions are saved to the `prompts` directory with one of these filename formats:
- `prompt_recording_<recording_id>.txt` (if file doesn't exist or user chooses to overwrite)
- `prompt_recording_<recording_id>_YYYYMMDD_HHMMSS.txt` (if file exists and user chooses not to overwrite)

Each description is saved on a new line in the output file.

## Requirements

- Python 3.x
- OpenAdapt

## Error Handling

The script includes comprehensive error handling and logging:
- Database connection issues
- Action processing errors
- File I/O errors

Logs include timestamps and are displayed in the console during execution.