import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import time
from src.logger import get_logger
from src.config import config

logger = get_logger()

class DiceScraper:
    def __init__(self):
        self.base_url = "https://www.dice.com/jobs"
        self.session = None

    async def scrape_jobs(self, filters=None):
        """Scrape jobs from Dice.com with filters"""
        jobs = []
        
        try:
            async with async_playwright() as p:
                logger.info("Starting Dice scraper...")
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Build search URL with filters
                search_url = self._build_search_url(filters)
                logger.info(f"Fetching jobs from: {search_url}")

                await page.goto(search_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)  # Wait for dynamic content

                # Evaluate inside browser to bypass shadow DOM
                raw_jobs = await page.evaluate('''() => {
                    const anchors = Array.from(document.querySelectorAll('a[href*="/job-detail/"]'));
                    const uniqueHrefs = new Set();
                    const jobs = [];
                    
                    for (const a of anchors) {
                        if (uniqueHrefs.has(a.href)) continue;
                        uniqueHrefs.add(a.href);
                        
                        const card = a.closest('dhi-search-card, article') || a.parentElement?.parentElement?.parentElement;
                        if (card) {
                            const textContent = card.innerText || "";
                            const lines = textContent.split('\\n').map(s => s.trim()).filter(s => s.length > 0);
                            jobs.push({
                                url: a.href,
                                lines: lines
                            });
                        }
                    }
                    return jobs;
                }''')

                for raw in raw_jobs:
                    job = self._extract_job_data_from_lines(raw['lines'], raw['url'])
                    if job:
                        jobs.append(job)

                await browser.close()
                logger.info(f"Found {len(jobs)} jobs")
                return jobs

        except Exception as e:
            logger.error(f"Error scraping Dice: {e}")
            return []

    def _build_search_url(self, filters=None):
        """Build Dice search URL with filters"""
        if filters is None:
            filters = config.job_filters

        url = self.base_url + "?q="
        
        # Combine keywords and title_patterns into search terms
        search_terms = set()
        
        # Add keywords
        for kw in filters.get('keywords', []):
            search_terms.add(kw.strip())
        
        # Add title_patterns (strip wildcards for Dice search)
        for pattern in filters.get('title_patterns', []):
            # Strip glob wildcards to get clean search term
            clean = pattern.replace('*', '').replace('?', '').strip()
            if clean:
                search_terms.add(clean)
        
        if search_terms:
            url += "%20".join(list(search_terms)[:5])  # Max 5 search terms
        
        # Add location
        locations = filters.get('locations', [])
        if locations:
            url += f"&location={locations[0]}"

        # Employment type filters (Dice uses specific query params)
        employment_types = filters.get('employment_type', [])
        if employment_types:
            for emp_type in employment_types:
                if emp_type.lower() == 'remote':
                    url += "&remote=true"
                elif emp_type.lower() == 'hybrid':
                    url += "&hybrid=true"

        # Posted date filter (1=Today, 3=Last 3 days, 7=Last 7 days)
        posted_date = filters.get('posted_date', 1)
        if posted_date:
            url += f"&filters.postedDate={posted_date}"

        return url

    def _extract_job_data_from_lines(self, lines, url):
        """Extract job data from text lines parsed from browser"""
        try:
            if len(lines) < 3:
                return None
            
            # Lines array typically looks like:
            # 0: Company
            # 1: "Easy Apply" or "Apply Now" (optional)
            # 2: Job Title
            # X: Location
            
            # Find the title by skipping 'Easy Apply' and 'Apply Now'
            title_idx = 1
            if lines[1].lower() in ['easy apply', 'apply now']:
                title_idx = 2
                
            company = lines[0]
            title = lines[title_idx]
            location = lines[title_idx + 1] if len(lines) > title_idx + 1 else "Unknown"
            
            # Combine all for description and full search
            full_text = " ".join(lines).lower()
            
            employment_type = "Unknown"
            if 'remote' in full_text:
                employment_type = 'Remote'
            elif 'hybrid' in full_text:
                employment_type = 'Hybrid'
            elif 'contract' in full_text:
                employment_type = 'Contract'
            elif 'full-time' in full_text or 'fulltime' in full_text:
                employment_type = 'Full-Time'
                
            # Try to find salary anywhere in the lines
            import re
            salary_min = None
            salary_max = None
            salary_pattern = r'\$([\d,]+)[kKmM]?\s*(?:-|to|–|—)\s*\$([\d,]+)[kKmM]?'
            
            for line in lines:
                matches = re.findall(salary_pattern, line)
                if matches:
                    try:
                        s_min = int(matches[0][0].replace(',', ''))
                        s_max = int(matches[0][1].replace(',', ''))
                        # if someone writes $60k it parses as 60, so multiply by 1000 if it's suspiciously low
                        if s_min < 1000: s_min *= 1000
                        if s_max < 1000: s_max *= 1000
                        salary_min = s_min
                        salary_max = s_max
                        break
                    except ValueError:
                        pass
                        
            if title and company:
                return {
                    'job_id': hash(f"{title}_{company}_{location}"),
                    'title': title,
                    'company': company,
                    'location': location,
                    'employment_type': employment_type,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'url': url,
                    'description': full_text,
                    'posted_date': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.debug(f"Error parsing job lines: {e}")
            
        return None

    def _extract_job_data(self, card):
        """Extract job data from a job card"""
        try:
            # Extract title
            title_elem = card.find('h3', {'class': 'jobTitle'})
            if not title_elem:
                title_elem = card.find('a', {'data-cy': 'job-title'})
            title = title_elem.get_text(strip=True) if title_elem else None

            # Extract company
            company_elem = card.find('div', {'class': 'jobCompany'})
            if not company_elem:
                company_elem = card.find('span', {'data-cy': 'company'})
            company = company_elem.get_text(strip=True) if company_elem else None

            # Extract location
            location_elem = card.find('span', {'class': 'jobLocation'})
            if not location_elem:
                location_elem = card.find('span', {'data-cy': 'location'})
            location = location_elem.get_text(strip=True) if location_elem else None

            # Extract employment type
            employment_type = self._extract_employment_type(card)

            # Extract salary
            salary_min, salary_max = self._extract_salary(card)

            # Extract job URL
            url_elem = card.find('a', {'href': True})
            url = url_elem['href'] if url_elem else None

            # Extract job description
            desc_elem = card.find('div', {'class': 'jobDescription'})
            description = desc_elem.get_text(strip=True) if desc_elem else None

            if title and company:
                return {
                    'job_id': hash(f"{title}_{company}_{location}"),
                    'title': title,
                    'company': company,
                    'location': location,
                    'employment_type': employment_type,
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'url': url,
                    'description': description,
                    'posted_date': datetime.now().isoformat()
                }
        except Exception as e:
            logger.debug(f"Error extracting job data: {e}")
        
        return None

    def _extract_employment_type(self, card):
        """Extract employment type from job card"""
        employment_type = "Unknown"
        
        try:
            text = card.get_text().lower()
            
            if 'remote' in text:
                employment_type = 'Remote'
            elif 'hybrid' in text:
                employment_type = 'Hybrid'
            elif 'full-time' in text or 'fulltime' in text:
                employment_type = 'Full-Time'
            elif 'contract' in text:
                employment_type = 'Contract'
            elif 'part-time' in text:
                employment_type = 'Part-Time'
        except:
            pass
        
        return employment_type

    def _extract_salary(self, card):
        """Extract salary range from job card"""
        import re
        
        salary_min = None
        salary_max = None
        
        try:
            text = card.get_text()
            
            # Look for salary patterns like $50K-$100K
            salary_pattern = r'\$(\d+)[KM]?\s*-\s*\$(\d+)[KM]?'
            matches = re.findall(salary_pattern, text)
            
            if matches:
                salary_min = int(matches[0][0]) * 1000
                salary_max = int(matches[0][1]) * 1000
        except Exception as e:
            logger.debug(f"Error extracting salary: {e}")
        
        return salary_min, salary_max

    async def login(self, email, password):
        """Login to Dice.com"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto("https://www.dice.com/dashboard/login", wait_until="networkidle")
                await page.wait_for_timeout(2000)

                # Enter email
                await page.fill('input[type="email"]', email)
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(2000)

                # Enter password
                await page.fill('input[type="password"]', password)

                # Click submit
                await page.click('button[type="submit"]')
                await page.wait_for_url("**/home-feed**", timeout=15000)

                logger.info("Successfully logged in to Dice")
                await browser.close()
                return True

        except Exception as e:
            logger.error(f"Error logging in to Dice: {e}")
            return False

def scrape_dice_jobs(filters=None):
    """Synchronous wrapper for scraping Dice jobs"""
    scraper = DiceScraper()
    return asyncio.run(scraper.scrape_jobs(filters))
