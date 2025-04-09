#!/usr/bin/env python3

from main import create_spider

PRODUCT_LISTING_TASK_PROMPT: str = """
Navigate to {url} homepage.
Extract all products on the homepage with its visible attributes.

Select a small sample of products (e.g., 3–5) on the homepage.
For each selected product:
Extract all visible attributes (price, description, brand, stock status, images, etc.).
If a dedicated product page is available (e.g., “View details” link), click through and capture any additional attributes.
Stop after you’ve collected enough products to demonstrate the data extraction (3 to 5 products).
"""

# This is an uruguayan supermarket with product listings on its website.
url: str = "https://tiendainglesa.com.uy/"

browser_use_task: str = PRODUCT_LISTING_TASK_PROMPT.format(url=url)

print("URL")
print(url)

print("Browser use task:")
print(browser_use_task)

# We run spider creation process here.

create_spider(
    browser_use_task=browser_use_task
)
