#!/usr/bin/env python3

from pydantic import BaseModel
from pydantic import Field

from langchain_core.messages import HumanMessage

# from shared import o1_llm
from shared import gemini_2_5_llm

from typing import Optional

import prettyprinter

prettyprinter.install_extras()


# NOTE: Maybe the criteria in the prompt can be improved.

# Used on HTMLClassificationResult.spider_code:
SCRAPY_CREATION_PROMPT: str = """
Write a Scrapy Spider like the one that {extracted_content_on_rec}

I am giving you only a portion of the HTML, not the whole website.
So you may not have the necessary context to do this.
Only write what you can do with the HTML and the context provided.

Write only the spider code.

The xpaths of the spider must comply with:
- Flexibility: The XPath should work even if the targeted element has additional classes or attributes.
- Specificity: The XPath should target the element as specifically as possible without being overly rigid (i.e., it should not break if additional classes or attributes are added).
- Performance: The XPath should not be unnecessarily complex, avoiding long or deeply nested expressions unless absolutely necessary.
- Future-proofing: The XPath should be resilient against minor changes in the HTML structure of the page.
- Readability: The XPath should be easy to understand and maintain.
"""


ROI_CLASSIFICATION_PROMPT: str = """
Piece of HTML:
```html
{website_html}
```

Classify the piece of HTML. Classify as True or False whether
it matches what I am planning to do with the HTML.

Planning:
```json
{planning}
```

Take a deep breath before classifying the piece of HTML.
"""


def get_html_classification_result_struct(
    extracted_content_on_rec: str
        ):

    class HTMLClassificationResult(BaseModel):
        result: bool = Field(
            ...,
            description="Whether the piece of HTML matches what I am planning to do with the HTML."
        )
        explanation: str = Field(
            ...,
            description="Explanation"
        )

        # The field description includes extracted content on rec
        # to orient the generated code towards "extracted_content_on_rec"
        # which will be taken as a target.
        spider_code: Optional[str] = Field(
            ...,
            description=SCRAPY_CREATION_PROMPT.format(
                extracted_content_on_rec=extracted_content_on_rec
            )
        )

    return HTMLClassificationResult


import random
import time
from functools import wraps


def retry_with_exponential_backoff(
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 6
        ):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            num_retries = 0
            delay = initial_delay

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    num_retries += 1
                    if num_retries > max_retries:
                        raise Exception(
                            f"Máximo de tentativas ({max_retries}) atingido: {str(e)}")

                    delay *= exponential_base * (1 + jitter * random.random())
                    time.sleep(delay)

        return wrapper
    return decorator


@retry_with_exponential_backoff()
def call_structured_roi_classifier_llm(
    structured_roi_classifier_llm,
    roi_html_render: str,
    planning: str
        ):

    html_classification_result = structured_roi_classifier_llm.invoke(
        [
            HumanMessage(
                content=ROI_CLASSIFICATION_PROMPT.format(
                    website_html=roi_html_render,
                    planning=planning
                )
            )
        ]
    )

    return html_classification_result


def classify_roi_html_create_cand_spider(
    dom_repr,
    extracted_content_on_rec: str,
    planning: str,
    max_exec_amt: int = 75
        ):
    HTMLClassificationResult = get_html_classification_result_struct(
        extracted_content_on_rec=extracted_content_on_rec
    )

    """
    structured_roi_classifier_llm = o1_llm.with_structured_output(
        HTMLClassificationResult
    )
    """
    structured_roi_classifier_llm = gemini_2_5_llm.with_structured_output(
        HTMLClassificationResult
    )

    CAND_SPIDER_CREATION_RESULTS: dict[int, bool] = {}

    exec_amt: int = 0

    # --- Classify ROI:
    for idx in dom_repr.tree_regions_system.sorted_roi_by_pos_xpath:
        print("*" * 50)
        print(f"IDX: {idx}")
        roi_html_render: str =\
            dom_repr.render_system.get_roi_html_render_with_pos_xpath(
                roi_idx=idx
            )

        # -> ROI Text render
        roi_text_render: str =\
            dom_repr.render_system.get_roi_text_render_with_pos_xpath(
                roi_idx=idx
            )
        print(roi_text_render)

        if roi_text_render.strip() != "":
            html_classification_result = call_structured_roi_classifier_llm(
                structured_roi_classifier_llm=structured_roi_classifier_llm,
                roi_html_render=roi_html_render,
                planning=planning
            )

            print(f"--- HTML CLASSIFICATION RESULT -> IDX: {idx} ---")
            prettyprinter.cpprint(html_classification_result)

            classification_result = html_classification_result
        else:
            classification_result = False

        CAND_SPIDER_CREATION_RESULTS[idx] = classification_result

        exec_amt += 1

        if exec_amt >= max_exec_amt:
            break

    return CAND_SPIDER_CREATION_RESULTS
