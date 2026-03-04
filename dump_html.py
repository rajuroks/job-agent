import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Goto page...")
        await page.goto("https://www.dice.com/jobs?q=cybersecurity&remote=true&hybrid=true&filters.postedDate=1")
        await page.wait_for_timeout(3000)
        content = await page.content()
        with open("dice_dump.html", "w") as f:
            f.write(content)
        await browser.close()
        print("Done.")

asyncio.run(main())
