#!/usr/bin/env python3
import argparse
import asyncio
import requests

from dotenv import load_dotenv
from pyobjtojson import obj_to_json
from langchain_openai import ChatOpenAI
from browser_use_recorder import Agent


import prettyprinter

prettyprinter.install_extras()

load_dotenv()

# 1. Setup an argument parser
parser = argparse.ArgumentParser(description="Run the Agent with command-line args for port and task.")
parser.add_argument(
    "--port", 
    type=int, 
    default=9000, 
    help="API port to send requests to. Default is 9000."
)
parser.add_argument(
    "--task",
    type=str,
    help="Task prompt string to use for the agent."
)
args = parser.parse_args()

# 2. Retrieve the port and task from arguments
API_PORT = args.port
TASK_PROMPT = args.task

# 3. Construct your LLM and agent
gpt41_model = ChatOpenAI(model="gpt-4.1")
agent = Agent(
    task=TASK_PROMPT,
    llm=gpt41_model
)


def send_agent_history_step(data):
    """Send the agent history step data to the specified port."""
    url = f"http://127.0.0.1:{API_PORT}/post_agent_history_step"
    response = requests.post(url, json=data)
    return response.json()


async def record_activity(agent_obj):
    """Hook function to record and send step-by-step agent activity."""
    website_html = None
    website_screenshot = None
    urls_json_last_elem = None
    model_thoughts_last_elem = None
    model_outputs_json_last_elem = None
    model_actions_json_last_elem = None
    extracted_content_json_last_elem = None

    print('--- BEFORE STEP FUNC ---')
    website_html: str = await agent_obj.browser_context.get_page_html()
    website_screenshot: str = await agent_obj.browser_context.take_screenshot()

    print("--> History:")
    if hasattr(agent_obj, "state"):
        history = agent_obj.state.history
    else:
        history = None

    model_thoughts = obj_to_json(
        obj=history.model_thoughts(),
        check_circular=False
    )

    if len(model_thoughts) > 0:
        model_thoughts_last_elem = model_thoughts[-1]

    model_outputs = agent_obj.state.history.model_outputs()
    model_outputs_json = obj_to_json(
        obj=model_outputs,
        check_circular=False
    )

    if len(model_outputs_json) > 0:
        model_outputs_json_last_elem = model_outputs_json[-1]

    model_actions = agent_obj.state.history.model_actions()
    model_actions_json = obj_to_json(
        obj=model_actions,
        check_circular=False
    )

    if len(model_actions_json) > 0:
        model_actions_json_last_elem = model_actions_json[-1]

    extracted_content = agent_obj.state.history.extracted_content()
    extracted_content_json = obj_to_json(
        obj=extracted_content,
        check_circular=False
    )
    if len(extracted_content_json) > 0:
        extracted_content_json_last_elem = extracted_content_json[-1]

    print("--- URLS ---")
    urls = agent_obj.state.history.urls()
    prettyprinter.cpprint(urls)
    urls_json = obj_to_json(
        obj=urls,
        check_circular=False
    )

    if len(urls_json) > 0:
        urls_json_last_elem = urls_json[-1]
        prettyprinter.cpprint(urls_json_last_elem)

    model_step_summary = {
        "website_html": website_html,
        "website_screenshot": website_screenshot,
        "url": urls_json_last_elem,
        "model_thoughts": model_thoughts_last_elem,
        "model_outputs": model_outputs_json_last_elem,
        "model_actions": model_actions_json_last_elem,
        "extracted_content": extracted_content_json_last_elem
    }

    print("--- MODEL STEP SUMMARY ---")

    # Send data to the local server
    send_agent_history_step(data=model_step_summary)


async def run_agent():
    """Run the agent with a maximum of 30 steps, recording each step."""
    try:
        await agent.run(
            before_step_func=record_activity,
            max_steps=30
        )
    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(run_agent())
