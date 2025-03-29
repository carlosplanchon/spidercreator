#!/usr/bin/env python3

import attrs
from attrs_strict import type_validator

from pipeline.make_candsp_runnable import make_cand_spider_runnable
from pipeline.get_url_from_sp import get_urls_from_spider_code
from pipeline.sp_addr_remapping import rewrite_ports_in_spider

from ctxexec.local_srv import HttpServerContext

from contextlib import ExitStack

from ctxexec.exec_sp import execute_spider_with_ptyprocess

from typing import Any


def map_url_to_exec_context(
    recordings_data,
    spider_urls: list[str],
    INITIAL_PORT: int = 8020,
    port_offset: int = 0
        ):
    URL_TO_HTML: dict[str, str] = {}

    seen_urls = []
    for url in spider_urls:
        # print(f"URL: {url}")
        for record in recordings_data:
            if record["url"] == url and url not in seen_urls:
                seen_urls.append(url)

                port: int = INITIAL_PORT + port_offset
                port_offset += 1

                # print(record)
                URL_TO_HTML[url] = {
                    "html": record["website_html"],
                    "port": port
                }
    return URL_TO_HTML, port_offset


def get_url_to_local_addresses(URL_TO_HTML):
    URL_TO_LOCAL_ADDRESSES = {}
    for url in URL_TO_HTML:
        URL_TO_LOCAL_ADDRESSES[url] = f"http://127.0.0.1:{URL_TO_HTML[url]['port']}"
    return URL_TO_LOCAL_ADDRESSES


def build_http_server_contexts(URL_TO_HTML):
    # Build a list of contexts:
    contexts = []
    for url, row in URL_TO_HTML.items():
        contexts.append(
            HttpServerContext(
                port=row["port"],
                html=row["html"]
            )
        )
    return contexts


def execute_spider_with_http_server_context(
    spider_code: str,
    http_server_contexts: list[HttpServerContext]
        ) -> str:
    # Use ExitStack to manage http_server_contexts in a single 'with' block
    with ExitStack() as stack:
        for ctx in http_server_contexts:
            stack.enter_context(ctx)

        spider_code_output_with_local_addresses: str =\
            execute_spider_with_ptyprocess(
                spider_code=spider_code
            )

        print("Done. Exiting the 'with' block will shut down both servers automatically.")
    return spider_code_output_with_local_addresses


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

    http_server_contexts: list[HttpServerContext] = attrs.field(
        validator=type_validator(),
        init=False
    )

    spider_code_output_with_local_addresses: str = attrs.field(
        validator=type_validator(),
        init=False
    )

    def start(self):
        self.spider_code_runnable: str = make_cand_spider_runnable(
            self.spider_code
        )

        print("--- SPIDER CODE RUNNABLE ---")
        print(self.spider_code_runnable)

        self.runnable_spider_urls: list[str] = get_urls_from_spider_code(
            self.spider_code_runnable
        )

        print("--- RUNNABLE SPIDER URLS ---")
        print(self.runnable_spider_urls)

        self.URL_TO_HTML, self.port_offset = map_url_to_exec_context(
            recordings_data=self.recordings_data,
            spider_urls=self.runnable_spider_urls,
            INITIAL_PORT=self.INITIAL_PORT,
            port_offset=self.port_offset
        )

        self.URL_TO_LOCAL_ADDRESSES = get_url_to_local_addresses(
            URL_TO_HTML=self.URL_TO_HTML
        )

        print("--- URL TO LOCAL ADDRESSES ---")
        print(self.URL_TO_LOCAL_ADDRESSES)

        self.spider_code_with_local_addresses =\
            rewrite_ports_in_spider(
                spider_code=self.spider_code_runnable,
                URL_TO_LOCAL_ADDRESSES=self.URL_TO_LOCAL_ADDRESSES
            )

        print("--- SPIDER WITH LOCAL ADDRESSES ---")
        print(self.spider_code_with_local_addresses)

        self.http_server_contexts = build_http_server_contexts(
            URL_TO_HTML=self.URL_TO_HTML
        )

        print("--- HTTP SERVER CONTEXTS ---")
        print(self.http_server_contexts)

        self.spider_code_output_with_local_addresses: str =\
            execute_spider_with_http_server_context(
                spider_code=self.spider_code_with_local_addresses,
                http_server_contexts=self.http_server_contexts
            )

        print("--- SPIDER CODE OUTPUT WITH LOCAL ADDRESSES ---")
        print(self.spider_code_output_with_local_addresses)
