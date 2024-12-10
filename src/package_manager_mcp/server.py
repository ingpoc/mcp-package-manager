"""
Main MCP server implementation for Package Manager.
"""

from contextlib import asynccontextmanager
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, Resource
from typing import Dict, Any, List, Optional
import asyncio
import json
import os
import logging
import subprocess
import sys
from . import config

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('package_manager.log')
    ]
)
logger = logging.getLogger(__name__)

def create_text_response(message: str) -> List[TextContent]:
    """Create a TextContent response."""
    try:
        return [TextContent(text=message)]
    except Exception as e1:
        try:
            return [TextContent(**{"text": message, "type": "text"})]
        except Exception as e2:
            logger.error(f"Error creating TextContent: {e1}, {e2}")
            return [TextContent(text=message, type="text")]

class PackageManagerMCPServer:
    def __init__(self):
        self.mcp_server = Server(name="package-manager-mcp-server")
        self._setup_mcp_handlers()

    def _setup_mcp_handlers(self):
        """Set up MCP server handlers."""
        @self.mcp_server.list_tools()
        async def list_tools() -> List[Tool]:
            return await self.list_tools()

        @self.mcp_server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            return await self.call_tool(name, arguments)

    async def list_tools(self) -> List[Tool]:
        """List available package management tools."""
        return [
            Tool(
                name="install",
                display_name="Install Package",
                description="Install npm or pip package",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "package": {
                            "type": "string",
                            "description": "Package name and version"
                        },
                        "manager": {
                            "type": "string",
                            "enum": ["npm", "pip"],
                            "description": "Package manager to use"
                        },
                        "path": {
                            "type": "string",
                            "description": "Installation path"
                        }
                    },
                    "required": ["package", "manager", "path"]
                }
            ),
            Tool(
                name="uninstall",
                display_name="Uninstall Package",
                description="Uninstall npm or pip package",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "package": {
                            "type": "string",
                            "description": "Package name"
                        },
                        "manager": {
                            "type": "string",
                            "enum": ["npm", "pip"],
                            "description": "Package manager to use"
                        },
                        "path": {
                            "type": "string",
                            "description": "Project path"
                        }
                    },
                    "required": ["package", "manager", "path"]
                }
            ),
            Tool(
                name="init",
                display_name="Initialize Project",
                description="Initialize package.json or requirements.txt",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "manager": {
                            "type": "string",
                            "enum": ["npm", "pip"],
                            "description": "Package manager to use"
                        },
                        "path": {
                            "type": "string",
                            "description": "Project path"
                        }
                    },
                    "required": ["manager", "path"]
                }
            )
        ]
        
    async def _run_subprocess(self, cmd: List[str], cwd: str, timeout: int) -> tuple[str, str, int]:
        """Run a subprocess with timeout."""
        try:
            # Log the exact command being executed
            logger.debug(f"Executing command: {' '.join(cmd)} in directory: {cwd}")
            
            # For Windows, always use shell=True when running npm
            use_shell = sys.platform == 'win32' and 'npm' in ' '.join(cmd)
            
            if use_shell:
                # For Windows, combine command into a single string
                cmd_str = ' '.join(cmd)
                logger.debug(f"Using shell command: {cmd_str}")
                process = await asyncio.create_subprocess_shell(
                    cmd_str,
                    cwd=cwd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    shell=True
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=cwd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout/1000
            )

            stdout_str = stdout.decode() if stdout else ""
            stderr_str = stderr.decode() if stderr else ""
            
            logger.debug(f"Command output - stdout: {stdout_str}, stderr: {stderr_str}, returncode: {process.returncode}")
            
            return stdout_str, stderr_str, process.returncode
            
        except asyncio.TimeoutError:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            raise
        except Exception as e:
            logger.error(f"Subprocess error: {e}")
            raise

    def _which(self, program: str) -> Optional[str]:
        """Find executable on PATH."""
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
                # Check for Windows executable extensions
                if sys.platform == 'win32':
                    for ext in ['.cmd', '.exe', '.bat']:
                        exe_file_ext = exe_file + ext
                        if is_exe(exe_file_ext):
                            return exe_file_ext
        return None

    async def _verify_package(self, package: str) -> bool:
        """Verify if package is in whitelist."""
        return any(allowed in package for allowed in config.ALLOWED_PACKAGES)

    async def _verify_path(self, path: str) -> bool:
        """Verify if path is within allowed project directory."""
        try:
            canonical_path = os.path.realpath(path)
            project_dir = os.path.realpath(config.PROJECT_DIR)
            return canonical_path.startswith(project_dir)
        except Exception as e:
            logger.error(f"Path verification error: {e}")
            return False

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute package management tools."""
        try:
            if name == "install":
                return await self._install_package(arguments)
            elif name == "uninstall":
                return await self._uninstall_package(arguments)
            elif name == "init":
                return await self._init_project(arguments)
            else:
                return create_text_response(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Tool error: {e}")
            return create_text_response(f"Error: {str(e)}")

    async def _install_package(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Install a package using npm or pip."""
        package = arguments["package"]
        manager = arguments["manager"]
        path = arguments["path"]

        logger.info(f"Installing package {package} with {manager} in {path}")

        # Security checks
        if not await self._verify_package(package):
            return create_text_response(f"Package {package} not in whitelist")

        if not await self._verify_path(path):
            return create_text_response(f"Path {path} not in allowed directory")

        try:
            # Create directory if it doesn't exist
            os.makedirs(path, exist_ok=True)

            if manager == "npm":
                # For Windows, use cmd /c to handle npm commands
                if sys.platform == 'win32':
                    base_cmd = ['cmd', '/c']
                    npm_cmd = ['npm']
                else:
                    base_cmd = []
                    npm_cmd = [config.NPM_PATH]

                # Check if package.json exists
                if not os.path.exists(os.path.join(path, 'package.json')):
                    logger.info("No package.json found, initializing...")
                    init_cmd = base_cmd + npm_cmd + ['init', '-y']
                    stdout, stderr, returncode = await self._run_subprocess(init_cmd, path, config.INIT_TIMEOUT)
                    if returncode != 0:
                        logger.error(f"Failed to initialize package.json: {stderr}")
                        return create_text_response(f"Failed to initialize package.json: {stderr}")

                # Run npm install
                install_cmd = base_cmd + npm_cmd + ['install', package]
                logger.info(f"Running npm install with command: {install_cmd}")
            else:
                # For pip installation
                install_cmd = [config.PIP_PATH, 'install', package]

            stdout, stderr, returncode = await self._run_subprocess(
                install_cmd,
                path,
                config.INSTALL_TIMEOUT
            )

            if returncode == 0:
                logger.info(f"Successfully installed {package}")
                return create_text_response(f"Successfully installed {package}\n{stdout}")
            else:
                logger.error(f"Installation failed: {stderr}")
                return create_text_response(f"Installation failed:\n{stderr}")

        except asyncio.TimeoutError:
            logger.error(f"Installation timeout for {package}")
            return create_text_response(f"Installation timeout for {package}")
        except Exception as e:
            logger.error(f"Installation error: {e}", exc_info=True)
            return create_text_response(f"Installation error: {str(e)}")

    async def _uninstall_package(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Uninstall a package using npm or pip."""
        package = arguments["package"]
        manager = arguments["manager"]
        path = arguments["path"]

        if not await self._verify_path(path):
            return create_text_response(f"Path {path} not in allowed directory")

        try:
            if manager == "npm":
                if sys.platform == 'win32':
                    cmd = ['cmd', '/c', 'npm', 'uninstall', package]
                else:
                    cmd = [config.NPM_PATH, 'uninstall', package]
            else:
                cmd = [config.PIP_PATH, 'uninstall', '-y', package]

            stdout, stderr, returncode = await self._run_subprocess(
                cmd,
                path,
                config.UNINSTALL_TIMEOUT
            )

            if returncode == 0:
                return create_text_response(f"Successfully uninstalled {package}\n{stdout}")
            else:
                return create_text_response(f"Uninstallation failed:\n{stderr}")

        except asyncio.TimeoutError:
            return create_text_response(f"Uninstallation timeout for {package}")
        except Exception as e:
            return create_text_response(f"Uninstallation error: {str(e)}")

    async def _init_project(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Initialize a new project with package.json or requirements.txt."""
        manager = arguments["manager"]
        path = arguments["path"]

        if not await self._verify_path(path):
            return create_text_response(f"Path {path} not in allowed directory")

        try:
            os.makedirs(path, exist_ok=True)
            
            if manager == "npm":
                if sys.platform == 'win32':
                    cmd = ['cmd', '/c', 'npm', 'init', '-y']
                else:
                    cmd = [config.NPM_PATH, 'init', '-y']
                    
                stdout, stderr, returncode = await self._run_subprocess(
                    cmd,
                    path,
                    config.INIT_TIMEOUT
                )

                if returncode == 0:
                    return create_text_response(f"Successfully initialized npm project\n{stdout}")
                else:
                    return create_text_response(f"Initialization failed:\n{stderr}")
            else:
                # For pip, create a requirements.txt file
                req_file = os.path.join(path, "requirements.txt")
                try:
                    with open(req_file, 'w') as f:
                        f.write("# Python package requirements\n")
                    return create_text_response(f"Created requirements.txt at {req_file}")
                except Exception as e:
                    return create_text_response(f"Failed to create requirements.txt: {str(e)}")

        except asyncio.TimeoutError:
            return create_text_response("Project initialization timeout")
        except Exception as e:
            return create_text_response(f"Project initialization error: {str(e)}")

    async def run(self):
        """Run the MCP server using stdio transport."""
        logger.info("Starting Package Manager MCP server...")
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server stdio transport initialized")
                init_options = InitializationOptions(
                    server_name="package-manager-mcp-server",
                    server_version="0.1.0",
                    capabilities=self.mcp_server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
                await self.mcp_server.run(read_stream, write_stream, init_options)
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise

async def main():
    """Main entry point for the server."""
    server = PackageManagerMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())