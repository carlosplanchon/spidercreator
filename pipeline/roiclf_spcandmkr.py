#!/usr/bin/env python3

from pydantic import BaseModel
from pydantic import Field

from langchain_core.messages import HumanMessage

from shared import o1_llm

from typing import Optional

import prettyprinter

prettyprinter.install_extras()


# NOTE: Maybe the criteria in the prompt can be improved.

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
        spider_code: Optional[str] = Field(
            ...,
            description=SCRAPY_CREATION_PROMPT.format(
                extracted_content_on_rec=extracted_content_on_rec
            )
        )

    return HTMLClassificationResult


def classify_roi_html_create_cand_spider(
    dom_repr,
    extracted_content_on_rec: str,
    planning: str,
    max_exec_amt: int = 75
        ):

    HTMLClassificationResult = get_html_classification_result_struct(
        extracted_content_on_rec=extracted_content_on_rec
    )

    structured_roi_classifier_llm = o1_llm.with_structured_output(
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
        roi_text_render: str =\
            dom_repr.render_system.get_roi_text_render_with_pos_xpath(
                roi_idx=idx
            )
        print(roi_text_render)

        if roi_text_render.strip() != "":
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
