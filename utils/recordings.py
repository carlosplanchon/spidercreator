#!/usr/bin/env python3

import json
import os


def load_recordings(directory: str):
    """Loads and parses all JSON files from the specified directory."""
    recordings = []

    for filename in sorted(
        os.listdir(directory),
        key=lambda x: int(x.split('.')[0])
            ):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    recordings.append(data)
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    return recordings
