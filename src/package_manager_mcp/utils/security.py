"""Security utility functions for package management."""

import os
import logging
from typing import Optional
from .. import config

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation utilities for package management."""
    
    @staticmethod
    async def verify_package(package: str, path: Optional[str] = None) -> bool:
        """Verify if package is in whitelist.
        
        Args:
            package: Package name or requirements file flag
            path: Optional path for requirements.txt verification
            
        Returns:
            bool: True if package is allowed, False otherwise
        """
        from ..package_managers import UVPackageManager
        
        # Handle requirements.txt case
        if package == "-r requirements.txt" and path:
            uv_manager = UVPackageManager()
            return await uv_manager.verify_requirements_file(path)
            
        # Allow all packages if wildcard is set
        if "*" in config.ALLOWED_PACKAGES:
            return True

        # Regular package verification
        is_allowed = any(allowed in package for allowed in config.ALLOWED_PACKAGES)
        if not is_allowed:
            logger.warning(f"Package {package} not in whitelist")
        return is_allowed

    @staticmethod
    async def verify_path(path: str) -> bool:
        """Verify if path is within allowed project directory.
        
        Args:
            path: Path to verify
            
        Returns:
            bool: True if path is allowed, False otherwise
        """
        try:
            # Normalize paths using os.path.normpath to handle different separators
            canonical_path = os.path.normpath(os.path.abspath(path))
            project_dir = os.path.normpath(os.path.abspath(config.PROJECT_DIR))
            
            # On Windows, make comparison case-insensitive
            if os.name == 'nt':
                canonical_path = canonical_path.lower()
                project_dir = project_dir.lower()
            
            # Check if canonical_path starts with project_dir
            is_allowed = canonical_path.startswith(project_dir)
            
            # If project_dir is H:/projects or H:\\projects, allow all paths under it
            if project_dir.replace('\\', '/').lower() == 'h:/projects':
                is_allowed = canonical_path.lower().startswith('h:')
            
            if not is_allowed:
                logger.warning(f"Path {path} not in allowed directory {project_dir}")
            return is_allowed
            
        except Exception as e:
            logger.error(f"Path verification error: {e}")
            return False