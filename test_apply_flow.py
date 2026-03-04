import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
email = os.getenv("DICE_EMAIL")
password = os.getenv("DICE_PASSWORD")

async def test_apply_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # visible browser so we can debug
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

        # Step 2: Go to a job detail page (Easy Apply job)
        job_url = "https://www.dice.com/job-detail/318d2226-5bdc-4611-9070-38bff24b0ae4"
        print(f"2. Navigating to job: {job_url}")
        await page.goto(job_url, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Step 3: Find all buttons on the page
        buttons = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button, a')).map(el => ({
                text: (el.innerText || el.textContent || '').trim().substring(0, 50),
                tagName: el.tagName,
                className: (el.className || '').substring(0, 80),
                href: el.href || null,
                type: el.type || null,
                ariaLabel: el.getAttribute('aria-label') || null
            })).filter(b => b.text.toLowerCase().includes('apply') || b.text.toLowerCase().includes('submit') || b.text.toLowerCase().includes('easy'));
        }''')
        print(f"3. Apply/Submit buttons found:")
        for b in buttons:
            print(f"   {b}")

        # Step 4: Try clicking the apply button
        print("4. Clicking apply button...")
        try:
            # Try "Easy Apply" first
            apply_btn = page.locator('button:has-text("Easy Apply")')
            if await apply_btn.count() > 0:
                await apply_btn.first.click()
                print("   Clicked 'Easy Apply'")
            else:
                apply_btn = page.locator('button:has-text("Apply")')
                if await apply_btn.count() > 0:
                    await apply_btn.first.click()
                    print("   Clicked 'Apply'")
                else:
                    print("   No apply button found!")
        except Exception as e:
            print(f"   Error clicking: {e}")

        await page.wait_for_timeout(3000)

        # Step 5: See what's on the page now (modal? new page?)
        print(f"5. Current URL after click: {page.url}")
        
        # Check for modal/dialog
        dialogs = await page.evaluate('''() => {
            const modals = document.querySelectorAll('[role="dialog"], .modal, [class*="modal"], [class*="dialog"], [class*="overlay"]');
            return Array.from(modals).map(m => ({
                role: m.getAttribute('role'),
                className: (m.className || '').substring(0, 100),
                text: (m.innerText || '').substring(0, 300)
            }));
        }''')
        print(f"   Dialogs/Modals found: {len(dialogs)}")
        for d in dialogs:
            print(f"   {d}")

        # Check all buttons/inputs in modal
        all_elements = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('button, input[type="submit"], a')).map(el => ({
                text: (el.innerText || el.textContent || el.value || '').trim().substring(0, 50),
                tagName: el.tagName,
                type: el.type || null,
                visible: el.offsetParent !== null
            })).filter(b => b.visible && (
                b.text.toLowerCase().includes('submit') || 
                b.text.toLowerCase().includes('apply') || 
                b.text.toLowerCase().includes('next') ||
                b.text.toLowerCase().includes('confirm') ||
                b.text.toLowerCase().includes('send')
            ));
        }''')
        print(f"6. Submit/Next/Confirm buttons after apply click:")
        for el in all_elements:
            print(f"   {el}")

        # Take a screenshot for debugging
        await page.screenshot(path="apply_flow_screenshot.png")
        print("7. Screenshot saved to apply_flow_screenshot.png")

        await page.wait_for_timeout(5000)
        await browser.close()

asyncio.run(test_apply_flow())
