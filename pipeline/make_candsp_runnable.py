#!/usr/bin/env python3

from utils.utils import extract_first_python_code

from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from shared import gpt4o_llm

from langchain_core.messages import HumanMessage


SPIDER_REWRITTING_PROMPT = """
Original Spider Code:
```
{spider_code}
```

Rewrite the following spider code so that:
1) It uses only Parsel (do not import or use Scrapy).
2) It prints the result of each field.
3) It does not use urljoin.
5) Use a realistic user-agent.
6) At the end, include a function call to run the spider when the script is executed.

Improved Spider Code:
"""


class SpiderCode(BaseModel):
    spider_code: Optional[str] = Field(
        ...,
        description="Spider code. Write only the python output."
    )


structured_spider_code_improver_llm = gpt4o_llm.with_structured_output(
    SpiderCode
)


def make_cand_spider_runnable(spider_code: str):
    spider_code_improved = structured_spider_code_improver_llm.invoke(
        [
            HumanMessage(
                content=SPIDER_REWRITTING_PROMPT.format(
                    spider_code=spider_code
                )
            )
        ]
    )

    print(spider_code_improved.spider_code)

    spider_code: str = extract_first_python_code(
        spider_code_improved.spider_code
    )

    return spider_code
