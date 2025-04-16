#!/usr/bin/env python3

import copy

from utils.utils import extract_first_python_code

from pipeline.xpath_builder_planning import Planning

from shared import gpt41_llm

from langchain_core.messages import HumanMessage

import json


SPIDER_COMBINATION_PROMPT_INSTRUCTIONS: str = """
> You are a senior Python-based web scraping engineer with extensive expertise in robust and clean scraper development for production environments. You have received a draft scraping plan defining user goals and some initial spider implementations.
>
> **Guidelines to follow strictly:**
>
> - The provided spider code implementations are your authoritative data source. Trust the attribute selectors and xpaths you found in the provided scripts.
> - User plans and desires are high-level guidelines and drafts, but the actual spider code logic and extraction paths are to be treated as the definitive source of truth.
> - Combine any provided scripts into a single cohesive and clearly-structured scraper class, ensuring readability, maintainability, and straightforward debugging procedures.
> - All script functionality must execute when the `if __name__ == "__main__":` condition is met, as it will be periodically scheduled for repeated runs on a cloud infrastructure.
> - Clearly separate data fetching, parsing logic, and execution procedures.
> - Provide helpful, clear, and concise logging or print statements for easy monitoring.
> - Keep it simple.
>

Please combine the spiders into a unified script, but use Playwright.
"""


def remove_example_xpaths_from_actions(data):
    """
    Returns a deep copy of the provided dictionary but removes
    the 'example_xpaths_you_might_need' key from each item in 'action_list'.
    """
    # Create a deep copy to avoid mutating the original data.
    data_copy = copy.deepcopy(data)

    # Iterate over each action in 'action_list' and remove the unwanted key.
    if "action_list" in data_copy:
        for action in data_copy["action_list"]:
            action.pop("example_xpaths_you_might_need", None)
            action.pop("verify", None)

    return data_copy


def get_spider_combination_prompt(
    PLANNER_IDX_TO_RESULT: dict[int, dict[str, str]],
    xpath_builder_structured_planning: Planning
        ) -> str:
    SPIDER_COMBINATION_PROMPT: str = ""

    for planner_idx, result in PLANNER_IDX_TO_RESULT.items():
        spider_code_runnable: str = result["spider_code_runnable"]
        # spider_output: str = result["spider_output"]

        # print(spider_output)
        # input()

        plan = xpath_builder_structured_planning.in_url_list[planner_idx]

        plan_json = plan.model_dump().copy()

        plan_json = remove_example_xpaths_from_actions(
            plan_json
        )

        # prettyprinter.cpprint(plan_json)

        dump_plan_json: str = json.dumps(plan_json, indent=4)

        # print(dump_plan_json)

        SPIDER_COMBINATION_PROMPT += "--> USER THOUGHTS:\n"
        SPIDER_COMBINATION_PROMPT += f"```json\n{dump_plan_json}\n```\n\n"
        SPIDER_COMBINATION_PROMPT += "--> SPIDER CODE:\n"
        SPIDER_COMBINATION_PROMPT += f"```python\n{spider_code_runnable}\n```\n\n"

    SPIDER_COMBINATION_PROMPT += SPIDER_COMBINATION_PROMPT_INSTRUCTIONS

    return SPIDER_COMBINATION_PROMPT


def get_spider_combination(
    PLANNER_IDX_TO_RESULT: dict[int, dict[str, str]],
    xpath_builder_structured_planning: Planning
        ) -> str:
    SPIDER_COMBINATION_PROMPT: str = get_spider_combination_prompt(
        PLANNER_IDX_TO_RESULT=PLANNER_IDX_TO_RESULT,
        xpath_builder_structured_planning=xpath_builder_structured_planning
    )

    print(SPIDER_COMBINATION_PROMPT)

    spider_combination_response = gpt41_llm.invoke(
        [
            HumanMessage(content=SPIDER_COMBINATION_PROMPT)
        ]
    )

    print("--- SPIDER COMBINATION RESPONSE ---")
    print(spider_combination_response.content)

    spider_code: str = extract_first_python_code(
        spider_combination_response.content
    )

    print("--- SPIDER CODE ---")
    print(spider_code)

    return spider_code
