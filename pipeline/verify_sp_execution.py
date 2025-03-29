#!/usr/bin/env python3

from pydantic import BaseModel
from pydantic import Field

from shared import gpt4o_llm

from langchain_core.messages import HumanMessage

XPATH_EXECUTION_VERIFICATION_PROMPT: str = """
Spider Code:
```python
{spider_code_runnable}
```

Verification criteria:
```
{verification_criteria}
```

What is expected is: {extracted_content_on_rec}

Spider execution result:
```
{spider_output}
```

You are an expert in web data extraction and information analysis
with over 10 years of experience.
- The website is already loaded. You don't need to verify that.
- From the verification criteria, verify what makes sense to be verified.
  For example, you can't verify clicks since you can't make a click.
- Your task is to evaluate the results obtained by different web
spiders that have extracted information from a specific website.
For each result, analyze the amount of key data extracted,
its relevance, and its completeness.
- Assign a score from 0 to 100 based on these criteria
and provide a brief explanation of your evaluation.
- Ignore encoding issues.
"""


class XPathExecutionVerificationResult(BaseModel):
    score: int = Field(
        ...,
        description="Score from 0 to 100 based on the verification criteria."
    )
    explanation: str = Field(
        ...,
        description="Explanation"
    )


structured_xpath_execution_verifier_llm = gpt4o_llm.with_structured_output(
    XPathExecutionVerificationResult
)


def verify_spider_exec_result(
    spider_code_runnable: str,
    verification_criteria: str,
    extracted_content_on_rec: str,
    spider_output: str
        ) -> XPathExecutionVerificationResult:
    xpath_verification_result = structured_xpath_execution_verifier_llm.invoke(
        [
            HumanMessage(
                content=XPATH_EXECUTION_VERIFICATION_PROMPT.format(
                    spider_code_runnable=spider_code_runnable,
                    verification_criteria=verification_criteria,
                    extracted_content_on_rec=extracted_content_on_rec,
                    spider_output=spider_output
                )
            )
        ]
    )

    return xpath_verification_result
