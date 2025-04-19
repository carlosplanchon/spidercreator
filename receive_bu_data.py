#!/usr/bin/env python3

import json
from pathlib import Path

from fastapi import FastAPI, Request
import prettyprinter

prettyprinter.install_extras()

app = FastAPI()


@app.post("/post_agent_history_step")
async def post_agent_history_step(request: Request):
    data = await request.json()

    print("-> Browser Use Recorder. Recording received!")
    # prettyprinter.cpprint(data)

    # Retrieve the folder name from app.state
    recordings_folder_name = app.state.folder_name
    print("RECORDINGS FOLDER NAME")
    print(recordings_folder_name)

    # Ensure the folder exists
    recordings_folder = Path(recordings_folder_name)
    recordings_folder.mkdir(parents=True, exist_ok=True)

    # Determine the next file number by examining existing .json files
    existing_numbers = []
    for item in recordings_folder.iterdir():
        if item.is_file() and item.suffix == ".json":
            try:
                file_num = int(item.stem)
                existing_numbers.append(file_num)
            except ValueError:
                # Ignore files that don't have an integer as the stem
                pass

    if existing_numbers:
        next_number = max(existing_numbers) + 1
    else:
        next_number = 1

    # Construct the file path
    file_path = recordings_folder / f"{next_number}.json"

    # Save the JSON data to the file
    with file_path.open("w") as f:
        json.dump(data, f, indent=2)

    return {"status": "ok", "message": f"Saved to {file_path}"}


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000,
                        help="Port number on which the API will run")
    parser.add_argument("--folder_name", type=str, default="recordings",
                        help="Name of the folder where recordings will be saved")
    args = parser.parse_args()

    # Store folder name in app's state so the route can see it
    app.state.folder_name = args.folder_name

    uvicorn.run(app, host="0.0.0.0", port=args.port)
