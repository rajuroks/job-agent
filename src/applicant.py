import asyncio
import time
from playwright.async_api import async_playwright
from src.logger import get_logger
from src.config import config
from src.database import JobDatabase

logger = get_logger()

class JobApplicant:
    def __init__(self):
        self.db = JobDatabase()
        self.base_url = "https://www.dice.com"
        self.login_attempts = 0
        self.max_login_attempts = 3

    async def apply_to_jobs(self, jobs, email=None, password=None):
        """Apply to multiple jobs"""
        email = email or config.email
        password = password or config.password

        if not email or not password:
            logger.error("Email or password not configured")
            return 0

        applied_count = 0
        max_applications = config.get_max_applications_per_day()

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Login to Dice
                login_success = await self._login_to_dice(page, email, password)
                if not login_success:
                    logger.error("Failed to login to Dice")
                    await browser.close()
                    return 0

                # Apply to each job
                for job in jobs:
                    if applied_count >= max_applications:
                        logger.info(f"Reached max applications limit ({max_applications})")
                        break

                    # Check if already applied
                    if self.db.job_exists(job.get('job_id')):
                        logger.debug(f"Already applied to: {job.get('title')}")
                        continue

                    # Apply to job
                    success = await self._apply_to_single_job(page, job)
                    
                    if success:
                        applied_count += 1
                        self.db.add_job(job)
                        self.db.add_application(
                            job.get('job_id'),
                            job.get('title'),
                            job.get('company')
                        )
                        logger.info(f"✓ Applied to: {job.get('title')} at {job.get('company')}")
                    else:
                        logger.warning(f"✗ Failed to apply: {job.get('title')}")

                    # Apply delay between applications
                    delay = config.application_settings.get('apply_delay_seconds', 2)
                    await page.wait_for_timeout(delay * 1000)

                await browser.close()
                logger.info(f"Applied to {applied_count} jobs")
                return applied_count

        except Exception as e:
            logger.error(f"Error applying to jobs: {e}")
            return applied_count

    async def _login_to_dice(self, page, email, password):
        """Login to Dice.com"""
        try:
            logger.info("Logging in to Dice...")
            
            await page.goto("https://www.dice.com/dashboard/login", wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Fill in email
            try:
                await page.fill('input[type="email"]', email, timeout=5000)
            except:
                await page.fill('input[name="email"]', email, timeout=5000)

            # Click submit for email
            await page.click('button[type="submit"]', timeout=5000)
            await page.wait_for_timeout(3000)

            # Fill in password
            await page.fill('input[type="password"]', password, timeout=5000)

            # Click submit for password
            await page.click('button[type="submit"]', timeout=5000)

            # Wait for login to complete
            await page.wait_for_url("**/home-feed**", timeout=15000)
            
            logger.info("Successfully logged in to Dice")
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    async def _apply_to_single_job(self, page, job):
        """Apply to a single job via Dice's application wizard"""
        try:
            job_url = job.get('url')
            
            if not job_url:
                logger.warning(f"No URL for job: {job.get('title')}")
                return False

            # Extract job ID from URL to build wizard URL
            job_uuid = job_url.rstrip('/').split('/')[-1]
            wizard_url = f"https://www.dice.com/job-applications/{job_uuid}/wizard"

            # Navigate to wizard
            logger.info(f"Opening application wizard for: {job.get('title')}")
            await page.goto(wizard_url, wait_until="networkidle")
            await page.wait_for_timeout(2000)

            page_text = await page.evaluate("() => document.body.innerText")
            
            # Check if already applied
            if "already applied" in page_text.lower():
                logger.info(f"  Already applied to: {job.get('title')}")
                return True
            
            # Check if redirected away from wizard (external apply jobs)
            if "wizard" not in page.url:
                logger.warning(f"  External apply job, cannot auto-apply: {job.get('title')}")
                return False

            # --- STEP 1: Resume & Cover Letter ---
            if "Step 1" in page_text:
                logger.info(f"  Step 1: Resume & Cover Letter (using profile resume)")
                next_btn = page.locator('button:has-text("Next")')
                if await next_btn.count() > 0:
                    await next_btn.last.click()
                    await page.wait_for_timeout(3000)
                else:
                    logger.warning(f"  No Next button on Step 1")
                    return False

            # --- STEP 2: Application Questions ---
            page_text = await page.evaluate("() => document.body.innerText")
            if "Step 2" in page_text or "Application Questions" in page_text:
                logger.info(f"  Step 2: Application Questions")
                
                # Use Playwright native clicks for radio buttons (React-friendly)
                all_radios = await page.evaluate('''() => {
                    const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
                    return radios.map(r => ({
                        name: r.name,
                        value: r.value
                    }));
                }''')
                
                # Group by name and click first of each group
                seen_groups = set()
                for radio in all_radios:
                    if radio['name'] not in seen_groups:
                        seen_groups.add(radio['name'])
                        selector = f'input[type="radio"][name="{radio["name"]}"][value="{radio["value"]}"]'
                        try:
                            await page.locator(selector).click(force=True)
                        except Exception:
                            pass
                
                await page.wait_for_timeout(1000)
                
                # Also handle any text inputs or selects
                await page.evaluate('''() => {
                    document.querySelectorAll('input[type="text"], textarea').forEach(input => {
                        if (!input.value || input.value.trim() === '') {
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(input, 'N/A');
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    });
                    document.querySelectorAll('select').forEach(select => {
                        if (select.selectedIndex <= 0 && select.options.length > 1) {
                            select.selectedIndex = 1;
                            select.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    });
                }''')
                
                await page.wait_for_timeout(500)
                
                next_btn = page.locator('button:has-text("Next")')
                if await next_btn.count() > 0:
                    await next_btn.last.click()
                    await page.wait_for_timeout(3000)
                
                # Check if Step 2 had validation errors
                page_text = await page.evaluate("() => document.body.innerText")
                if "Problem" in page_text and "Step 2" in page_text:
                    logger.warning(f"  Step 2 validation error, retrying...")
                    # Try selecting all radios again with force
                    for radio in all_radios:
                        selector = f'input[type="radio"][name="{radio["name"]}"]'
                        try:
                            await page.locator(selector).first.click(force=True)
                        except Exception:
                            pass
                    await page.wait_for_timeout(500)
                    next_btn = page.locator('button:has-text("Next")')
                    if await next_btn.count() > 0:
                        await next_btn.last.click()
                        await page.wait_for_timeout(3000)

            # --- STEP 3: Review & Submit ---
            page_text = await page.evaluate("() => document.body.innerText")
            if "Step 3" in page_text or "Review" in page_text:
                logger.info(f"  Step 3: Review & Submit")
                # The Submit button can be type="button" OR type="submit"
                submit_btn = page.locator('button:has-text("Submit")')
                if await submit_btn.count() > 0:
                    await submit_btn.first.click()
                    await page.wait_for_timeout(4000)
                    
                    # Check for success via URL first (most reliable)
                    if "success" in page.url:
                        logger.info(f"  ✓ Application submitted successfully!")
                        return True
                    
                    # Check for success via page text
                    result_text = await page.evaluate("() => document.body.innerText")
                    if any(kw in result_text.lower() for kw in ['applied', 'success', 'thank', 'submitted', 'congratulations', 'on its way']):
                        logger.info(f"  ✓ Application submitted successfully!")
                        return True
                    elif "problem" in result_text.lower() or "error" in result_text.lower():
                        logger.warning(f"  ✗ Submit encountered an error for: {job.get('title')}")
                        return False
                    else:
                        logger.info(f"  ✓ Application likely submitted (no error detected)")
                        return True
                else:
                    logger.warning(f"  No Submit button found on Step 3")
                    return False
            
            # If we didn't reach Step 3, something went wrong
            page_text = await page.evaluate("() => document.body.innerText")
            if "problem" in page_text.lower() or "error" in page_text.lower():
                logger.warning(f"  ✗ Application wizard encountered issues for: {job.get('title')}")
                return False
            
            logger.info(f"  Application flow completed for: {job.get('title')}")
            return True

        except Exception as e:
            logger.error(f"Error applying to job {job.get('title')}: {e}")
            return False

def apply_to_matched_jobs(jobs, email=None, password=None):
    """Synchronous wrapper for applying to jobs"""
    applicant = JobApplicant()
    return asyncio.run(applicant.apply_to_jobs(jobs, email, password))
