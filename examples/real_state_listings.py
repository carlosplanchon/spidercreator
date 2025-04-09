#!/usr/bin/env python3

from main import create_spider

REAL_ESTATE_LISTING_TASK_PROMPT: str = """
Navigate to the {url} homepage.
Find and click on the link or navigation menu item leading to the real estate/property listings page (e.g., "Properties", "Listings", "Homes for Sale", "Real Estate", "Buy", "Rent").
If the page offers search or filter functionality, optionally perform a basic search or apply filters (e.g., location, property type, price range) to reveal property listings.

Extract visible property listings from the resulting page along with their visible attributes.

Select a small sample of property listings (e.g., 3–5).
For each selected property listing:
- Extract all visible attributes (property title, price, location/address, property type, number of bedrooms/bathrooms, area size, listing date, short description, etc.).
- If a dedicated property detail page is available (e.g., "View property", "More details", or clicking on the listing itself), click through and capture additional attributes (e.g., full property description, agent contact information, amenities, images).

Stop after you’ve collected enough property listings to demonstrate the data extraction (3 to 5 listings).
"""


# This is an uruguayan supermarket with product listings on its website.
url: str = "https://www.wspleiloes.com.br/lotes/imovel/"

browser_use_task: str = REAL_ESTATE_LISTING_TASK_PROMPT.format(url=url)

print("URL")
print(url)

print("Browser use task:")
print(browser_use_task)

# We run spider creation process here.
create_spider(
    browser_use_task=browser_use_task
)
