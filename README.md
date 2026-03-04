# Dice Job Agent

Automated job application agent for Dice.com with filtering and daily statistics tracking.

## Features

✅ **Automatic Job Scraping** - Continuously monitors Dice.com for new job postings  
✅ **Smart Filtering** - Filter by employment type (Full-Time, Contract, Hybrid, Remote), keywords, salary, and more  
✅ **Auto-Application** - Automatically applies to matching jobs  
✅ **Daily Statistics** - Track applications submitted, jobs matched, and more  
✅ **Web Dashboard** - Beautiful dashboard to manage filters and view statistics  
✅ **Configurable Scheduler** - Run checks at custom intervals  
✅ **Comprehensive Logging** - Detailed logs of all activities  

## Project Structure

```
job-agent/
├── config/
│   └── filters.json              # Job filters configuration
├── data/
│   └── jobs.db                   # SQLite database (auto-created)
├── logs/
│   └── agent_YYYYMMDD.log       # Daily logs
├── src/
│   ├── __init__.py
│   ├── logger.py                 # Logging setup
│   ├── config.py                 # Configuration management
│   ├── database.py               # SQLite database operations
│   ├── dice_scraper.py           # Dice.com web scraper
│   ├── job_matcher.py            # Job filtering logic
│   ├── applicant.py              # Auto-application module
│   ├── scheduler.py              # Job scheduling
│   └── dashboard.py              # Web dashboard
├── main.py                        # CLI entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                       # This file
```

## Installation

### 1. Clone or Setup the Project

```bash
cd /path/to/job-agent
```

### 2. Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install  # Install browser for Playwright
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Dice.com credentials
nano .env
```

Set your Dice credentials:
```
DICE_EMAIL=your_email@example.com
DICE_PASSWORD=your_password
```

### 5. Configure Job Filters

Edit `config/filters.json` to set your job preferences:

```json
{
  "job_filters": {
    "employment_type": ["Full-Time", "Contract", "Hybrid", "Remote"],
    "keywords": ["Python", "JavaScript", "AWS"],
    "exclude_keywords": ["unpaid", "internship"],
    "min_salary": 50000,
    "locations": ["USA"],
    "exclude_companies": []
  },
  "application_settings": {
    "auto_apply": true,
    "apply_delay_seconds": 2,
    "max_applications_per_day": 50
  },
  "scheduler": {
    "check_interval_minutes": 60,
    "enabled": true
  }
}
```

## Usage

### Command Line Interface

**Start the agent** (runs in background with scheduler):
```bash
python main.py start
```

**Stop the agent**:
```bash
python main.py stop
```

**Run job cycle once** (useful for testing):
```bash
python main.py run-once
```

**Check agent status**:
```bash
python main.py status
```

**Start web dashboard**:
```bash
python main.py dashboard --host 0.0.0.0 --port 5000
# Open http://localhost:5000 in browser
```

### Web Dashboard Features

The web dashboard (http://localhost:5000) provides:

- **Real-time Statistics** - See jobs found, matched, and applications submitted today
- **Configuration Panel** - Update filters without restarting
  - Select employment types (Full-Time, Contract, Hybrid, Remote)
  - Add required keywords
  - Set minimum salary
  - Configure check intervals
  - Enable/disable auto-apply
- **Application History** - View recent applications with timestamps
- **Agent Controls** - Start, stop, or run job cycles manually
- **Status Monitoring** - Check if agent is running and next run time

## Deployment on Ubuntu Server

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y chromium-browser  # For Playwright
```

### 2. Clone Repository

```bash
cd /home/ubuntu
git clone <repo-url> job-agent
cd job-agent
```

### 3. Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

### 4. Create .env File

```bash
cp .env.example .env
nano .env  # Edit with your Dice credentials
```

### 5. Setup Systemd Service

Create `/etc/systemd/system/job-agent.service`:

```ini
[Unit]
Description=Dice Job Application Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/job-agent
Environment="PATH=/home/ubuntu/job-agent/venv/bin"
ExecStart=/home/ubuntu/job-agent/venv/bin/python main.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable job-agent
sudo systemctl start job-agent
sudo systemctl status job-agent
```

