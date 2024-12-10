"""
Configuration settings for the MCP Package Manager server.
"""

import os
from typing import List
import platform
import shutil

def find_npm_path() -> str:
    """Find the npm executable path."""
    if platform.system() == 'Windows':
        # First try using shutil which is more reliable
        npm_path = shutil.which('npm')
        if npm_path:
            return npm_path
            
        # Fallback paths without quotes (will be handled in the subprocess call)
        possible_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'nodejs', 'npm.cmd')
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
                
    return 'npm'  # Default fallback

# Package Manager Configuration
ALLOWED_PACKAGES: List[str] = os.getenv('ALLOWED_PACKAGES', 'typescript,react,express').split(',')
MAX_INSTALL_SIZE: int = int(os.getenv('MAX_INSTALL_SIZE', '50000000'))
PROJECT_DIR: str = os.getenv('PROJECT_DIR', 'H:/projects')
INSTALL_TIMEOUT: int = int(os.getenv('INSTALL_TIMEOUT', '300000'))
UNINSTALL_TIMEOUT: int = int(os.getenv('UNINSTALL_TIMEOUT', '60000'))
INIT_TIMEOUT: int = int(os.getenv('INIT_TIMEOUT', '30000'))

# Node.js Package Manager Configuration
NPM_PATH: str = find_npm_path()
NODE_ENV: str = os.getenv('NODE_ENV', 'development')

# Python Package Manager Configuration
PIP_PATH: str = os.getenv('PIP_PATH', 'pip')
PYTHON_ENV: str = os.getenv('PYTHON_ENV', 'development')

# Logging Configuration
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG').upper()