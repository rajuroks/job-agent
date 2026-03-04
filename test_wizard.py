import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
email = os.getenv("DICE_EMAIL")
password = os.getenv("DICE_PASSWORD")

async def test_wizard_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Step 1: Login
        print("1. Logging in...")
        await page.goto("https://www.dice.com/dashboard/login", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.fill('input[type="email"]', email)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)
        await page.fill('input[type="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/home-feed**", timeout=15000)
        print(f"   Logged in! URL: {page.url}")

        # Step 2: Go to the application wizard directly
        wizard_url = "https://www.dice.com/job-applications/318d2226-5bdc-4611-9070-38bff24b0ae4/wizard"
        print(f"2. Going to wizard: {wizard_url}")
        await page.goto(wizard_url, wait_until="networkidle")
        await page.wait_for_timeout(3000)
        print(f"   Current URL: {page.url}")
        
        # Step 3: See what's on the wizard page
        page_text = await page.evaluate("() => document.body.innerText")
        print(f"3. Page text (first 1000 chars):")
        print(f"   {page_text[:1000]}")
        
        # Step 4: Find all buttons
        buttons = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button, input[type="submit"], a')).map(el => ({
                text: (el.innerText || el.textContent || el.value || '').trim().substring(0, 80),
                tagName: el.tagName,
                type: el.type || null,
                visible: el.offsetParent !== null,
                href: el.href || null
            })).filter(b => b.visible && b.text.length > 0);
        }''')
        print(f"4. Buttons on wizard page:")
        for b in buttons:
            print(f"   {b}")

        # Step 5: Check for resume section / file upload
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                type: el.type || 'text',
                name: el.name || '',
                id: el.id || '',
                placeholder: el.placeholder || '',
                value: (el.value || '').substring(0, 50),
                visible: el.offsetParent !== null
            })).filter(i => i.visible);
        }''')
        print(f"5. Inputs on wizard page:")
        for i in inputs:
            print(f"   {i}")

        await page.screenshot(path="wizard_screenshot.png")
        print("6. Screenshot saved to wizard_screenshot.png")

        await browser.close()

asyncio.run(test_wizard_flow())
