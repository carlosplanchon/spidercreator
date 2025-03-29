#!/usr/bin/env python3

import os
import tempfile
import threading
import shutil
import http.server
import socketserver


class ServerThread(threading.Thread):
    """
    Runs a simple http.server in a separate thread, serving files
    from the given `directory` on `port`.
    """
    def __init__(self, port, directory):
        super().__init__()
        self.port = port
        self.directory = directory
        self.httpd = None

    def run(self):
        # Our simple handler
        handler = http.server.SimpleHTTPRequestHandler
        # Create the server
        with socketserver.TCPServer(
                ("127.0.0.1", self.port), handler) as httpd:
            # We'll store httpd so we can shut it down later
            self.httpd = httpd

            # Make sure we serve files from `directory`
            os.chdir(self.directory)

            # If port=0, the OS picks a free port.  If not, it uses the given port.
            actual_port = httpd.server_address[1]
            print(f"[ServerThread] Serving on port {actual_port} from directory: {self.directory}")

            # Serve forever, or until .shutdown() is called
            httpd.serve_forever()

    def stop(self):
        # Gracefully stop the server if it's running
        if self.httpd:
            self.httpd.shutdown()
            print(f"[ServerThread] Shutting down server on port {self.port}")


class HttpServerContext:
    """
    Context manager that starts a local HTTP server (in-process)
    on `port`, serving an `index.html` file containing `html`.
    Cleans up (stops server, removes temp dir) when done.
    """

    def __init__(self, port: int, html: str):
        self.port = port
        self.html = html
        self._tmpdir = None
        self._server_thread = None

    def __enter__(self):
        # 1) Create temp directory, write index.html
        self._tmpdir = tempfile.mkdtemp(prefix="html_server_")
        index_path = os.path.join(self._tmpdir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(self.html)

        # 2) Create and start the server thread
        self._server_thread = ServerThread(
            port=self.port,
            directory=self._tmpdir
        )
        self._server_thread.start()

        return self  # So the user can reference this context object if needed

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 3) Stop the server thread gracefully
        if self._server_thread:
            self._server_thread.stop()  # calls httpd.shutdown()
            self._server_thread.join(timeout=5)

        # 4) Remove the temporary directory
        if self._tmpdir and os.path.isdir(self._tmpdir):
            shutil.rmtree(self._tmpdir, ignore_errors=True)
