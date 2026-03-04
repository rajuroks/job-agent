import asyncio
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Going to dice.com")
        await page.goto("https://www.dice.com/")
        await page.wait_for_timeout(3000)
        
        # Look for login/signin links
        links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a, button')).map(el => ({
                text: el.innerText || el.textContent,
                href: el.href || null,
                tagName: el.tagName
            })).filter(l => l.text && (l.text.toLowerCase().includes('login') || l.text.toLowerCase().includes('sign in')));
        }''')
        print(f"Login/Signin links found: {links}")
        await browser.close()

asyncio.run(test_login())
