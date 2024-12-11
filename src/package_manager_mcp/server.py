"""
Main MCP server implementation for Package Manager.
"""

import asyncio
import logging
import sys
from typing import Dict, Any, List

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from . import config
from .tools.definitions import get_tool_definitions
from .tools.handlers import ToolHandlers

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

class PackageManagerMCPServer:
    """MCP server implementation for package management."""
    
    def __init__(self):
        """Initialize the server with tools and handlers."""
        self.mcp_server = Server(name="package-manager-mcp-server")
        self.tool_handlers = ToolHandlers()
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
        return get_tool_definitions()

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute package management tools."""
        try:
            return await self.tool_handlers.handle_tool(name, arguments)
        except Exception as e:
            logger.error(f"Tool error: {e}")
            return [TextContent(text=f"Error: {str(e)}")]

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