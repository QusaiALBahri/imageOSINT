"""
OSINT Image Tool - Architecture Overview
"""

# Create placeholder files for uploads and outputs
import os
from pathlib import Path

# Create .gitkeep files to ensure directories are tracked
Path("uploads/.gitkeep").parent.mkdir(parents=True, exist_ok=True)
Path("uploads/.gitkeep").touch(exist_ok=True)

Path("outputs/.gitkeep").parent.mkdir(parents=True, exist_ok=True)
Path("outputs/.gitkeep").touch(exist_ok=True)

Path("logs/.gitkeep").parent.mkdir(parents=True, exist_ok=True)
Path("logs/.gitkeep").touch(exist_ok=True)

print("✓ Project structure initialized")
