import sys
from pathlib import Path

# Add src directory to Python path
src_path = str(Path(__file__).parent / 'src')
sys.path.insert(0, src_path)

from openadapt_descriptions.cli import main

if __name__ == "__main__":
    main() 