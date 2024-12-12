"""Subprocess utility functions."""

import asyncio
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

async def run_subprocess(cmd: List[str], cwd: str, timeout: int = 30000) -> Tuple[str, str, int]:
    """Run a subprocess with timeout.
    
    Args:
        cmd: Command and arguments
        cwd: Working directory
        timeout: Timeout in milliseconds
        
    Returns:
        Tuple[str, str, int]: stdout, stderr, return code
    """
    try:
        # Convert milliseconds to seconds for asyncio
        timeout_seconds = timeout / 1000
        
        logger.debug(f"Running command: {cmd} in {cwd} with timeout {timeout_seconds}s")
        
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for completion with timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_seconds
            )
            return stdout.decode(), stderr.decode(), process.returncode
            
        except asyncio.TimeoutError:
            logger.error(f"Command timed out after {timeout_seconds}s: {cmd}")
            try:
                process.kill()
            except:
                pass
            raise
            
    except Exception as e:
        logger.error(f"Error running command {cmd}: {e}")
        return "", str(e), 1