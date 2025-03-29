#!/usr/bin/env python3

import re

import base64


def extract_first_python_code(markdown_text: str) -> str:
    """
    Extracts and returns the first Python code block enclosed in triple backticks 
    from a Markdown string. If no code block is found, returns an empty string.

    :param markdown_text: The entire Markdown text as a string.
    :return: The first Python code block (without the backticks), or an empty string if none found.
    """
    if isinstance(markdown_text, str) is False:
        return ""

    pattern = r"```python\s+([\s\S]*?)```"
    match = re.search(pattern, markdown_text)
    if match:
        return match.group(1).strip()
    return ""


def b64_to_png(b64_string, output_file):
    """
    Convert a Base64-encoded string to a PNG file.

    :param b64_string: A string containing Base64-encoded data
    :param output_file: The path to the output PNG file
    """
    with open(output_file, "wb") as f:
        f.write(base64.b64decode(b64_string))
