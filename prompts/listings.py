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
