import fnmatch
from src.logger import get_logger
from src.config import config

logger = get_logger()

class JobMatcher:
    def __init__(self, filters=None):
        self.filters = filters or config.job_filters

    def match_job(self, job):
        """Check if job matches all filter criteria"""
        
        # Check if title matches priority patterns (e.g. cyber*, cloud*)
        title_matched = self._match_title_patterns(job)

        # Check employment type (skip if title pattern matched)
        if not title_matched and not self._match_employment_type(job):
            return False, "Employment type mismatch"

        # Check keywords (skip if title pattern matched)
        if not title_matched and not self._match_keywords(job):
            return False, "Keywords mismatch"

        # Check location
        if not self._match_location(job):
            return False, "Location mismatch"

        # Check excluded companies
        if self._is_excluded_company(job):
            return False, "Company is excluded"

        return True, "Match"

    def _match_title_patterns(self, job):
        """Check if job title matches any priority title patterns (glob-style wildcards)"""
        patterns = self.filters.get('title_patterns', [])
        
        if not patterns:
            return False  # No patterns = no special matching

        job_title = job.get('title', '').lower()
        
        for pattern in patterns:
            if fnmatch.fnmatch(job_title, pattern.lower()):
                logger.debug(f"Title pattern matched: '{pattern}' on '{job_title}'")
                return True
        
        return False

    def _match_employment_type(self, job):
        """Check if employment type matches"""
        employment_types = self.filters.get('employment_type', [])
        
        if not employment_types:
            return True  # No filter = accept all

        job_type = job.get('employment_type', '').lower()
        
        # For jobs with a detected employment type, check against filter
        for emp_type in employment_types:
            if emp_type.lower() in job_type:
                return True
        
        # For Unknown types, fall back to checking the job description text
        # since the card text sometimes has the info even if the scraper
        # couldn't parse it into the employment_type field
        if job_type == 'unknown' or job_type == '':
            job_desc = job.get('description', '').lower()
            for emp_type in employment_types:
                if emp_type.lower() in job_desc:
                    return True
        
        return False

    def _match_keywords(self, job):
        """Check if job title contains required keywords.
        
        Only checks the job TITLE (not description) to avoid false positives
        where a keyword like 'cybersecurity' appears in an unrelated job's
        description text (e.g. 'Client Health Management' mentioning cybersecurity
        as a tangential responsibility).
        """
        keywords = self.filters.get('keywords', [])
        
        if not keywords:
            return True  # No keywords = accept all

        job_title = job.get('title', '').lower()
        job_title_no_spaces = job_title.replace(" ", "")

        # Check if any keyword is present in the title
        for keyword in keywords:
            kw_clean = keyword.lower().replace(" ", "")
            if kw_clean in job_title or kw_clean in job_title_no_spaces:
                return True

        return False

    def _match_location(self, job):
        """Check if location matches"""
        locations = self.filters.get('locations', [])
        
        if not locations:
            return True  # No location filter = accept all

        job_location = job.get('location', '').lower()
        
        for location in locations:
            if location.lower() in job_location:
                return True
        
        return False

    def _is_excluded_company(self, job):
        """Check if company is in exclusion list"""
        excluded_companies = self.filters.get('exclude_companies', [])
        
        if not excluded_companies:
            return False

        job_company = job.get('company', '').lower()
        
        for company in excluded_companies:
            if company.lower() in job_company:
                return True
        
        return False

    def filter_jobs(self, jobs):
        """Filter list of jobs and return matched jobs with reasons"""
        matched = []
        unmatched = []

        for job in jobs:
            is_match, reason = self.match_job(job)
            
            if is_match:
                matched.append(job)
                logger.info(f"✓ Matched: {job.get('title')} at {job.get('company')}")
            else:
                unmatched.append({
                    'job': job,
                    'reason': reason
                })
                logger.info(f"✗ Unmatched: {job.get('title')} - {reason}")

        logger.info(f"Filtering complete: {len(matched)} matched, {len(unmatched)} unmatched")
        return matched, unmatched
