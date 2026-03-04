import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Goto page...")
        await page.goto("https://www.dice.com/jobs?q=cybersecurity&remote=true&hybrid=true")
        await page.wait_for_timeout(5000)
        
        cards = await page.evaluate('''() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/job-detail/"]'));
            return anchors.slice(0, 3).map(a => {
                // Find closest article or card container
                const card = a.closest('div.card') || a.parentElement.parentElement;
                return card ? card.innerText : "no parent";
            });
        }''')
        
        for i, c in enumerate(cards):
            print(f"--- Card {i} ---")
            print(c)
            
        await browser.close()
        print("Done.")

asyncio.run(main())
