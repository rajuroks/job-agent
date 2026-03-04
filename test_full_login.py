import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()
email = os.getenv("DICE_EMAIL")
password = os.getenv("DICE_PASSWORD")

async def test_full_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Going to login page")
        await page.goto("https://www.dice.com/dashboard/login", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        print("Filling email...")
        await page.fill('input[type="email"]', email)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)
        
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input')).map(el => ({
                type: el.type,
                name: el.name
            }));
        }''')
        print(f"Inputs after email: {inputs}")
        
        try:
            print("Filling password...")
            await page.fill('input[type="password"]', password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(4000)
            print(f"URL after login: {page.url}")
        except Exception as e:
            print(f"Error: {e}")
            
        await browser.close()

asyncio.run(test_full_login())
