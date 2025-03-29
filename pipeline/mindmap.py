#!/usr/bin/env python3

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import Field
from pydantic import BaseModel

import json

from shared import o1_llm


class Mermaid(BaseModel):
    """Valid mermaid code."""

    mermaid_code: str = Field(description="Valid mermaid code.")


mermaid_structured_llm = o1_llm.with_structured_output(Mermaid)


MERMAID_WORK_MINDMAP_PROMPT: str = """
You are an AI specialized in generating **valid Mermaid mindmap diagrams** that visualize automated web navigation processes.

## **Objective**
Given a structured sequence of automated browser actions, generate a **Mermaid mindmap** that visually maps out the navigation workflow in a clear and hierarchical manner. 

Ensure that:
- Each **step explicitly specifies the URL** where the action occurs.
- Actions include clear labels such as **(Navigation), (User Interaction), (Data Extraction)**, etc.
- Branching actions (e.g., dropdown selections, multiple paths) are structured logically.
- The diagram maintains a **clean and readable hierarchy**.

## **Formatting Guidelines**
- Use **valid Mermaid syntax** for a **mindmap**.
- The root node should represent the **automation process**.
- Each child node should represent an action, with its **step number, description, and URL**.
- Nested actions should be grouped logically.

## **Few-Shot Example**

### **Example 1: JobHuntPro Scraper**
#### **Output (Mermaid Code)**
```mermaid
mindmap
  root((Automated Web Scraper - JobHuntPro))
    "Step 1: (Page Load) Start on JobHuntPro [URL: https://www.jobhuntpro.com]"
      "Step 2: (User Interaction: Button Click) Accept Cookie Policy [URL: https://www.jobhuntpro.com]"
      "Step 3: (User Interaction: Dropdown) Open 'Job Categories' Menu [URL: https://www.jobhuntpro.com]"
        "Step 4: (User Interaction: Selection) Select 'Software Development' [URL: https://www.jobhuntpro.com/categories/software-development]"
          "Step 5: (Data Extraction: List) Extract job listings [URL: https://www.jobhuntpro.com/categories/software-development]"
          "Step 6: (User Interaction: Pagination) Navigate to next page [URL: https://www.jobhuntpro.com/categories/software-development?page=2]"
        "Step 7: (Navigation: Back) Return to 'Job Categories' Menu [URL: https://www.jobhuntpro.com/categories]"
        "Step 8: (User Interaction: Selection) Select 'Marketing' [URL: https://www.jobhuntpro.com/categories/marketing]"
          "Step 9: (Data Extraction: List) Extract job listings [URL: https://www.jobhuntpro.com/categories/marketing]"
          "Step 10: (User Interaction: Pagination) Navigate to next page [URL: https://www.jobhuntpro.com/categories/marketing?page=2]"
        "Step 11: (Navigation: Back) Return to 'Home' [URL: https://www.jobhuntpro.com]"
```
```

## **Additional Notes**
- If multiple paths exist, clearly **branch them** in the mindmap.
- Do not generate invalid Mermaid syntax.
- Always include **step numbers**, **action types**, and **URLs**.
- Ensure proper indentation for readability.
- Avoid repeating steps unless they bring new information or change in state (e.g., new URL, different action/element, etc.).
"""


def make_mermaid_mindmap(recordings) -> str:
    mermaid_work_mindmap_final = mermaid_structured_llm.invoke(
        [
            HumanMessage(content=json.dumps(recordings)),
            SystemMessage(content=MERMAID_WORK_MINDMAP_PROMPT)
        ]
    )

    return mermaid_work_mindmap_final.mermaid_code
