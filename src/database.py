import sqlite3
import json
from datetime import datetime
from pathlib import Path
from src.logger import get_logger

logger = get_logger()

class JobDatabase:
    def __init__(self, db_path='data/jobs.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                location TEXT,
                employment_type TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                url TEXT,
                description TEXT,
                posted_date TIMESTAMP,
                fetched_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                job_title TEXT,
                company TEXT,
                applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                FOREIGN KEY(job_id) REFERENCES jobs(job_id)
            )
        ''')

        # Stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                jobs_found INTEGER,
                jobs_matched INTEGER,
                applications_submitted INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database initialized")

    def job_exists(self, job_id):
        """Check if job already exists in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM jobs WHERE job_id = ?', (job_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def add_job(self, job_data):
        """Add a new job to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO jobs (job_id, title, company, location, employment_type, 
                                salary_min, salary_max, url, description, posted_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('job_id'),
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('location'),
                job_data.get('employment_type'),
                job_data.get('salary_min'),
                job_data.get('salary_max'),
                job_data.get('url'),
                job_data.get('description'),
                job_data.get('posted_date')
            ))
            conn.commit()
            logger.info(f"Job added: {job_data.get('title')} at {job_data.get('company')}")
        except Exception as e:
            logger.error(f"Error adding job: {e}")
        finally:
            conn.close()

    def add_application(self, job_id, job_title, company):
        """Record application submission"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO applications (job_id, job_title, company, status)
                VALUES (?, ?, ?, ?)
            ''', (job_id, job_title, company, 'submitted'))
            conn.commit()
            logger.info(f"Application recorded: {job_title} at {company}")
        except Exception as e:
            logger.error(f"Error recording application: {e}")
        finally:
            conn.close()

    def get_applied_jobs(self):
        """Get list of job IDs already applied to"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT job_id FROM applications')
        applied_jobs = [row[0] for row in cursor.fetchall()]
        conn.close()
        return applied_jobs

    def update_daily_stats(self, jobs_found, jobs_matched, applications_submitted):
        """Update daily statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().date()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats 
                (date, jobs_found, jobs_matched, applications_submitted)
                VALUES (?, ?, ?, ?)
            ''', (today, jobs_found, jobs_matched, applications_submitted))
            conn.commit()
            logger.info(f"Stats updated: {jobs_found} jobs found, {jobs_matched} matched, {applications_submitted} applied")
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
        finally:
            conn.close()

    def get_today_stats(self):
        """Get today's statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT jobs_found, jobs_matched, applications_submitted 
            FROM daily_stats WHERE date = ?
        ''', (today,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'jobs_found': result[0],
                'jobs_matched': result[1],
                'applications_submitted': result[2]
            }
        return {
            'jobs_found': 0,
            'jobs_matched': 0,
            'applications_submitted': 0
        }

    def get_recent_applications(self, days=7):
        """Get applications from last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT applied_date, job_title, company, status
            FROM applications
            WHERE applied_date >= datetime('now', '-' || ? || ' days')
            ORDER BY applied_date DESC
        ''', (days,))
        
        applications = []
        for row in cursor.fetchall():
            applications.append({
                'date': row[0],
                'job_title': row[1],
                'company': row[2],
                'status': row[3]
            })
        
        conn.close()
        return applications
