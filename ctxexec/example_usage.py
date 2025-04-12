#!/usr/bin/env python3

"""
Example usage of the refactored SpiderCreator context execution module.
This shows how to use the new Trio-based, ptyprocess-free implementation 
with FastAPI servers and structured logging.
"""

import trio
import structlog

# Import the refactored context execution module
from ctxexec import run_pipeline

logger = structlog.get_logger()

# Sample spider code example
SAMPLE_SPIDER_CODE = """
import requests
from parsel import Selector

def spider():
    url = "https://example.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    selector = Selector(text=response.text)

    title = selector.css('h1::text').get()
    description = selector.css('p::text').get()

    print(f"Title: {title}")
    print(f"Description: {description}")

if __name__ == "__main__":
    spider()
"""


# Mock candidate spider creation results
class MockSpiderCreationResult:
    def __init__(self, spider_code, explanation):
        self.spider_code = spider_code
        self.explanation = explanation


# Sample recordings data
SAMPLE_RECORDINGS_DATA = [
    {
        "url": "https://example.com",
        "website_html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Example Domain</title>
        </head>
        <body>
            <h1>Example Domain</h1>
            <p>This domain is for use in illustrative examples in documents.</p>
        </body>
        </html>
        """
    }
]


async def main():
    # Create mock candidate spider creation results
    CAND_SPIDER_CREATION_RESULTS = {
        1: MockSpiderCreationResult(
            spider_code=SAMPLE_SPIDER_CODE,
            explanation="This spider extracts the title and description from example.com"
        )
    }

    logger.info("Starting example pipeline execution")

    # Run the pipeline with our mock data
    results = await run_pipeline(
        CAND_SPIDER_CREATION_RESULTS=CAND_SPIDER_CREATION_RESULTS,
        recordings_data=SAMPLE_RECORDINGS_DATA,
        max_exec_instances=1
    )

    # Display results
    for key, executor in results.items():
        logger.info(
            "Spider execution result",
            key=key,
            output=executor.spider_code_output_with_local_addresses
        )

    logger.info("Example completed successfully")


if __name__ == "__main__":
    # Run the main function with Trio
    trio.run(main)
