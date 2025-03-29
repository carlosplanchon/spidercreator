#!/usr/bin/env python3

from exec_funcs import generate_task_id

from exec_funcs import RecordingAPIContext
from exec_funcs import run_recorder_with_pty

from exec_funcs import run_spider_creator_with_pty

from pathlib import Path


def create_spider(
    browser_use_task: str,
    api_port: int = 9000
        ) -> str:
    # Generate a unique task_id for this session
    task_id = generate_task_id()

    print(f"task_id: {task_id}")

    # Create a sub-folder per session
    folder_name = f"recordings/{task_id}"

    Path(folder_name).mkdir(parents=True, exist_ok=True)

    # Start the API in a context manager
    with RecordingAPIContext(
        port=api_port,
        folder_name=folder_name
            ) as api_ctx:
        print("Within the with-block: the API is running on a background thread.")
        # Do whatever logic you want here. For example, sleeping or handling requests:

        run_recorder_with_pty(
            api_port=api_port,
            task=browser_use_task
        )

        print("Exiting the with-block now...")

    # Once we leave the with-block, the context manager stops the API process/thread
    print("Main script is done.")

    run_spider_creator_with_pty(task_id=task_id)

    return task_id
