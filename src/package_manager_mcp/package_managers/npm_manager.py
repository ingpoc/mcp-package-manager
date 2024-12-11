"""NPM Package Manager implementation."""

import os
import sys
import logging
from typing import List, Tuple
from .. import config

logger = logging.getLogger(__name__)

class NPMPackageManager:
    @staticmethod
    async def install(package: str, path: str, run_subprocess) -> Tuple[str, bool, str]:
        """Install a package using npm."""
        try:
            # NPM installation logic
            if sys.platform == 'win32':
                base_cmd = ['cmd', '/c']
                npm_cmd = ['npm']
            else:
                base_cmd = []
                npm_cmd = [config.NPM_PATH]

            if not os.path.exists(os.path.join(path, 'package.json')):
                logger.info("No package.json found, initializing...")
                init_cmd = base_cmd + npm_cmd + ['init', '-y']
                stdout, stderr, returncode = await run_subprocess(init_cmd, path, config.INIT_TIMEOUT)
                if returncode != 0:
                    return f"Failed to initialize package.json: {stderr}", False, stderr

            install_cmd = base_cmd + npm_cmd + ['install', package]
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
            logger.error(f"NPM installation error: {e}")
            return f"NPM installation error: {str(e)}", False, str(e)

    @staticmethod
    async def uninstall(package: str, path: str, run_subprocess) -> Tuple[str, bool, str]:
        """Uninstall a package using npm."""
        try:
            if sys.platform == 'win32':
                cmd = ['cmd', '/c', 'npm', 'uninstall', package]
            else:
                cmd = [config.NPM_PATH, 'uninstall', package]

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
            logger.error(f"NPM uninstallation error: {e}")
            return f"NPM uninstallation error: {str(e)}", False, str(e)

    @staticmethod
    async def init(path: str, run_subprocess) -> Tuple[str, bool, str]:
        """Initialize a new npm project."""
        try:
            if sys.platform == 'win32':
                cmd = ['cmd', '/c', 'npm', 'init', '-y']
            else:
                cmd = [config.NPM_PATH, 'init', '-y']

            stdout, stderr, returncode = await run_subprocess(
                cmd,
                path,
                config.INIT_TIMEOUT
            )

            if returncode == 0:
                return f"Successfully initialized npm project\n{stdout}", True, stdout
            else:
                return f"Initialization failed:\n{stderr}", False, stderr

        except Exception as e:
            logger.error(f"NPM initialization error: {e}")
            return f"NPM initialization error: {str(e)}", False, str(e)