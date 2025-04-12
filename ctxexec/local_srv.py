#!/usr/bin/env python3

import os
import tempfile
import shutil
import trio
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from hypercorn.config import Config
from hypercorn.trio import serve

logger = structlog.get_logger()


class FastAPIServerContext:
    """
    Context manager that starts a local
    FastAPI server (using Hypercorn with Trio)
    on `port`, serving an `index.html` file containing `html`.
    Cleans up (stops server, removes temp dir) when done.
    """

    def __init__(self, port: int, html: str):
        self.port = port
        self.html = html
        self._tmpdir = None
        self._nursery = None
        self._task_status = None
        self._app = None

    async def start_server(self, task_status=trio.TASK_STATUS_IGNORED):
        """Start the FastAPI server using Hypercorn with Trio."""
        self._app = FastAPI()

        @self._app.get("/", response_class=HTMLResponse)
        async def serve_html(request: Request):
            return self.html

        config = Config()
        config.bind = [f"127.0.0.1:{self.port}"]

        # Use task_status to mark the server as started
        # after it's bound to the socket but before it starts serving
        async with trio.open_nursery() as nursery:
            await nursery.start(
                serve,
                self._app,
                config,
                # task_status=task_status
                task_status
            )

    async def __aenter__(self):
        # 1) Create temp directory, write index.html if needed
        self._tmpdir = tempfile.mkdtemp(prefix="html_server_")
        index_path = os.path.join(self._tmpdir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(self.html)

        # 2) Create nursery for server task
        self._nursery = trio.open_nursery()
        nursery = await self._nursery.__aenter__()

        # 3) Start server and wait until it's ready
        await nursery.start(self.start_server)

        logger.info("Started FastAPI server", port=self.port)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 1) Close the nursery, which cancels all tasks
        if self._nursery:
            logger.info("Shutting down FastAPI server", port=self.port)
            await self._nursery.__aexit__(exc_type, exc_val, exc_tb)

        # 2) Remove the temporary directory
        if self._tmpdir and os.path.isdir(self._tmpdir):
            shutil.rmtree(self._tmpdir, ignore_errors=True)
            logger.debug("Removed temporary directory", path=self._tmpdir)
