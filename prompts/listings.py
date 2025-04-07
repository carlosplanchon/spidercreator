#!/usr/bin/env python3

PRODUCT_LISTING_TASK_PROMPT: str = """
Navigate to {url} homepage.
Extract all products on the homepage with its visible attributes.

Select a small sample of products (e.g., 3–5) on the homepage.
For each selected product:
Extract all visible attributes (price, description, brand, stock status, images, etc.).
If a dedicated product page is available (e.g., “View details” link), click through and capture any additional attributes.
Stop after you’ve collected enough products to demonstrate the data extraction (3 to 5 products).
"""

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
