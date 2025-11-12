#!/usr/bin/env python3
"""
AI OS Quick Start Script
Launch the unified client with all features.
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_os.unified_client import main

if __name__ == '__main__':
    sys.exit(main())
