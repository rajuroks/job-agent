# Dice Job Agent - Features Overview

## What This Agent Does

### 🔍 Job Scraping
- Continuously monitors Dice.com for new job postings
- Scrapes job details: title, company, location, salary, employment type
- Stores all jobs in SQLite database to prevent duplicates

### 🎯 Smart Filtering
Apply jobs based on multiple criteria:
- **Employment Type**: Full-Time, Contract, Hybrid, Remote
- **Keywords**: Required skills/technologies (Python, AWS, etc.)
- **Exclude Keywords**: Skip jobs with certain terms (unpaid, internship)
- **Salary**: Minimum acceptable salary threshold
- **Locations**: Geographic preferences
- **Companies**: Exclude specific companies

### 🤖 Automatic Application
- Automatically applies to matching jobs using browser automation
- Logs in to your Dice account
- Clicks apply buttons and completes applications
- Respects rate limiting (configurable delay between applications)

### 📊 Daily Statistics
Tracks and displays:
- Jobs found today
- Jobs matched (after filtering)
- Applications submitted today
- Application history (last 7 days)
- Success rate

### 🌐 Web Dashboard
Beautiful, responsive web interface at http://localhost:5000:
- View real-time statistics
- Update filters without restarting
- Start/stop agent
- View application history
- Check agent status

### ⏰ Scheduled Execution
- Configurable check intervals (default: hourly)
- Runs in background 24/7
- Restarts automatically on failure (when using systemd)
- Detailed logging of all activities

### 💾 Data Management
- SQLite database for persistent storage
- Prevents duplicate applications
- Historical tracking of all applications
- Daily statistics snapshot

## Configuration Options

```json
{
  "job_filters": {
    "employment_type": ["Full-Time", "Contract", "Hybrid", "Remote"],
    "keywords": ["Python", "JavaScript", "AWS"],
    "exclude_keywords": ["unpaid", "internship"],
    "min_salary": 50000,
    "locations": ["USA"],
    "exclude_companies": ["Company A", "Company B"]
  },
  "application_settings": {
    "auto_apply": true,              // Enable/disable auto-apply
    "apply_delay_seconds": 2,        // Delay between applications
    "max_applications_per_day": 50,  // Daily application limit
    "enable_notifications": true
  },
  "scheduler": {
    "check_interval_minutes": 60,    // Check every hour
    "enabled": true
  }
}
```

## Command Examples

### Development/Testing
```bash
# Test the full cycle once
python main.py run-once

# Start agent (Ctrl+C to stop)
python main.py start

# Start web dashboard
python main.py dashboard

# Check status
python main.py status
```

### Production (Ubuntu Server)
```bash
# Install as system service
sudo bash deploy.sh

# Manage services
sudo systemctl start job-agent
sudo systemctl stop job-agent
sudo systemctl restart job-agent
sudo systemctl status job-agent

# View logs
sudo journalctl -u job-agent -f
sudo journalctl -u job-agent-dashboard -f

# Access dashboard
# http://your-server-ip:5000
```

## Performance Characteristics

- **CPU**: Low (~5% during application, idle rest of time)
- **Memory**: ~100-200MB (Chromium browser when running)
- **Network**: Minimal (one request per check interval)
- **Application Rate**: ~30 jobs/hour (with 2-second delays)
- **Database**: ~10-20MB per 10,000 jobs

## Security Considerations

1. **Credentials**: Stored in .env file (never commit to git)
2. **Rate Limiting**: Configurable to avoid detection
3. **Headless Mode**: Runs without visible browser window
4. **Local Storage**: All data stays on your server
5. **No Third-Party APIs**: No external services used

## Troubleshooting Tips

1. **Login Issues**: Verify credentials, check for 2FA
2. **No Jobs Found**: Adjust keyword filters, try broader search
3. **Applications Failing**: May need to update selectors if Dice changes HTML
4. **High Memory**: Reduce check frequency or applications per day
5. **Database Full**: Old applications can be archived or deleted

## Advanced Usage

### Custom Keywords
Target multiple skill levels:
```json
"keywords": ["Senior Python", "AWS", "Docker"]
```

### Salary Tiers
Different salary ranges based on location:
```json
"min_salary": 80000  // For senior roles
```

### Time-Based Filtering
Update filters for specific job markets:
```bash
# Edit config during business hours
# Different settings for different times
```

### Email Notifications
Get alerts on successful applications:
```python
# Add email module to applicant.py
```

## Integration Examples

### Slack Notifications
```python
# Extend applicant.py to post to Slack webhook
```

### Email Reports
```python
# Add email summary of daily stats
```

### Custom Database Sync
```python
# Export data to external database
```

## Performance Tuning

**For High-Volume Applications:**
- Increase check_interval_minutes to 120+ (less frequent checks)
- Reduce max_applications_per_day to 20-30
- Increase apply_delay_seconds to 5-10

**For Precision Targeting:**
- Narrow down keywords
- Increase salary floor
- Add exclude_keywords for better filtering

**For Cost Efficiency (Cloud):**
- Run at specific hours only
- Use cheaper instance types
- Archive old database entries

## Success Metrics

Track in dashboard:
- Total applications submitted
- Applications per day trend
- Most common matched job titles
- Top companies applying to
- Success rate (interviews/applications)
