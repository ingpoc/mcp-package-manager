"""Subprocess utility functions for package management."""

import asyncio
import sys
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

async def run_subprocess(cmd: List[str], cwd: str, timeout: int) -> Tuple[str, str, int]:
    """Run a subprocess with timeout.
    
    Args:
        cmd: Command list to execute
        cwd: Working directory
        timeout: Timeout in milliseconds
        
    Returns:
        Tuple of (stdout, stderr, return_code)
    """
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
        if 'process' in locals():
            process.terminate()
            await process.wait()
        raise
    except Exception as e:
        logger.error(f"Subprocess error: {e}")
        if 'process' in locals():
            process.terminate()
            await process.wait()
        raise