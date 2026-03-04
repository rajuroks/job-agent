import asyncio
from src.dice_scraper import DiceScraper, scrape_dice_jobs

filters = {
    'keywords': ['cybersecurity'],
    'employment_type': ['Contract', 'Remote', 'Hybrid']
}

print("Running scraper...")
scraper = DiceScraper()
url = scraper._build_search_url(filters)
print(f"Built URL: {url}")

jobs = scrape_dice_jobs(filters)
print(f"Found {len(jobs)} jobs")
if jobs:
    for job in jobs[:3]:
        print(job)
