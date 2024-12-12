"""UV Package Manager implementation."""

import os
import sys
import logging
from typing import List, Tuple
from .. import config

logger = logging.getLogger(__name__)

class UVPackageManager:
    @staticmethod
    async def verify_requirements_file(path: str) -> bool:
        """Verify all packages in requirements.txt are in whitelist."""
        try:
            req_file = os.path.join(path, "requirements.txt")
            if not os.path.exists(req_file):
                return False
                
            # If wildcard is in allowed packages, allow all
            if "*" in config.ALLOWED_PACKAGES:
                return True
                
            with open(req_file, 'r') as f:
                requirements = f.readlines()
                
            # Process each line to extract package names
            for line in requirements:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Extract package name (remove version specifiers)
                package_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                if not any(allowed in package_name for allowed in config.ALLOWED_PACKAGES):
                    logger.error(f"Package {package_name} from requirements.txt not in whitelist")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error verifying requirements.txt: {e}")
            return False

    @staticmethod
    async def add(args: List[str], path: str, run_subprocess) -> Tuple[str, bool, str]:
        """Add packages using UV add command."""
        try:
            # Check if we need to verify requirements.txt
            if "-r" in args and "requirements.txt" in args:
                if not await UVPackageManager.verify_requirements_file(path):
                    return "Some packages in requirements.txt are not in whitelist", False, ""

            # Create base command
            cmd = [config.UV_PATH, "add"] + args

            # Run the UV add command
            stdout, stderr, returncode = await run_subprocess(
                cmd,
                path,
                config.INSTALL_TIMEOUT
            )

            if returncode == 0:
                return f"Successfully added packages using 'uv add {' '.join(args)}'\n{stdout}", True, stdout
            else:
                return f"Package addition failed:\n{stderr}", False, stderr

        except Exception as e:
            logger.error(f"UV add error: {e}")
            return f"UV add error: {str(e)}", False, str(e)

    @staticmethod
    async def install(package: str, path: str, run_subprocess) -> Tuple[str, bool, str]:
        """Install a package using UV."""
        try:
            # UV installation
            if not os.path.exists(os.path.join(path, 'pyproject.toml')):
                logger.info("No pyproject.toml found, initializing...")
                init_cmd = [config.UV_PATH, 'init']
                stdout, stderr, returncode = await run_subprocess(init_cmd, path, config.INIT_TIMEOUT)
                if returncode != 0:
                    return f"Failed to initialize pyproject.toml: {stderr}", False, stderr

            # Handle requirements.txt case
            if package == "-r requirements.txt":
                if not await UVPackageManager.verify_requirements_file(path):
                    return "Some packages in requirements.txt are not in whitelist", False, ""
                install_cmd = [config.UV_PATH, 'add', "-r", "requirements.txt"]
            else:
                # Determine if we should use 'add' or 'pip install'
                use_add = not package.startswith('-') and ' ' not in package  # Single package without flags
                
                if use_add:
                    # For uv add, we need to validate the package name against whitelist
                    package_name = package.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    if "*" not in config.ALLOWED_PACKAGES and not any(allowed in package_name for allowed in config.ALLOWED_PACKAGES):
                        return f"Package {package_name} not in whitelist", False, ""
                    install_cmd = [config.UV_PATH, 'add', package]
                else:
                    # Fall back to pip install for complex cases
                    install_cmd = [config.UV_PATH, 'pip', 'install', package]

            stdout, stderr, returncode = await run_subprocess(
                install_cmd,
                path,
                config.INSTALL_TIMEOUT
            )

            if returncode == 0:
                return f"Successfully installed {package}\n{stdout}", True, stdout
            else:
                return f"Installation failed:\n{stderr}", False, stderr

        except Exception as e:
            logger.error(f"UV installation error: {e}")
            return f"UV installation error: {str(e)}", False, str(e)

    @staticmethod
    async def uninstall(package: str, path: str, run_subprocess) -> Tuple[str, bool, str]:
        """Uninstall a package using UV."""
        try:
            # Use uv remove for packages installed with uv add, fallback to pip uninstall
            if os.path.exists(os.path.join(path, 'pyproject.toml')):
                cmd = [config.UV_PATH, 'remove', package]
            else:
                cmd = [config.UV_PATH, 'pip', 'uninstall', '-y', package]

            stdout, stderr, returncode = await run_subprocess(
                cmd,
                path,
                config.UNINSTALL_TIMEOUT
            )

            if returncode == 0:
                return f"Successfully uninstalled {package}\n{stdout}", True, stdout
            else:
                return f"Uninstallation failed:\n{stderr}", False, stderr

        except Exception as e:
            logger.error(f"UV uninstallation error: {e}")
            return f"UV uninstallation error: {str(e)}", False, str(e)

    @staticmethod
    async def init(path: str, run_subprocess) -> Tuple[str, bool, str]:
        """Initialize a new UV project."""
        try:
            cmd = [config.UV_PATH, 'init']

            stdout, stderr, returncode = await run_subprocess(
                cmd,
                path,
                config.INIT_TIMEOUT
            )

            if returncode == 0:
                return f"Successfully initialized UV project\n{stdout}", True, stdout
            else:
                return f"Initialization failed:\n{stderr}", False, stderr

        except Exception as e:
            logger.error(f"UV initialization error: {e}")
            return f"UV initialization error: {str(e)}", False, str(e)

    @staticmethod
    async def create_venv(path: str, venv_name: str, run_subprocess) -> Tuple[str, bool, str]:
        """Create a new virtual environment using UV."""
        try:
            cmd = [config.UV_PATH, 'venv', venv_name]
            
            stdout, stderr, returncode = await run_subprocess(
                cmd,
                path,
                config.VENV_TIMEOUT
            )

            if returncode == 0:
                venv_path = os.path.join(path, venv_name)
                if os.path.exists(venv_path):
                    return f"Successfully created virtual environment at {venv_path}\n{stdout}", True, stdout
                else:
                    return f"Virtual environment creation seemed to succeed but {venv_path} not found", False, stdout
            else:
                return f"Virtual environment creation failed:\n{stderr}", False, stderr

        except Exception as e:
            logger.error(f"UV venv creation error: {e}")
            return f"UV venv creation error: {str(e)}", False, str(e)