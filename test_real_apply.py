import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()
email = os.getenv("DICE_EMAIL")
password = os.getenv("DICE_PASSWORD")

async def test_real_apply():
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
        print("   Logged in!")

        # Pick a real job from search results
        print("2. Finding a test job...")
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
            return results.slice(0, 3);
        }''')
        print(f"   Found {len(job_links)} jobs")

        if not job_links:
            print("   No jobs found, exiting")
            await browser.close()
            return

        # Test with first job
        job_url = job_links[0]
        job_uuid = job_url.rstrip('/').split('/')[-1]
        wizard_url = f"https://www.dice.com/job-applications/{job_uuid}/wizard"
        
        print(f"3. Testing wizard for: {job_url}")
        print(f"   Wizard URL: {wizard_url}")
        await page.goto(wizard_url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # ---- STEP 1 ----
        page_text = await page.evaluate("() => document.body.innerText")
        print(f"\n=== STEP 1 ===")
        if "already applied" in page_text.lower():
            print("   Already applied to this job!")
            await browser.close()
            return
        
        if "Step 1" in page_text:
            print("   Resume & Cover Letter page detected")
            # Check if resume is loaded
            if "pdf" in page_text.lower() or "resume" in page_text.lower():
                print("   ✓ Resume detected on page")
            
            await page.screenshot(path="debug_step1.png")
            
            next_btn = page.locator('button[type="submit"]')
            btn_text = await next_btn.first.inner_text() if await next_btn.count() > 0 else "NOT FOUND"
            print(f"   Submit button text: '{btn_text}'")
            
            if await next_btn.count() > 0:
                await next_btn.first.click()
                await page.wait_for_timeout(3000)
                print("   ✓ Clicked Next")
        else:
            print(f"   WARNING: Step 1 not detected. Page text preview:")
            print(f"   {page_text[:300]}")

        # ---- STEP 2 ----
        page_text = await page.evaluate("() => document.body.innerText")
        print(f"\n=== STEP 2 ===")
        
        if "Step 2" in page_text or "Application Questions" in page_text:
            print("   Application Questions page detected")
            
            # Get all questions and their types
            questions_info = await page.evaluate('''() => {
                const questions = [];
                
                // Find all fieldsets or question containers
                const fieldsets = document.querySelectorAll('fieldset, [class*="question"], [role="group"]');
                
                fieldsets.forEach((fs, idx) => {
                    const legend = fs.querySelector('legend, label, [class*="label"]');
                    const questionText = legend ? legend.innerText.trim() : '';
                    
                    const radios = fs.querySelectorAll('input[type="radio"]');
                    const textInputs = fs.querySelectorAll('input[type="text"], textarea');
                    const selects = fs.querySelectorAll('select');
                    
                    const radioLabels = [];
                    radios.forEach(r => {
                        const label = r.closest('label') || document.querySelector(`label[for="${r.id}"]`);
                        radioLabels.push({
                            name: r.name,
                            value: r.value,
                            label: label ? label.innerText.trim() : r.value,
                            checked: r.checked
                        });
                    });
                    
                    questions.push({
                        index: idx,
                        text: questionText,
                        radioCount: radios.length,
                        radioLabels: radioLabels,
                        textCount: textInputs.length,
                        selectCount: selects.length
                    });
                });
                
                return questions;
            }''')
            
            print(f"   Found {len(questions_info)} question groups:")
            for q in questions_info:
                print(f"     Q{q['index']}: '{q['text']}' -> {q['radioCount']} radios, {q['textCount']} texts, {q['selectCount']} selects")
                for r in q.get('radioLabels', []):
                    print(f"       Radio: name={r['name']}, value={r['value']}, label='{r['label']}', checked={r['checked']}")
            
            # Also get all radios directly
            all_radios = await page.evaluate('''() => {
                const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
                return radios.map(r => {
                    const label = r.closest('label') || document.querySelector(`label[for="${r.id}"]`);
                    const parentLabel = r.parentElement ? r.parentElement.innerText.trim() : '';
                    return {
                        name: r.name,
                        value: r.value,
                        id: r.id,
                        checked: r.checked,
                        label: label ? label.innerText.trim() : parentLabel
                    };
                });
            }''')
            print(f"\n   ALL radio buttons ({len(all_radios)}):")
            for r in all_radios:
                print(f"     name={r['name']}, value={r['value']}, label='{r['label']}', checked={r['checked']}")
            
            await page.screenshot(path="debug_step2_before.png")
            
            # Now try to select radios using Playwright's native click
            # Group radios by name and click first of each group
            radio_groups = {}
            for r in all_radios:
                if r['name'] not in radio_groups:
                    radio_groups[r['name']] = r
            
            print(f"\n   Selecting first option for {len(radio_groups)} question groups...")
            for name, radio in radio_groups.items():
                try:
                    # Use Playwright's native locator to click
                    selector = f'input[type="radio"][name="{name}"][value="{radio["value"]}"]'
                    await page.locator(selector).click(force=True)
                    print(f"     ✓ Selected '{radio['label']}' for group '{name}'")
                except Exception as e:
                    print(f"     ✗ Failed to select for group '{name}': {e}")
            
            await page.wait_for_timeout(1000)
            
            # Verify selections
            verified = await page.evaluate('''() => {
                const radios = Array.from(document.querySelectorAll('input[type="radio"]:checked'));
                return radios.map(r => ({ name: r.name, value: r.value }));
            }''')
            print(f"\n   Verified selections: {verified}")
            
            await page.screenshot(path="debug_step2_after.png")
            
            # Click Next
            next_btn = page.locator('button[type="submit"]')
            if await next_btn.count() > 0:
                await next_btn.first.click()
                await page.wait_for_timeout(3000)
                print("   ✓ Clicked Next")

        # ---- CHECK RESULT ----
        page_text = await page.evaluate("() => document.body.innerText")
        print(f"\n=== AFTER STEP 2 ===")
        
        if "Problem" in page_text or "error" in page_text.lower():
            print("   ✗ ERROR - Problem encountered!")
            # Find the error message
            error_lines = [l.strip() for l in page_text.split('\n') if 'problem' in l.lower() or 'error' in l.lower() or 'required' in l.lower() or 'please' in l.lower()]
            for line in error_lines:
                print(f"     {line}")
        
        if "Step 3" in page_text:
            print("   ✓ Reached Step 3!")
            
            # Look for submit button
            buttons = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('button')).map(b => ({
                    text: b.innerText.trim(),
                    type: b.type
                })).filter(b => b.text);
            }''')
            print(f"   Buttons: {buttons}")
        
        await page.screenshot(path="debug_result.png")
        print(f"\n   Final URL: {page.url}")
        print(f"   Page text preview: {page_text[:500]}")
        
        await browser.close()
        print("\nDone!")

asyncio.run(test_real_apply())
