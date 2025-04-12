#!/usr/bin/env python3

# Configure structlog early
import structlog
import logging

# Setup structlog
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    cache_logger_on_first_use=True,
)

# Export the main components for easy access
from ctxexec.pipeline import execute_cand_spiders, run_pipeline
from ctxexec.cand_sp_exec import CandSpiderExecutor
from ctxexec.local_srv import FastAPIServerContext
from ctxexec.exec_sp import execute_spider_with_trio_subprocess
