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
        npm_path = shutil.which('npm')
        if npm_path:
            return npm_path
            
        possible_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'nodejs', 'npm.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'nodejs', 'npm.cmd')
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
                
    return 'npm'  # Default fallback

def find_uv_path() -> str:
    """Find the uv executable path."""
    if platform.system() == 'Windows':
        uv_path = shutil.which('uv.cmd')
        if uv_path:
            return uv_path
        # Look in common installation locations
        possible_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'uv', 'uv.exe'),
            os.path.join(os.environ.get('APPDATA', ''), 'uv', 'uv.exe')
        ]
        for path in possible_paths:
            if os.path.isfile(path):
                return path
    else:
        uv_path = shutil.which('uv')
        if uv_path:
            return uv_path
    return 'uv'  # Default fallback

# Package Manager Configuration
ALLOWED_PACKAGES: List[str] = os.getenv('ALLOWED_PACKAGES', 'typescript,react,express').split(',')
MAX_INSTALL_SIZE: int = int(os.getenv('MAX_INSTALL_SIZE', '50000000'))
PROJECT_DIR: str = os.getenv('PROJECT_DIR', 'H:/projects')
INSTALL_TIMEOUT: int = int(os.getenv('INSTALL_TIMEOUT', '300000'))
UNINSTALL_TIMEOUT: int = int(os.getenv('UNINSTALL_TIMEOUT', '60000'))
INIT_TIMEOUT: int = int(os.getenv('INIT_TIMEOUT', '30000'))
VENV_TIMEOUT: int = int(os.getenv('VENV_TIMEOUT', '30000'))  # Added for venv creation

# Node.js Package Manager Configuration
NPM_PATH: str = find_npm_path()
NODE_ENV: str = os.getenv('NODE_ENV', 'development')

# Python Package Manager Configuration
PIP_PATH: str = os.getenv('PIP_PATH', 'pip')
UV_PATH: str = os.getenv('UV_PATH', find_uv_path())
USE_UV: bool = os.getenv('USE_UV', 'true').lower() == 'true'
PYTHON_ENV: str = os.getenv('PYTHON_ENV', 'development')
VENV_NAME: str = os.getenv('VENV_NAME', '.venv')  # Default venv directory name

# Logging Configuration
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG').upper()