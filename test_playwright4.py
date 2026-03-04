import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Goto page...")
        await page.goto("https://www.dice.com/jobs?q=cybersecurity&remote=true&hybrid=true")
        await page.wait_for_timeout(5000)
        
        # We can extract all `a[href*="/job-detail/"]` elements and their text
        jobs_data = await page.evaluate('''() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/job-detail/"]'));
            const uniqueHrefs = new Set();
            const jobs = [];
            
            for (const a of anchors) {
                if (uniqueHrefs.has(a.href)) continue;
                uniqueHrefs.add(a.href);
                
                // The parent element that seems to hold the card content 
                // is usually an article or a div with role=listitem etc.
                // Or we can just find the closest element that has enough children.
                const card = a.closest('dhi-search-card, article') || a.parentElement.parentElement.parentElement;
                
                if (card) {
                    const textContent = card.innerText || "";
                    const lines = textContent.split('\\n').map(s => s.trim()).filter(s => s.length > 0);
                    
                    // Lines might look like:
                    // AaraTechnologies Inc
                    // Easy Apply
                    // CYBER SECURITY
                    // Remote or Hybrid in Chicago, Illinois
                    // Today
                    // Description...
                    // Contract
                    // $60,000 - $70,000
                    
                    jobs.push({
                        url: a.href,
                        lines: lines
                    });
                }
            }
            return jobs;
        }''')
        
        for i, j in enumerate(jobs_data[:3]):
            print(f"--- Job {i} ---")
            print("URL:", j['url'])
            print("Lines:", j['lines'])
            
        await browser.close()
        print("Done.")

asyncio.run(main())
