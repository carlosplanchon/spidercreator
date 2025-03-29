#!/usr/bin/env python3

from shared import o1_llm

from langchain_core.messages import HumanMessage

from pydantic import BaseModel
from pydantic import Field


XPATH_BUILDER_PLANNING_PROMPT: str = """
Spider operation mindmap.
```mermaid
{mindmap}
```

Scrapy Spider:
```python
{scrapy_spider}
```

Okay, now my goal is to build all the xpaths from the HTML itself.
Based on the prior information, grouped by URL, what xpaths I have to build, and for which action?
"""


def make_non_structured_planning(
    # recordings: list[dict[str, Any]],
    mermaid_code: str,
    scrapy_spider: str
        ) -> str:
    xpath_builder_planning = o1_llm.invoke(
        [
            HumanMessage(
                content=XPATH_BUILDER_PLANNING_PROMPT.format(
                    # recordings=recordings,
                    mindmap=mermaid_code,
                    scrapy_spider=scrapy_spider
                )
            )
        ]
    )

    return xpath_builder_planning.content


class Action(BaseModel):
    action_description: str = Field(..., description="User action")
    example_xpaths_you_might_need: list[str] = Field(
        ...,
        description="Example XPaths you might need, also include description."
    )
    verify: str = Field(
        ...,
        description="I will execute this xpaths on the browser. How do I verify that execution have the result I want?, for example, by checking extracted content is correct, or checking that clicking a button navigates to the expected page."
    )


class InUrl(BaseModel):
    url: str = Field(..., description="URL")
    action_list: list[Action]


class Planning(BaseModel):
    in_url_list: list[InUrl]
    summary: str = Field(..., description="Summary")


structured_xpath_builder_llm = o1_llm.with_structured_output(
    Planning
)


def make_structured_planning(
    mermaid_code: str,
    scrapy_spider_draft: str
        ) -> Planning:

    xpath_builder_structured_planning = structured_xpath_builder_llm.invoke(
        [
            HumanMessage(
                content=XPATH_BUILDER_PLANNING_PROMPT.format(
                    mindmap=mermaid_code,
                    scrapy_spider=scrapy_spider_draft
                )
            )
        ]
    )

    return xpath_builder_structured_planning
