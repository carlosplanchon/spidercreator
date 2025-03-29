#!/usr/bin/env python3

import uuid

import threading
from ptyprocess import PtyProcessUnicode
from typing import Optional

import time

import sys


#######################
#                     #
#   --- TASK ID ---   #
#                     #
#######################

def generate_task_id() -> str:
    """Generate a unique task identifier."""
    return str(uuid.uuid4())


##########################################
#                                        #
#   --- RECORDING WITH BROWSER-USE ---   #
#                                        #
##########################################


def run_recording_api_with_pty(port=8000, folder_name="recordings", on_spawn=None):
    """
    Spawns receive_bu_data.py under a pseudoterminal with the specified
    port and folder name. If on_spawn is given, it is a callback that
    receives the PtyProcessUnicode instance after it is spawned.
    """
    cmd = [
        "python",
        "receive_bu_data.py",
        "--port", str(port),
        "--folder_name", folder_name
    ]
    process = PtyProcessUnicode.spawn(cmd)

    # Let the caller (context manager) keep a reference to the process
    if on_spawn:
        on_spawn(process)

    print(f"Started receive_bu_data.py on port {port}, saving to folder '{folder_name}'.\n"
          f"Press Ctrl+C or exit the program to terminate.\n")

    try:
        while True:
            output = process.readline()
            if not output:  # EOF
                break
            print(output, end="")
    except (EOFError, KeyboardInterrupt):
        print("\nTerminating the process...")
        process.terminate(force=True)
    finally:
        print("Process finished.")


def start_recording_api_thread(
    port=8000,
    folder_name="recordings",
    on_spawn=None
        ) -> threading.Thread:
    """
    Starts the run_recording_api_with_pty function on a separate daemon thread
    and returns the Thread object.
    """
    api_thread = threading.Thread(
        target=run_recording_api_with_pty,
        args=(port, folder_name, on_spawn),
        daemon=True  # Daemon means it ends with main process
    )
    api_thread.start()
    return api_thread


class RecordingAPIContext:
    """
    Context manager that starts the receive_bu_data.py API in a thread upon
    entering, and terminates it upon exiting.
    """
    def __init__(self, port=8000, folder_name="recordings"):
        self.port = port
        self.folder_name = folder_name
        self._thread: Optional[threading.Thread] = None
        self._process: Optional[PtyProcessUnicode] = None

    def __enter__(self):
        """
        Enter the context by starting the API in a background thread.
        We provide an `on_spawn` callback to capture the PtyProcessUnicode.
        """
        def on_spawn(process):
            self._process = process

        self._thread = start_recording_api_thread(
            port=self.port, folder_name=self.folder_name, on_spawn=on_spawn
        )
        return self  # We could return other info as needed

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        On exit, forcibly terminate the pty process if it is still running.
        This should cause the thread to exit from its read loop.
        Then we optionally wait for the thread to confirm it shut down.
        """
        if self._process is not None and self._process.isalive():
            print("Context manager exiting; terminating process...")
            self._process.terminate(force=True)

        # Wait for the thread to finish if it's still alive
        if self._thread is not None and self._thread.is_alive():
            self._thread.join()
        print("Context closed. The background API has been terminated.")


def run_recorder_with_pty(api_port: int, task: str) -> str:
    """
    Run the command:
        python script.py --port <api_port> --task <task>
    in a pseudo-tty using PtyProcessUnicode and return the process's output.

    :param api_port: The desired API port to pass as an argument.
    :param task: The task prompt string to pass as an argument.
    :return: The full output from the spawned process as a string.
    """
    # Prepare the command and arguments
    command = [
        sys.executable,  # 'python' interpreter path, cross-platform safe
        "record_activity.py",
        "--port",
        str(api_port),
        "--task",
        task
    ]
    
    # Spawn a new PTY process
    process = PtyProcessUnicode.spawn(command)
    
    output_collected = []
    
    try:
        while process.isalive():
            # Attempt to read the pseudo-tty output in small chunks
            try:
                chunk = process.read(1024)
                if chunk:
                    # Accumulate output
                    output_collected.append(chunk)
                    # For real-time output, uncomment the line below
                    # print(chunk, end='', flush=True)
            except EOFError:
                # The child process has ended, stop reading
                break
    finally:
        # Close any open resources
        process.close(force=True)
    
    # Combine all chunks into a single string
    return "".join(output_collected)


#############################
#                           #
#   --- SPIDERCREATOR ---   #
#                           #
#############################


def run_spider_creator_with_pty(task_id: str) -> str:
    """
    Run the command:
        python spidercreator.py --task_id <task_id>
    in a pseudo-tty using PtyProcessUnicode and return the process's output.

    :param task_id: The unique task identifier string.
    :return: The full output from the spawned process as a string.
    """
    print(f"\n--- Starting spidercreator.py for task_id: {task_id} ---")
    # Prepare the command and arguments
    command = [
        sys.executable,  # Use the same Python interpreter
        "spidercreator.py",
        "--task_id",
        task_id,
    ]

    process = None # Initialize process to None
    output_collected = []

    try:
        # Spawn a new PTY process
        process = PtyProcessUnicode.spawn(command, echo=False) # echo=False often cleaner
        print(f"Spawned spidercreator.py (PID: {process.pid}). Reading output...")

        while process.isalive():
            # Attempt to read the pseudo-tty output line by line
            try:
                line = process.readline()
                if line:
                    output_collected.append(line)
                    # Print output in real-time:
                    print(line, end='', flush=True)
                else:
                    # readline returned empty string, likely EOF
                    if not process.isalive():
                        break # Process ended
            except EOFError:
                print("\nspidercreator.py process ended (EOFError).")
                break
            except Exception as e:
                print(f"\nError reading from spidercreator.py: {e}")
                break

    except FileNotFoundError:
        error_msg = f"Error: The script 'spidercreator.py' was not found."
        print(error_msg)
        return error_msg # Return error message as output
    except Exception as e:
        error_msg = f"Error spawning or interacting with spidercreator.py: {e}"
        print(error_msg)
        output_collected.append(f"\n{error_msg}\n")
    finally:
        # Ensure the process is terminated and closed
        if process is not None:
            if process.isalive():
                print("\nTerminating spidercreator.py process...")
                process.terminate(force=True)
            time.sleep(0.5) # Brief pause
            exit_status = process.wait() # Get exit status
            process.close()
            print(f"spidercreator.py process finished with exit status: {exit_status}.")
        else:
            print("\nspidercreator.py process was not successfully spawned.")
        print(f"--- Finished spidercreator.py ---")

    # Combine all collected lines into a single string
    return "".join(output_collected)


def create_spider(
    url: str,
    browser_use_task: str,
    api_port: int = 9000
        ):
    # Generate a unique task_id for this session
    task_id = generate_task_id()

    print(f"task_id: {task_id}")

    # Create a sub-folder per session
    folder_name = f"recordings/{task_id}"

    # Start the API in a context manager
    with RecordingAPIContext(port=api_port, folder_name=folder_name) as api_ctx:
        print("Within the with-block: the API is running on a background thread.")
        # Do whatever logic you want here. For example, sleeping or handling requests:

        run_recorder_with_pty(api_port=api_port, task=task)

        print("Exiting the with-block now...")

    # Once we leave the with-block, the context manager stops the API process/thread
    print("Main script is done.")

    spider_creator_output = run_spider_creator_with_pty(task_id=task_id)
