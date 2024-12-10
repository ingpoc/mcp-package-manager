# Package Manager MCP Server

A Model Context Protocol (MCP) server implementation for package management in Claude Desktop. This server handles npm and pip package installations, uninstallations, and project initializations.

## Features

- Package installation (npm/pip)
- Package uninstallation
- Project initialization
- Security checks and whitelisting
- Path verification
- Timeout handling

## Installation

```bash
# Using pip
pip install package-manager-mcp

# Using uv (recommended)
uv pip install package-manager-mcp
```

## Configuration

Environment variables:

```bash
# Common
LOG_LEVEL=debug
NODE_ENV=development

# Package Management
ALLOWED_PACKAGES=typescript,react,express...
MAX_INSTALL_SIZE=50000000
PROJECT_DIR=H:/projects
INSTALL_TIMEOUT=300000
UNINSTALL_TIMEOUT=60000
INIT_TIMEOUT=30000

# Package Managers
NPM_PATH=npm
PIP_PATH=pip
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
        "ALLOWED_PACKAGES": "typescript,react,express...",
        "MAX_INSTALL_SIZE": "50000000",
        "PROJECT_DIR": "H:/projects",
        "LOG_LEVEL": "debug",
        "NODE_ENV": "development"
      }
    }
  }
}
```

### Available Tools

1. install
   - Install npm or pip packages
   - Respects security whitelist
   - Handles timeouts

2. uninstall
   - Remove installed packages
   - Supports both npm and pip

3. init
   - Initialize new projects
   - Create package.json or requirements.txt

## Development

### Setup

```bash
# Clone repository
git clone <repository-url>

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e .
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=package_manager_mcp
```

## Security

- Package whitelist enforcement
- Path traversal protection
- Timeout limits
- Resource restrictions

## License

MIT License
