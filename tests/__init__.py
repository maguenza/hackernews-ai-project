"""
Test package for HackerNews AI project.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path for all tests
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root)) 