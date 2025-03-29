#!/usr/bin/env python3

import os
import tempfile
from ptyprocess import PtyProcessUnicode


def execute_spider_with_ptyprocess(spider_code: str):
    """
    Run the given Python code in a pseudoterminal (PTY) via ptyprocess
    and return everything printed to stdout.
    """

    # 1) Write the spider code to a temporary file
    with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".py") as tmp_file:
        tmp_file_name = tmp_file.name
        tmp_file.write(spider_code)

    try:
        # 2) Use ptyprocess to spawn "python" on the temporary file
        p = PtyProcessUnicode.spawn(["python", tmp_file_name])
        output = []

        # 3) Continuously read from the process until EOF
        while True:
            try:
                data = p.read()
                if not data:
                    break
                output.append(data)
            except EOFError:
                break

        # 4) Join all the output pieces and return
        return "".join(output)

    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_file_name):
            os.remove(tmp_file_name)