### 6. Setup Dashboard Service (Optional)

Create `/etc/systemd/system/job-agent-dashboard.service`:

```ini
[Unit]
Description=Dice Job Agent Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/job-agent
Environment="PATH=/home/ubuntu/job-agent/venv/bin"
ExecStart=/home/ubuntu/job-agent/venv/bin/python main.py dashboard --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable job-agent-dashboard
sudo systemctl start job-agent-dashboard
```

### 7. Setup Nginx Reverse Proxy (Optional)

```bash
sudo apt-get install -y nginx
```

Create `/etc/nginx/sites-available/job-agent`:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/job-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. View Logs

```bash
# Agent logs
tail -f /home/ubuntu/job-agent/logs/agent_*.log

# Systemd logs
sudo journalctl -u job-agent -f
sudo journalctl -u job-agent-dashboard -f
```

## Configuration Guide

### Employment Types
- **Full-Time**: Traditional full-time positions
- **Contract**: Temporary contract roles
- **Hybrid**: Mix of remote and office
- **Remote**: 100% remote work

### Keywords
Add skills/technologies you want to target:
```
Python, JavaScript, AWS, Docker, Kubernetes
```

### Salary Filter
Set minimum acceptable salary (annual in USD):
```
50000  # Will only apply to jobs with salary >= $50,000
```

### Auto-Apply Settings
- **auto_apply**: Enable/disable automatic applications
- **apply_delay_seconds**: Delay between applications (prevent detection)
- **max_applications_per_day**: Limit daily applications

### Scheduler
- **check_interval_minutes**: How often to check for new jobs (60 = hourly)

## Troubleshooting

### Login Issues
- Verify Dice credentials in `.env`
- Check if Dice requires 2FA (may need manual setup)
- Check logs for browser errors

### No Jobs Found
- Check if keyword filters are too restrictive
- Verify filters match actual Dice postings
- Try broadening employment types

### Applications Not Submitting
- Verify login is working
- Check if Dice has changed HTML structure (scraper may need updates)
- Check apply button selector in logs

### Database Issues
- Delete `data/jobs.db` to reset (will lose history)
- Check file permissions in data folder

## Logs

Logs are stored in `logs/agent_YYYYMMDD.log` with:
- Timestamp
- Log level (INFO, WARNING, ERROR, DEBUG)
- Module name
- Message

View today's logs:
```bash
tail -f logs/agent_$(date +%Y%m%d).log
```

## Database

The SQLite database (`data/jobs.db`) tracks:
- **jobs**: All scraped job listings
- **applications**: Submitted applications with dates
- **daily_stats**: Daily statistics (jobs found, matched, applied)

Query stats:
```bash
sqlite3 data/jobs.db "SELECT * FROM daily_stats ORDER BY date DESC LIMIT 10;"
```

## API Endpoints (Dashboard)

- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `GET /api/stats` - Get today's statistics
- `GET /api/applications` - Get recent applications
- `POST /api/agent/start` - Start agent
- `POST /api/agent/stop` - Stop agent
- `POST /api/agent/run-once` - Run once
- `GET /api/agent/status` - Get agent status

## Performance Tips

1. **Increase Check Interval** - Reduces server load
   ```json
   "check_interval_minutes": 120  // Check every 2 hours
   ```

2. **Limit Daily Applications** - Avoid detection
   ```json
   "max_applications_per_day": 30  // Max 30 per day
   ```

3. **Smart Keywords** - More specific = fewer applications
   ```json
   "keywords": ["Senior Python", "AWS"]  // More targeted
   ```

4. **Headless Mode** - Already enabled by default (faster)

## Support

For issues or questions, check:
1. Logs in `logs/` directory
2. Configuration in `config/filters.json`
3. Database for application history
4. Systemd status: `sudo systemctl status job-agent`

## License

MIT License - Use at your own risk. Respect Dice.com terms of service.
