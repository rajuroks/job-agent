import sys
from src.dice_scraper import scrape_dice_jobs
from src.job_matcher import JobMatcher
from src.config import config

def main():
    print("Scraping jobs...")
    jobs = scrape_dice_jobs(config.job_filters)
    if not jobs:
        print("No jobs found")
        return
    
    print(f"Found {len(jobs)} jobs. Matching...")
    matcher = JobMatcher(config.job_filters)
    for job in jobs[:10]:
        is_match, reason = matcher.match_job(job)
        print(f"[{'MATCH' if is_match else 'NO MATCH'}] {job['title']} | Reason: {reason} | Salary Min: {job.get('salary_min')} | EmpType: {job.get('employment_type')}")

if __name__ == '__main__':
    main()
