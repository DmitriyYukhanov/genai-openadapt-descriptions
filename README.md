# genai-openadapt-descriptions

A utility script for generating natural language descriptions from OpenAdapt recordings.

## Overview

This script processes OpenAdapt recordings and generates natural language descriptions for each recorded action. It works with the OpenAdapt database to retrieve recordings and their associated actions.

## Features

- Retrieves the latest recording from OpenAdapt database
- Processes action events to generate natural language descriptions
- Saves numbered descriptions to individual files per recording
- Smart file naming with recording ID and name
- Automatic timestamp-based versioning to prevent overwriting
- Comprehensive logging
- Error handling and user confirmation at key steps

## Usage

1. Ensure you have OpenAdapt installed and configured
2. Run the script:
`python generate_descriptions.py`

The script will:
1. Find the latest recording from the database
2. Display recording ID and name
3. Ask for confirmation to process the events
4. Generate descriptions for each action
5. Save the results with numbered descriptions

## Interactive Prompts

The script will ask for confirmation at several points:
- Before generating descriptions
- Before overwriting existing files (with option to save as a new version)

## Output

Descriptions are saved to the `prompts` directory with one of these filename formats:
- `prompt_recording_<id>_<recording_name>.txt` (if file doesn't exist or user chooses to overwrite)
- `prompt_recording_<id>_<recording_name>_YYYYMMDD_HHMMSS.txt` (if file exists and user chooses not to overwrite)

Each description is numbered and saved on a new line in the output file:

## Requirements

- Python 3.x
- OpenAdapt

## Error Handling

The script includes comprehensive error handling and logging:
- Database connection issues
- Action processing errors
- File I/O errors

Logs include timestamps and are displayed in the console during execution.