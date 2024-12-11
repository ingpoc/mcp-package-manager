"""Tool definitions for package management."""

from typing import List
from mcp.types import Tool

def get_tool_definitions() -> List[Tool]:
    """Get list of available package management tools.
    
    Returns:
        List[Tool]: List of tool definitions
    """
    return [
        Tool(
            name="install",
            display_name="Install Package",
            description="Install npm or Python package. For Python, use '-r requirements.txt' to install from file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Package name and version, or '-r requirements.txt' for Python requirements"
                    },
                    "manager": {
                        "type": "string",
                        "enum": ["npm", "uv"],
                        "description": "Package manager to use (npm for Node.js, uv for Python)"
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
            description="Uninstall npm or Python package",
            inputSchema={
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Package name"
                    },
                    "manager": {
                        "type": "string",
                        "enum": ["npm", "uv"],
                        "description": "Package manager to use (npm for Node.js, uv for Python)"
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
            description="Initialize package.json or pyproject.toml",
            inputSchema={
                "type": "object",
                "properties": {
                    "manager": {
                        "type": "string",
                        "enum": ["npm", "uv"],
                        "description": "Package manager to use (npm for Node.js, uv for Python)"
                    },
                    "path": {
                        "type": "string",
                        "description": "Project path"
                    }
                },
                "required": ["manager", "path"]
            }
        ),
        Tool(
            name="create_venv",
            display_name="Create Virtual Environment",
            description="Create a Python virtual environment using UV",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Project path"
                    },
                    "venv_name": {
                        "type": "string",
                        "description": "Name of virtual environment",
                        "default": ".venv"
                    }
                },
                "required": ["path"]
            }
        )
    ]