import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self, config_path='config/filters.json'):
        self.config_path = config_path
        self.load_filters()
        self.email = os.getenv('DICE_EMAIL', '')
        self.password = os.getenv('DICE_PASSWORD', '')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'

    def load_filters(self):
        """Load filter configuration from JSON"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.job_filters = data.get('job_filters', {})
                self.application_settings = data.get('application_settings', {})
                self.scheduler = data.get('scheduler', {})
        else:
            self.job_filters = {}
            self.application_settings = {}
            self.scheduler = {}

    def save_filters(self):
        """Save current filter configuration to JSON"""
        data = {
            'job_filters': self.job_filters,
            'application_settings': self.application_settings,
            'scheduler': self.scheduler
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def update_employment_types(self, types):
        """Update employment type filters"""
        self.job_filters['employment_type'] = types
        self.save_filters()

    def update_keywords(self, keywords):
        """Update job keywords"""
        self.job_filters['keywords'] = keywords
        self.save_filters()

    def get_employment_types(self):
        """Get current employment type filters"""
        return self.job_filters.get('employment_type', [])

    def get_keywords(self):
        """Get current job keywords"""
        return self.job_filters.get('keywords', [])

    def get_max_applications_per_day(self):
        """Get max applications per day limit"""
        return self.application_settings.get('max_applications_per_day', 50)

    def is_auto_apply_enabled(self):
        """Check if auto-apply is enabled"""
        return self.application_settings.get('auto_apply', False)

config = Config()
