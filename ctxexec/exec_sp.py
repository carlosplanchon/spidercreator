#!/usr/bin/env python3

import os
import tempfile
import trio
import structlog
from typing import Optional

logger = structlog.get_logger()

async def execute_spider_with_trio_subprocess(spider_code: str) -> str:
    """
    Run the given Python code using trio.subprocess.run
    and return everything printed to stdout.
    """
    # 1) Write the spider code to a temporary file
    with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".py") as tmp_file:
        tmp_file_name = tmp_file.name
        tmp_file.write(spider_code)
    
    try:
        # 2) Use trio subprocess to run python on the temporary file
        logger.info("Executing spider code", file=tmp_file_name)
        
        process = await trio.run_process(
            ["python", tmp_file_name],
            capture_stdout=True,
            capture_stderr=True
        )
        
        # Process stdout and stderr
        stdout = process.stdout.decode('utf-8')
        stderr = process.stderr.decode('utf-8')
        
        if stderr:
            logger.warning("Spider execution produced errors", stderr=stderr)
            
        return stdout
    
    except Exception as e:
        logger.error("Error executing spider", error=str(e))
        return f"Error executing spider: {str(e)}"
        
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_file_name):
            os.remove(tmp_file_name)
            logger.debug("Removed temporary spider file", file=tmp_file_name)