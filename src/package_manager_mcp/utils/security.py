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
            canonical_path = os.path.realpath(path)
            project_dir = os.path.realpath(config.PROJECT_DIR)
            is_allowed = canonical_path.startswith(project_dir)
            if not is_allowed:
                logger.warning(f"Path {path} not in allowed directory {project_dir}")
            return is_allowed
        except Exception as e:
            logger.error(f"Path verification error: {e}")
            return False