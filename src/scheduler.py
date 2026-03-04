from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from src.logger import get_logger
from src.config import config
from src.dice_scraper import scrape_dice_jobs
from src.job_matcher import JobMatcher
from src.applicant import apply_to_matched_jobs
from src.database import JobDatabase

logger = get_logger()

class JobScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db = JobDatabase()
        self.is_running = False

    def start(self):
        """Start the job scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        try:
            # Get interval from config
            interval_minutes = config.scheduler.get('check_interval_minutes', 60)
            
            # Add job to scheduler
            self.scheduler.add_job(
                self._run_job_cycle,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='dice_job_cycle',
                name='Dice Job Application Cycle',
                replace_existing=True
            )

            if not self.scheduler.running:
                self.scheduler.start()
            else:
                self.scheduler.resume()
                
            self.is_running = True
            logger.info(f"Scheduler started - checking every {interval_minutes} minutes")

        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")

    def stop(self):
        """Stop the job scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return

        try:
            self.scheduler.pause()
            self.is_running = False
            logger.info("Scheduler stopped (paused)")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def _run_job_cycle(self):
        """Run one complete job application cycle"""
        try:
            logger.info("=" * 60)
            logger.info("Starting job application cycle")
            logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)

            # Step 1: Scrape jobs from Dice
            logger.info("Step 1: Scraping jobs from Dice...")
            jobs = scrape_dice_jobs(config.job_filters)
            jobs_found = len(jobs)
            logger.info(f"Found {jobs_found} jobs")

            if jobs_found == 0:
                logger.warning("No jobs found")
                self.db.update_daily_stats(0, 0, 0)
                return

            # Step 2: Filter jobs
            logger.info("Step 2: Filtering jobs...")
            matcher = JobMatcher(config.job_filters)
            matched_jobs, unmatched_jobs = matcher.filter_jobs(jobs)
            jobs_matched = len(matched_jobs)
            logger.info(f"Matched {jobs_matched} jobs")

            if jobs_matched == 0:
                logger.warning("No matching jobs found")
                self.db.update_daily_stats(jobs_found, 0, 0)
                return

            # Step 3: Apply to matched jobs
            if config.is_auto_apply_enabled():
                logger.info("Step 3: Applying to matched jobs...")
                applications_submitted = apply_to_matched_jobs(matched_jobs)
                logger.info(f"Submitted {applications_submitted} applications")
            else:
                logger.info("Step 3: Auto-apply is disabled - skipping applications")
                applications_submitted = 0

            # Step 4: Update statistics
            logger.info("Step 4: Updating statistics...")
            self.db.update_daily_stats(jobs_found, jobs_matched, applications_submitted)

            logger.info("=" * 60)
            logger.info(f"Cycle complete: {jobs_found} found, {jobs_matched} matched, {applications_submitted} applied")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error in job cycle: {e}")

    def run_once(self):
        """Run job cycle once (useful for testing)"""
        self._run_job_cycle()

    def get_status(self):
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'next_run_time': str(self.scheduler.get_job('dice_job_cycle').next_run_time) if self.is_running else None,
            'jobs': [job.name for job in self.scheduler.get_jobs()] if self.is_running else []
        }

scheduler = JobScheduler()
