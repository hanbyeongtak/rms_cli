# src/config.py
import os
from pathlib import Path

# This file's path: /path/to/project/src/config.py
# .parent -> /path/to/project/src
# .parent -> /path/to/project
# This provides a reliable absolute path to the project root directory.
ROOT_DIR = Path(__file__).parent.parent.resolve()
