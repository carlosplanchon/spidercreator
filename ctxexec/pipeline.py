#!/usr/bin/env python3

import structlog
import trio
from typing import Dict, Any, Optional

from ctxexec.cand_sp_exec import CandSpiderExecutor

logger = structlog.get_logger()

async def execute_cand_spiders(
    CAND_SPIDER_CREATION_RESULTS,
    recordings_data,
    max_exec_instances: int = 20
        ) -> Dict[int, CandSpiderExecutor]:
    """
    Execute candidate spiders asynchronously using Trio.
    
    Args:
        CAND_SPIDER_CREATION_RESULTS: Dictionary of candidate spider creation results
        recordings_data: Data from browser recordings
        max_exec_instances: Maximum number of spider instances to execute
    
    Returns:
        Dictionary of CandSpiderExecutor instances with results
    """
    CAND_SPIDER_EXEC_RESULTS: Dict[int, CandSpiderExecutor] = {}
    port_offset: int = 0
    actual_exec_instance: int = 0
    
    # Process each candidate spider
    for key, chunk in CAND_SPIDER_CREATION_RESULTS.items():
        if chunk is not False:
            logger.info(f"Processing candidate spider", key=key, instance=actual_exec_instance)
            
            if chunk is not None and chunk.spider_code not in [None, ""]:
                logger.debug("Spider explanation", explanation=chunk.explanation)
                
                # Create and initialize the spider executor
                cand_spider_executor = CandSpiderExecutor(
                    spider_code=chunk.spider_code,
                    recordings_data=recordings_data,
                    port_offset=port_offset
                )
                
                # Run the spider using Trio
                await cand_spider_executor.start()
                
                # Update port offset for next execution
                port_offset = cand_spider_executor.port_offset
                
                # Store results
                CAND_SPIDER_EXEC_RESULTS[key] = cand_spider_executor
                
                # Increment instance counter
                actual_exec_instance += 1
                
                # Break if we've reached max instances
                if actual_exec_instance >= max_exec_instances:
                    logger.info("Reached maximum execution instances", max=max_exec_instances)
                    break
    
    return CAND_SPIDER_EXEC_RESULTS

# Main entry point for running the pipeline
async def run_pipeline(CAND_SPIDER_CREATION_RESULTS, recordings_data, max_exec_instances: int = 20):
    """Main entry point for running the entire pipeline with Trio"""
    results = await execute_cand_spiders(
        CAND_SPIDER_CREATION_RESULTS,
        recordings_data,
        max_exec_instances
    )
    return results