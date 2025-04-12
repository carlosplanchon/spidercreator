#!/usr/bin/env python3

import attrs
from attrs_strict import type_validator
import structlog
from contextlib import AsyncExitStack

from pipeline.make_candsp_runnable import make_cand_spider_runnable
from pipeline.get_url_from_sp import get_urls_from_spider_code
from pipeline.sp_addr_remapping import rewrite_ports_in_spider

from ctxexec.local_srv import FastAPIServerContext
from ctxexec.exec_sp import execute_spider_with_trio_subprocess

from typing import Any

logger = structlog.get_logger()


async def map_url_to_exec_context(
    recordings_data,
    spider_urls: list[str],
    INITIAL_PORT: int = 8020,
    port_offset: int = 0
        ) -> tuple[dict[str, dict[str, Any]], int]:
    URL_TO_HTML: dict[str, dict[str, Any]] = {}

    seen_urls = []
    for url in spider_urls:
        for record in recordings_data:
            if record["url"] == url and url not in seen_urls:
                seen_urls.append(url)

                port: int = INITIAL_PORT + port_offset
                port_offset += 1

                URL_TO_HTML[url] = {
                    "html": record["website_html"],
                    "port": port
                }
                logger.debug("Mapped URL to HTML", url=url, port=port)

    return URL_TO_HTML, port_offset


def get_url_to_local_addresses(
    URL_TO_HTML: dict[str, dict[str, Any]]
        ) -> dict[str, str]:
    URL_TO_LOCAL_ADDRESSES = {}
    for url in URL_TO_HTML:
        URL_TO_LOCAL_ADDRESSES[url] =\
            f"http://127.0.0.1:{URL_TO_HTML[url]['port']}"
    return URL_TO_LOCAL_ADDRESSES


async def build_fastapi_server_contexts(
    URL_TO_HTML: dict[str, dict[str, Any]]
        ) -> list[FastAPIServerContext]:
    # Build a list of contexts:
    contexts = []
    for url, row in URL_TO_HTML.items():
        contexts.append(
            FastAPIServerContext(
                port=row["port"],
                html=row["html"]
            )
        )
    return contexts


async def execute_spider_with_fastapi_server_context(
    spider_code: str,
    server_contexts: list[FastAPIServerContext]
        ) -> str:
    # Use AsyncExitStack to manage server_contexts
    # in a single 'async with' block
    async with AsyncExitStack() as stack:
        for ctx in server_contexts:
            await stack.enter_async_context(ctx)

        logger.info("All FastAPI servers started, running spider")
        spider_code_output: str = await execute_spider_with_trio_subprocess(
            spider_code=spider_code
        )

        logger.info("Spider execution complete")
    # AsyncExitStack's __aexit__ will shut down all servers automatically
    return spider_code_output


@attrs.define()
class CandSpiderExecutor:
    spider_code: str = attrs.field(
        validator=type_validator()
    )

    recordings_data: Any = attrs.field(
        validator=type_validator()
    )

    spider_code_runnable: str = attrs.field(
        validator=type_validator(),
        init=False
    )

    runnable_spider_urls: list[str] = attrs.field(
        validator=type_validator(),
        init=False
    )

    URL_TO_HTML: dict[str, Any] = attrs.field(
        validator=type_validator(),
        init=False,
        repr=False
    )

    INITIAL_PORT: int = attrs.field(
        validator=type_validator(),
        default=8020
    )

    port_offset: int = attrs.field(
        validator=type_validator(),
        default=0
    )

    URL_TO_LOCAL_ADDRESSES: dict[str, str] = attrs.field(
        validator=type_validator(),
        init=False
    )

    spider_code_with_local_addresses: str = attrs.field(
        validator=type_validator(),
        init=False
    )

    server_contexts: list[FastAPIServerContext] = attrs.field(
        validator=type_validator(),
        init=False
    )

    spider_code_output_with_local_addresses: str = attrs.field(
        validator=type_validator(),
        init=False
    )

    async def start(self):
        """Run the entire spider execution process asynchronously with Trio"""
        logger.info("Starting spider execution process")

        # 1. Make candidate spider runnable
        self.spider_code_runnable: str = make_cand_spider_runnable(
            self.spider_code
        )
        logger.debug("Created runnable spider code")

        # 2. Extract URLs from the spider code
        self.runnable_spider_urls: list[str] = get_urls_from_spider_code(
            self.spider_code_runnable
        )
        logger.info(
            "Extracted URLs from spider code",
            urls=self.runnable_spider_urls
        )

        # 3. Map URLs to local execution contexts
        self.URL_TO_HTML, self.port_offset = await map_url_to_exec_context(
            recordings_data=self.recordings_data,
            spider_urls=self.runnable_spider_urls,
            INITIAL_PORT=self.INITIAL_PORT,
            port_offset=self.port_offset
        )

        # 4. Create mapping of original URLs to local server addresses
        self.URL_TO_LOCAL_ADDRESSES = get_url_to_local_addresses(
            URL_TO_HTML=self.URL_TO_HTML
        )
        logger.debug(
            "Created URL to local address mapping",
            mapping=self.URL_TO_LOCAL_ADDRESSES
        )

        # 5. Rewrite spider code to use local URLs instead of actual ones
        self.spider_code_with_local_addresses = rewrite_ports_in_spider(
            spider_code=self.spider_code_runnable,
            URL_TO_LOCAL_ADDRESSES=self.URL_TO_LOCAL_ADDRESSES
        )
        logger.debug("Rewrote spider code with local addresses")

        # 6. Create server contexts for each URL/HTML pair
        self.server_contexts = await build_fastapi_server_contexts(
            URL_TO_HTML=self.URL_TO_HTML
        )
        logger.debug(
            "Created FastAPI server contexts",
            count=len(self.server_contexts)
        )

        # 7. Run the spider with local FastAPI servers
        self.spider_code_output_with_local_addresses: str =\
            await execute_spider_with_fastapi_server_context(
                spider_code=self.spider_code_with_local_addresses,
                server_contexts=self.server_contexts
            )
        logger.info("Completed spider execution")
