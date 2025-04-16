#!/usr/bin/env python3

from main import create_spider


JOB_LISTING_TASK_PROMPT: str = """
Navigate to the {url} homepage.
Find and click on the link or navigation menu item leading to the careers/jobs/employment page. (e.g., "Careers", "Jobs", "Employment", "Work with Us").
If the page has a search or filter functionality, optionally perform a basic search or filtering operation to reveal job postings.

Extract visible job postings listed on the resulting page with their visible attributes.

Select a small sample of job postings (e.g., 3–5).
For each selected job posting:
- Extract all visible attributes (job title, company name, location, salary, job type, posted date, description snippet, etc.).
- If a dedicated job detail page is available (e.g., “View job” or “More details” link), click through and capture additional attributes.

Stop after you’ve collected enough job postings to demonstrate the data extraction (3 to 5 listings).
"""


# This is an uruguayan job posting board with job listings on its website.
url: str = "https://uy.computrabajo.com/"

url: str = "https://hiring.cafe/"

browser_use_task: str = JOB_LISTING_TASK_PROMPT.format(url=url)

print("URL")
print(url)

print("Browser use task:")
print(browser_use_task)

# We run spider creation process here.
create_spider(
    browser_use_task=browser_use_task
)
