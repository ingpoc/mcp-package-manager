"""Tool handlers for package management."""

import os
import logging
import asyncio
from typing import Dict, Any, List

from mcp.types import TextContent

from ..utils.security import SecurityValidator
from ..utils.responses import create_text_response
from ..utils.subprocess import run_subprocess
from ..package_managers import NPMPackageManager, UVPackageManager

logger = logging.getLogger(__name__)

class ToolHandlers:
    """Handlers for package management tools."""
    
    def __init__(self):
        self.npm_manager = NPMPackageManager()
        self.uv_manager = UVPackageManager()

    async def handle_install(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle package installation."""
        package = arguments["package"]
        manager = arguments["manager"]
        path = arguments["path"]

        logger.info(f"Installing package {package} with {manager} in {path}")

        # Security checks
        if not await SecurityValidator.verify_package(package, path):
            return create_text_response(f"Package {package} not in whitelist")

        if not await SecurityValidator.verify_path(path):
            return create_text_response(f"Path {path} not in allowed directory")

        try:
            # Create directory if it doesn't exist
            os.makedirs(path, exist_ok=True)

            if manager == "npm":
                message, success, _ = await self.npm_manager.install(package, path, run_subprocess)
            else:
                message, success, _ = await self.uv_manager.install(package, path, run_subprocess)

            return create_text_response(message)

        except asyncio.TimeoutError:
            logger.error(f"Installation timeout for {package}")
            return create_text_response(f"Installation timeout for {package}")
        except Exception as e:
            logger.error(f"Installation error: {e}", exc_info=True)
            return create_text_response(f"Installation error: {str(e)}")

    async def handle_uninstall(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle package uninstallation."""
        package = arguments["package"]
        manager = arguments["manager"]
        path = arguments["path"]

        if not await SecurityValidator.verify_path(path):
            return create_text_response(f"Path {path} not in allowed directory")

        try:
            if manager == "npm":
                message, success, _ = await self.npm_manager.uninstall(package, path, run_subprocess)
            else:
                message, success, _ = await self.uv_manager.uninstall(package, path, run_subprocess)

            return create_text_response(message)

        except asyncio.TimeoutError:
            return create_text_response(f"Uninstallation timeout for {package}")
        except Exception as e:
            return create_text_response(f"Uninstallation error: {str(e)}")

    async def handle_init(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle project initialization."""
        manager = arguments["manager"]
        path = arguments["path"]

        if not await SecurityValidator.verify_path(path):
            return create_text_response(f"Path {path} not in allowed directory")

        try:
            os.makedirs(path, exist_ok=True)
            
            if manager == "npm":
                message, success, _ = await self.npm_manager.init(path, run_subprocess)
            else:
                message, success, _ = await self.uv_manager.init(path, run_subprocess)

            return create_text_response(message)

        except asyncio.TimeoutError:
            return create_text_response("Project initialization timeout")
        except Exception as e:
            return create_text_response(f"Project initialization error: {str(e)}")

    async def handle_create_venv(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle virtual environment creation."""
        path = arguments["path"]
        venv_name = arguments.get("venv_name", ".venv")

        if not await SecurityValidator.verify_path(path):
            return create_text_response(f"Path {path} not in allowed directory")

        try:
            os.makedirs(path, exist_ok=True)
            message, success, _ = await self.uv_manager.create_venv(path, venv_name, run_subprocess)
            return create_text_response(message)

        except asyncio.TimeoutError:
            return create_text_response("Virtual environment creation timeout")
        except Exception as e:
            return create_text_response(f"Virtual environment creation error: {str(e)}")

    async def handle_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Route tool calls to appropriate handlers."""
        handlers = {
            "install": self.handle_install,
            "uninstall": self.handle_uninstall,
            "init": self.handle_init,
            "create_venv": self.handle_create_venv
        }
        
        handler = handlers.get(name)
        if handler:
            return await handler(arguments)
        else:
            return create_text_response(f"Unknown tool: {name}")