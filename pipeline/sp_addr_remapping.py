#!/usr/bin/env python3

from langchain_core.messages import HumanMessage
from pydantic import Field
from pydantic import BaseModel

from utils.utils import extract_first_python_code

import json

from shared import gpt4o_llm

from typing import Optional


SPIDER_ADDRESS_REMAPPING_PROMPT = """
Original Spider Code:
```
{spider_code}
```

You are an expert programmer.
The HTML of the URLs in the spider will be served locally.
Rewrite the following spider code so that original URLS are now server from local addresses:

URLs to local addresses:
{URL_TO_LOCAL_ADDRESSES}

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


def rewrite_ports_in_spider(
    spider_code: str,
    URL_TO_LOCAL_ADDRESSES: dict[str, str]
        ):
    spider_code_with_local_addresses =\
        structured_spider_code_improver_llm.invoke(
            [
                HumanMessage(
                    content=SPIDER_ADDRESS_REMAPPING_PROMPT.format(
                        spider_code=spider_code,
                        URL_TO_LOCAL_ADDRESSES=json.dumps(
                            URL_TO_LOCAL_ADDRESSES
                        )
                    )
                )
            ]
        )

    spider_code_with_local_addresses_improved: str =\
        extract_first_python_code(
            spider_code_with_local_addresses.spider_code
        )

    return spider_code_with_local_addresses_improved
