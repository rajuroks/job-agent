import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Goto page...")
        await page.goto("https://www.dice.com/jobs?q=cybersecurity&remote=true&hybrid=true&filters.postedDate=1")
        await page.wait_for_timeout(5000)
        
        # In Playwright we can search inside shadow DOM. Let's see all links or h3s.
        job_titles = await page.locator("a.card-title-link").all_inner_texts()
        if not job_titles:
            # Let's just find anything with 'job' or 'card' class or tag
            all_text = await page.evaluate("() => document.body.innerText")
            print("Page Text length:", len(all_text))
            if len(all_text) < 500:
                print("Text:", all_text)
            
            # Use querySelectorAll with composed tree access if possible, or just playright's 'css=' which crosses shadow DOM open boundaries
            titles = await page.locator("css=a").element_handles()
            found = []
            for t in titles:
                text = await t.inner_text()
                href = await t.get_attribute("href")
                if href and "jobs/detail/" in href:
                    found.append(text)
            print("Found via jobs/detail href:", len(found))
            job_titles = found

        print(f"Titles: {job_titles[:5]}")
        await browser.close()
        print("Done.")

asyncio.run(main())
