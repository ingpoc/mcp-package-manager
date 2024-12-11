# Package Manager MCP Server

A Model Context Protocol (MCP) server implementation for package management in Claude Desktop. This server handles npm (for Node.js) and uv (for Python) package installations, uninstallations, project initializations, and virtual environment management.

## Features

- Node.js package management (using npm)
- Python package management (using uv)
  - Package installation and uninstallation
  - Requirements.txt support with whitelist validation
  - Virtual environment creation and management
  - Platform-specific path detection
- Project initialization (package.json/pyproject.toml)
- Security features:
  - Package whitelist validation
  - Path verification
  - Resource limits
  - Timeout handling
- Cross-platform support:
  - Windows path detection for npm and uv
  - Unix/Linux compatibility
- Comprehensive logging and error handling

## Requirements

- Python 3.12+
- Node.js (for npm operations)
- UV for Python package management

## Installation

```bash
# Create and activate a virtual environment (recommended)
uv venv .venv
source .venv/bin/activate  # Unix/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e .
```

## Configuration

Environment variables:

```bash
# Common Settings
LOG_LEVEL=DEBUG
NODE_ENV=development
PYTHON_ENV=development

# Package Management
ALLOWED_PACKAGES=typescript,react,express,requests,pandas...
MAX_INSTALL_SIZE=50000000
PROJECT_DIR=H:/projects

# Timeouts (in milliseconds)
INSTALL_TIMEOUT=300000
UNINSTALL_TIMEOUT=60000
INIT_TIMEOUT=30000
VENV_TIMEOUT=30000

# Package Managers Configuration
NPM_PATH=npm                  # Optional: Auto-detected
UV_PATH=uv                    # Optional: Auto-detected
USE_UV=true
VENV_NAME=.venv
```

## Usage

### Claude Desktop Configuration

Add to your claude_desktop_config.json:

```json
{
  "mcpServers": {
    "package-manager": {
      "command": "python",
      "args": ["-m", "package_manager_mcp.server"],
      "env": {
        "ALLOWED_PACKAGES": "typescript,react,express,requests,pandas...",
        "MAX_INSTALL_SIZE": "50000000",
        "PROJECT_DIR": "H:/projects",
        "LOG_LEVEL": "DEBUG",
        "NODE_ENV": "development",
        "USE_UV": "true",
        "UV_PATH": "uv",
        "VENV_NAME": ".venv",
        "PYTHON_VERSION": "3.12",
        "VENV_TIMEOUT": "30000"
      }
    }
  }
}
```

### Available Tools

1. install
   - Install npm (Node.js) or uv (Python) packages
   - Supports requirements.txt with whitelist validation
   - Handles versioning and dependencies
   - Respects security whitelist and timeouts

2. uninstall
   - Remove installed packages
   - Supports both npm and uv
   - Clean uninstallation with dependency handling

3. init
   - Initialize new projects
   - Creates package.json (npm) or pyproject.toml (uv)
   - Configures initial project structure

4. create_venv
   - Create Python virtual environments
   - Uses UV for reliable environment creation
   - Path verification and security checks
   - Configurable venv name and location

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/your-org/package-manager-mcp.git

# Create virtual environment
uv venv .venv
source .venv/bin/activate  # Unix/Linux
# or
.venv\Scripts\activate     # Windows

# Install development dependencies
uv pip install -r requirements-dev.txt
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=package_manager_mcp

# Run specific test modules
pytest tests/test_uv_manager.py
```

### Logging

The server provides comprehensive logging with:
- Console output
- File logging (package_manager.log)
- Configurable log levels
- Detailed error messages and stack traces

## Security

- Package whitelist enforcement
- Path traversal protection
- Virtual environment path verification
- Resource usage limits
- Operation timeouts
- Comprehensive input validation
- Secure subprocess management

## License

MIT License