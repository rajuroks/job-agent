import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
email = os.getenv("DICE_EMAIL")
password = os.getenv("DICE_PASSWORD")

async def test_submit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Login
        print("Logging in...")
        await page.goto("https://www.dice.com/dashboard/login", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        await page.fill('input[type="email"]', email)
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)
        await page.fill('input[type="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/home-feed**", timeout=15000)
        print("Logged in!")

        # Find jobs
        await page.goto("https://www.dice.com/jobs?q=cybersecurity&remote=true&hybrid=true", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        job_links = await page.evaluate('''() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/job-detail/"]'));
            const unique = new Set();
            const results = [];
            for (const a of anchors) {
                if (!unique.has(a.href)) {
                    unique.add(a.href);
                    results.push(a.href);
                }
            }
            return results;
        }''')
        
        # Try multiple jobs to find one we can apply to
        for idx, job_url in enumerate(job_links[:5]):
            job_uuid = job_url.rstrip('/').split('/')[-1]
            wizard_url = f"https://www.dice.com/job-applications/{job_uuid}/wizard"
            
            print(f"\n{'='*60}")
            print(f"Testing job {idx}: {job_url}")
            await page.goto(wizard_url, wait_until="networkidle")
            await page.wait_for_timeout(2000)

            page_text = await page.evaluate("() => document.body.innerText")
            current_url = page.url
            
            print(f"  After navigation URL: {current_url}")
            
            if "already applied" in page_text.lower():
                print("  → Already applied, skipping")
                continue
                
            if "wizard" not in current_url:
                print(f"  → Redirected away from wizard (external apply?), skipping")
                continue
            
            if "Step 1" not in page_text:
                print(f"  → No Step 1 found, checking page...")
                print(f"  → First 300 chars: {page_text[:300]}")
                continue

            # STEP 1
            print("  STEP 1: Resume & Cover Letter")
            # Only click the Next button inside the wizard form, not nav buttons
            next_btn = page.locator('button:has-text("Next"):not([class*="nav"])')
            count = await next_btn.count()
            print(f"  Next buttons found: {count}")
            if count > 0:
                # Click the last "Next" button (nav ones are usually first)
                await next_btn.last.click()
                await page.wait_for_timeout(3000)

            # STEP 2
            page_text = await page.evaluate("() => document.body.innerText")
            if "Step 2" in page_text:
                print("  STEP 2: Application Questions")
                
                all_radios = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('input[type="radio"]')).map(r => ({
                        name: r.name, value: r.value
                    }));
                }''')
                
                seen = set()
                for r in all_radios:
                    if r['name'] not in seen:
                        seen.add(r['name'])
                        await page.locator(f'input[type="radio"][name="{r["name"]}"][value="{r["value"]}"]').click(force=True)
                        print(f"    Selected: name={r['name']}, value={r['value']}")
                
                await page.wait_for_timeout(1000)
                
                next_btn = page.locator('button:has-text("Next"):not([class*="nav"])')
                await next_btn.last.click()
                await page.wait_for_timeout(3000)
                
                page_text = await page.evaluate("() => document.body.innerText")
                if "Problem" in page_text and "Step 2" in page_text:
                    print("    → Retry Step 2...")
                    for r in all_radios:
                        await page.locator(f'input[type="radio"][name="{r["name"]}"]').first.click(force=True)
                    await page.wait_for_timeout(500)
                    next_btn = page.locator('button:has-text("Next"):not([class*="nav"])')
                    await next_btn.last.click()
                    await page.wait_for_timeout(3000)
            elif "Step 3" in page_text:
                print("  No Step 2 (skipped to Step 3)")
            else:
                print(f"  → Unexpected page after Step 1")
                print(f"  → First 300 chars: {page_text[:300]}")
                continue

            # STEP 3
            page_text = await page.evaluate("() => document.body.innerText")
            if "Step 3" in page_text or "Review" in page_text:
                print("  STEP 3: Review & Submit")
                submit_btn = page.locator('button:has-text("Submit")')
                count = await submit_btn.count()
                print(f"  Submit buttons found: {count}")
                
                if count > 0:
                    print("  >>> CLICKING SUBMIT <<<")
                    await submit_btn.first.click()
                    await page.wait_for_timeout(5000)
                    
                    final_text = await page.evaluate("() => document.body.innerText")
                    print(f"  Final URL: {page.url}")
                    
                    for kw in ['applied', 'success', 'thank', 'submitted', 'congratulations']:
                        if kw in final_text.lower():
                            print(f"  ✓ SUCCESS: '{kw}' found!")
                    
                    if 'problem' in final_text.lower():
                        print(f"  ✗ ERROR found")
                    
                    print(f"  Result text: {final_text[:400]}")
                    break  # Only test one successful application
            else:
                print(f"  → Did not reach Step 3")
                print(f"  → Page text: {page_text[:300]}")

        await browser.close()
        print("\nDone!")

asyncio.run(test_submit())
