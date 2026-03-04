import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
email = os.getenv("DICE_EMAIL")
password = os.getenv("DICE_PASSWORD")

async def test_full_wizard():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Login
        print("1. Logging in...")
        await page.goto("https://www.dice.com/dashboard/login", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.fill('input[type="email"]', email)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)
        await page.fill('input[type="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/home-feed**", timeout=15000)
        print(f"   Logged in!")

        # Go to wizard
        wizard_url = "https://www.dice.com/job-applications/318d2226-5bdc-4611-9070-38bff24b0ae4/wizard"
        print(f"2. Going to wizard...")
        await page.goto(wizard_url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # STEP 1: Resume & Cover Letter - Click Next
        print("3. STEP 1 - Resume & Cover Letter")
        page_text = await page.evaluate("() => document.body.innerText")
        if "Step 1" in page_text:
            print("   Step 1 detected, clicking Next...")
            await page.click('button[type="submit"]:has-text("Next")')
            await page.wait_for_timeout(3000)
        
        # STEP 2: See what's here
        print("4. STEP 2")
        page_text = await page.evaluate("() => document.body.innerText")
        step2_lines = [l.strip() for l in page_text.split('\n') if l.strip()]
        # Print relevant portion
        for line in step2_lines:
            if any(kw in line.lower() for kw in ['step', 'question', 'next', 'submit', 'required', 'optional', 'select', 'experience', 'years', 'visa', 'sponsorship', 'relocat', 'salary', 'willing']):
                print(f"   {line}")
        
        buttons = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button')).map(el => ({
                text: (el.innerText || '').trim().substring(0, 50),
                type: el.type
            })).filter(b => b.text.length > 0);
        }''')
        print(f"   Buttons: {buttons}")
        
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
                type: el.type || 'text',
                name: el.name || '',
                id: el.id || '',
                placeholder: el.placeholder || '',
                required: el.required,
                visible: el.offsetParent !== null,
                label: ''
            })).filter(i => i.visible);
        }''')
        print(f"   Inputs: {inputs}")

        # Check for select dropdowns or radio buttons
        selects = await page.evaluate('''() => {
            const labels = Array.from(document.querySelectorAll('label, legend, [class*="question"], [class*="label"]'));
            return labels.map(l => ({
                text: (l.innerText || '').trim().substring(0, 100),
                tagName: l.tagName
            })).filter(l => l.text.length > 2);
        }''')
        print(f"   Labels/Questions: {selects}")

        await page.screenshot(path="wizard_step2.png")

        # Try clicking Next/Submit on step 2
        try:
            next_btn = page.locator('button[type="submit"]')
            if await next_btn.count() > 0:
                btn_text = await next_btn.first.inner_text()
                print(f"   Submit button text: '{btn_text}'")
                
                # Click it
                print(f"   Clicking '{btn_text}'...")
                await next_btn.first.click()
                await page.wait_for_timeout(3000)
                
                # STEP 3
                print("5. STEP 3")
                page_text = await page.evaluate("() => document.body.innerText")
                step3_lines = [l.strip() for l in page_text.split('\n') if l.strip()]
                for line in step3_lines:
                    if any(kw in line.lower() for kw in ['step', 'submit', 'review', 'confirm', 'apply', 'application']):
                        print(f"   {line}")
                
                buttons3 = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('button')).map(el => ({
                        text: (el.innerText || '').trim().substring(0, 50),
                        type: el.type
                    })).filter(b => b.text.length > 0);
                }''')
                print(f"   Buttons: {buttons3}")
                await page.screenshot(path="wizard_step3.png")
        except Exception as e:
            print(f"   Error: {e}")

        await browser.close()
        print("Done!")

asyncio.run(test_full_wizard())
