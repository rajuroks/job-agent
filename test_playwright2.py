import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Goto page...")
        await page.goto("https://www.dice.com/jobs?q=cybersecurity&remote=true&hybrid=true")
        await page.wait_for_timeout(5000)
        
        # In Playwright we can search inside shadow DOM with `*css=` or just standard selectors if the components are open or Light DOM
        links = await page.evaluate('''() => {
            const allLinks = Array.from(document.querySelectorAll('*'));
            return allLinks.filter(el => el.tagName === 'A').map(a => ({
                href: a.href,
                text: a.innerText,
                className: a.className
            }));
        }''')
        
        jobs = [lnk for lnk in links if "job-" in lnk['href'] or "detail" in lnk['href'] or "dice.com/job" in lnk['href']]
        print("Job links found:", len(jobs))
        for j in jobs[:3]:
            print(f"Text: {j['text']}, Href: {j['href']}, Class: {j['className']}")
            
        await browser.close()
        print("Done.")

asyncio.run(main())
