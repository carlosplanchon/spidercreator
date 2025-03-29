#!/usr/bin/env python3

from typing import Any

from langchain_core.messages import HumanMessage

from shared import o1_llm


DRAFT_SCRAPY_SPIDER_CREATION_PROMPT: str = """
Recordings:
```json
{recordings}
```

```mermaid
{mindmap}
```

You are an expert web scraper with 10 years of experience.
Based on the recordings, what is the best Scrapy Spider to create?
I also passed you a Mermaid mindmap.
It is based on what the user had seen.

- Based on this mindmap, create a Scrapy Spider. Use only Scrapy.
- Take into account that the user may had repeated actions many times.
- Evaluate if it makes sense to make a loop or to just skip repeated steps.
"""


def make_scrapy_spider_draft(
    recordings: list[dict[str, Any]],
    mermaid_code: str
        ) -> str:
    scrapy_spider_draft = o1_llm.invoke(
        [
            HumanMessage(
                content=DRAFT_SCRAPY_SPIDER_CREATION_PROMPT.format(
                    recordings=recordings,
                    mindmap=mermaid_code
                )
            )
        ]
    )

    return scrapy_spider_draft.content
