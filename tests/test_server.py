"""
Tests for the Package Manager MCP Server.
"""

import pytest
import os
import asyncio
from package_manager_mcp.server import PackageManagerMCPServer
from package_manager_mcp import config

@pytest.fixture
async def server():
    """Create a test server instance."""
    server = PackageManagerMCPServer()
    yield server

@pytest.mark.asyncio
async def test_list_tools(server):
    """Test tool listing."""
    tools = await server.list_tools()
    assert len(tools) == 3
    tool_names = {tool.name for tool in tools}
    assert tool_names == {"install", "uninstall", "init"}

@pytest.mark.asyncio
async def test_verify_package(server):
    """Test package verification."""
    # Test allowed package
    assert await server._verify_package("react") is True
    # Test disallowed package
    assert await server._verify_package("malicious-package") is False

@pytest.mark.asyncio
async def test_verify_path(server):
    """Test path verification."""
    # Test path within project directory
    test_path = os.path.join(config.PROJECT_DIR, "test")
    assert await server._verify_path(test_path) is True
    # Test path outside project directory
    assert await server._verify_path("/tmp/malicious") is False

@pytest.mark.asyncio
async def test_install_package(server):
    """Test package installation."""
    # Test with valid package
    result = await server._install_package({
        "package": "react",
        "manager": "npm",
        "path": os.path.join(config.PROJECT_DIR, "test")
    })
    assert isinstance(result, list)
    assert all(hasattr(item, 'text') for item in result)

@pytest.mark.asyncio
async def test_uninstall_package(server):
    """Test package uninstallation."""
    result = await server._uninstall_package({
        "package": "react",
        "manager": "npm",
        "path": os.path.join(config.PROJECT_DIR, "test")
    })
    assert isinstance(result, list)
    assert all(hasattr(item, 'text') for item in result)

@pytest.mark.asyncio
async def test_init_project(server):
    """Test project initialization."""
    # Test npm init
    npm_result = await server._init_project({
        "manager": "npm",
        "path": os.path.join(config.PROJECT_DIR, "test")
    })
    assert isinstance(npm_result, list)
    assert all(hasattr(item, 'text') for item in npm_result)

    # Test pip init
    pip_result = await server._init_project({
        "manager": "pip",
        "path": os.path.join(config.PROJECT_DIR, "test")
    })
    assert isinstance(pip_result, list)
    assert all(hasattr(item, 'text') for item in pip_result)

@pytest.mark.asyncio
async def test_run_subprocess(server):
    """Test subprocess execution."""
    cmd = ["echo", "test"]
    stdout, stderr, returncode = await server._run_subprocess(
        cmd,
        config.PROJECT_DIR,
        1000
    )
    assert returncode == 0
    assert stdout.strip() == "test"
    assert not stderr

@pytest.mark.asyncio
async def test_subprocess_timeout(server):
    """Test subprocess timeout handling."""
    cmd = ["sleep", "10"]
    with pytest.raises(asyncio.TimeoutError):
        await server._run_subprocess(cmd, config.PROJECT_DIR, 100)
