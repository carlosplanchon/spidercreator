#!/usr/bin/env python3

from pydantic import BaseModel
from pydantic import Field

from shared import gpt4o_llm

from langchain_core.messages import HumanMessage


class URLList(BaseModel):
    urls: list[str] = Field(
        ...,
        description="List of URLs present in the spider code."
    )


structured_url_list_llm = gpt4o_llm.with_structured_output(
    URLList
)


URL_LIST_PROMPT = """
Spider code:
```
{spider_code}
```

Give me the list of URLs present in that code.
"""


def get_urls_from_spider_code(spider_code: str) -> list[str]:
    url_list = structured_url_list_llm.invoke(
        [
            HumanMessage(
                content=URL_LIST_PROMPT.format(
                    spider_code=spider_code
                )
            )
        ]
    )

    return url_list.urls
