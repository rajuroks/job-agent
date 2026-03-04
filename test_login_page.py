import asyncio
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Going to login page")
        await page.goto("https://www.dice.com/dashboard/login", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input')).map(el => ({
                type: el.type,
                name: el.name,
                id: el.id
            }));
        }''')
        print(f"Inputs found: {inputs}")
        
        buttons = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button')).map(el => ({
                text: el.innerText || el.textContent,
                type: el.type,
                id: el.id
            }));
        }''')
        print(f"Buttons found: {buttons}")
        await browser.close()

asyncio.run(test_login())
