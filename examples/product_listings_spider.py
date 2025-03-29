#!/usr/bin/env python3

from main import create_spider

from prompts.listings import PRODUCT_LISTING_TASK_PROMPT

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
