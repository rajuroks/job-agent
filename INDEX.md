# 📖 Dice Job Agent - Complete Documentation Index

## 🎯 Getting Started

**Start here if you're new:**
1. Read [BUILD_SUMMARY.md](BUILD_SUMMARY.md) - 5 min overview
2. Run [quickstart.sh](quickstart.sh) - Setup in 5 minutes
3. Configure [config/filters.json](config/filters.json) - Set your job preferences
4. Run `python main.py dashboard` - Start the web UI

## 📚 Documentation Files

### Core Documentation
- **[README.md](README.md)** - Complete feature documentation and user guide
  - Features overview
  - Installation instructions
  - Usage guide (CLI and Dashboard)
  - Ubuntu deployment guide
  - Configuration guide
  - Troubleshooting

- **[BUILD_SUMMARY.md](BUILD_SUMMARY.md)** - What's been built for you
  - Complete feature list
  - File structure
  - Quick start (5 minutes)
  - Command reference
  - Ubuntu deployment steps

### Configuration & Examples
- **[config/filters.json](config/filters.json)** - Your job filter settings
  - Employment type (Full-Time, Contract, Hybrid, Remote)
  - Keywords and exclusions
  - Salary filters
  - Application settings
  - Scheduler configuration

- **[CONFIG_EXAMPLES.md](CONFIG_EXAMPLES.md)** - Example configurations
  - Python developer example
  - Data engineer example
  - Senior full-stack example
  - DevOps engineer example
  - Frontend developer example
  - Tips for configuration
  - Seasonal adjustments

### Deployment & Operations
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Ubuntu server deployment
  - System dependencies
  - Systemd service setup
  - Nginx reverse proxy (optional)
  - Service management

- **[deploy.sh](deploy.sh)** - Automated Ubuntu deployment script
  - Installs all dependencies
  - Sets up virtual environment
  - Configures systemd services
  - One command deployment

### Features & Architecture
- **[FEATURES.md](FEATURES.md)** - Detailed feature descriptions
  - Job scraping
  - Smart filtering
  - Auto-application
  - Daily statistics
  - Web dashboard
  - Performance characteristics
  - Advanced usage examples

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
  - Component overview
  - Data flow diagrams
  - Module dependencies
  - Database schema
  - Configuration hierarchy
  - Deployment architecture
  - Performance metrics

### Quick Reference
- **[COMMANDS.md](COMMANDS.md)** - Command reference
  - Setup commands
  - Configuration commands
  - Running the agent
  - Ubuntu server commands
  - Logging and monitoring
  - Database commands
  - Troubleshooting commands

## 🚀 Quick Start Commands

```bash
# 1. Setup (first time only)
bash quickstart.sh
cp .env.example .env
nano .env  # Add your Dice credentials

# 2. Configure your filters
nano config/filters.json

# 3. Test the agent
python main.py run-once

# 4. Start web dashboard
python main.py dashboard
# Open http://localhost:5000
```

## 🌐 Web Dashboard

Access at **http://localhost:5000**

Features:
- 📊 Real-time statistics (jobs found, matched, applied)
- ⚙️ Configuration management (filter by type, keywords, salary)
- 🎮 Agent controls (start, stop, run once)
- 📋 Application history (last 7 days)
- 📈 Daily statistics tracking

## 🐧 Ubuntu Server Deployment

```bash
# One command setup:
sudo bash deploy.sh

# Or manual steps:
sudo apt-get install -y python3 python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
cp .env.example .env
# Edit .env with credentials
sudo cp job-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable job-agent
sudo systemctl start job-agent
```

## 📊 Project Structure

```
job-agent/
├── src/                          # Python source code
│   ├── logger.py                # Logging setup
│   ├── config.py                # Configuration management
│   ├── database.py              # SQLite database
│   ├── dice_scraper.py          # Dice.com scraper (Playwright)
│   ├── job_matcher.py           # Job filtering logic
│   ├── applicant.py             # Auto-application module
│   ├── scheduler.py             # Job scheduling (APScheduler)
│   └── dashboard.py             # Web dashboard (Flask)
├── config/
│   └── filters.json             # Job filter configuration
├── data/
│   └── jobs.db                  # SQLite database (auto-created)
├── logs/
│   └── agent_YYYYMMDD.log      # Daily log files
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── job-agent.service            # Systemd service (Ubuntu)
├── job-agent-dashboard.service  # Dashboard service (Ubuntu)
├── deploy.sh                    # Ubuntu deployment script
├── quickstart.sh                # Quick setup script
└── *.md                         # Documentation files
```

## 🎯 Configuration Quick Guide

### Filter by Employment Type
```json
"employment_type": ["Full-Time", "Remote", "Hybrid"]
```

### Filter by Keywords
```json
"keywords": ["Python", "AWS", "Backend"],
"exclude_keywords": ["unpaid", "internship"]
```

### Salary Filter
```json
"min_salary": 80000  // Annual salary in USD
```

### Application Settings
```json
"auto_apply": true,                    // Enable auto-apply
"max_applications_per_day": 50,        // Limit per day
"apply_delay_seconds": 2,              // Delay between apps
"check_interval_minutes": 60           // Check every hour
```

## 🔄 Main Workflow

```
1. SCRAPE: Downloads job listings from Dice.com
   │
   ├─ Uses Playwright browser automation
   ├─ Parses job details
   └─ Stores in SQLite database
   │
2. FILTER: Matches jobs against your criteria
   │
   ├─ Checks employment type
   ├─ Checks keywords
   ├─ Checks salary range
   ├─ Checks location
   └─ Excludes matches
   │
3. APPLY: Automatically applies to matched jobs
   │
   ├─ Logs into your Dice account
   ├─ Navigates to each job
   ├─ Clicks apply button
   ├─ Confirms submission
   └─ Records in database
   │
4. STATS: Updates daily statistics
   │
   ├─ Jobs found
   ├─ Jobs matched
   ├─ Applications submitted
   └─ Visible in dashboard
```

## 📈 Expected Results

**Daily Activity:**
- Jobs found: 20-50 (depends on keywords)
- Jobs matched: 5-30 (after filtering)
- Applications: Up to your limit (default: 50)

**Success Metrics:**
- Response rate: 10-30% (depends on role, location, salary)
- Time to interview: 1-7 days typically
- Database growth: ~1-2MB per 1000 jobs

## 🛠️ Key Features

✅ **Automated Scraping** - Monitors Dice.com 24/7
✅ **Smart Filtering** - Multiple filter types
✅ **Auto-Application** - Applies automatically
✅ **Daily Stats** - Track your progress
✅ **Web Dashboard** - Beautiful management UI
✅ **Database Tracking** - Prevents duplicates
✅ **Scheduled Execution** - Configurable intervals
✅ **Comprehensive Logging** - Detailed logs
✅ **Production Ready** - Systemd, error handling
✅ **Easy Deployment** - One-command Ubuntu setup

## 📞 Support & Troubleshooting

### Common Issues
| Issue | Solution | Docs |
|-------|----------|------|
| Login fails | Check credentials in .env | [README.md](README.md#troubleshooting) |
| No jobs found | Make filters less strict | [README.md](README.md#troubleshooting) |
| Apps not submitting | Update HTML selectors | [README.md](README.md#troubleshooting) |
| Port 5000 in use | Use different port | [COMMANDS.md](COMMANDS.md) |
| Database errors | Delete data/jobs.db | [README.md](README.md#troubleshooting) |

See [README.md](README.md#troubleshooting) for detailed troubleshooting guide.

## 🎓 Learning Path

1. **Understanding** (10 min)
   - Read [BUILD_SUMMARY.md](BUILD_SUMMARY.md)
   - Check [FEATURES.md](FEATURES.md)

2. **Setup** (5 min)
   - Run [quickstart.sh](quickstart.sh)
   - Configure [.env](.env.example)

3. **Configuration** (10 min)
   - Edit [config/filters.json](config/filters.json)
   - Review [CONFIG_EXAMPLES.md](CONFIG_EXAMPLES.md)

4. **Testing** (5 min)
   - Run `python main.py run-once`
   - Check logs and database

5. **Deployment** (20 min)
   - Understand [ARCHITECTURE.md](ARCHITECTURE.md)
   - Follow [DEPLOYMENT.md](DEPLOYMENT.md)
   - Or run `sudo bash deploy.sh`

6. **Operations** (ongoing)
   - Monitor [Web Dashboard](http://localhost:5000)
   - Check logs: `tail -f logs/agent_*.log`
   - Query stats: `sqlite3 data/jobs.db`

## 🔗 Navigation Guide

**If you want to...**
- **Get started quickly** → [BUILD_SUMMARY.md](BUILD_SUMMARY.md)
- **Deploy to Ubuntu** → [DEPLOYMENT.md](DEPLOYMENT.md)
- **Understand the system** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **See configuration examples** → [CONFIG_EXAMPLES.md](CONFIG_EXAMPLES.md)
- **Find a command** → [COMMANDS.md](COMMANDS.md)
- **Learn about features** → [FEATURES.md](FEATURES.md)
- **Full documentation** → [README.md](README.md)
- **Configure filters** → [config/filters.json](config/filters.json)

## ✅ Pre-Launch Checklist

Before running the agent:
- [ ] Read [BUILD_SUMMARY.md](BUILD_SUMMARY.md)
- [ ] Run [quickstart.sh](quickstart.sh)
- [ ] Edit `.env` with Dice credentials
- [ ] Edit `config/filters.json` with your preferences
- [ ] Run `python main.py run-once` to test
- [ ] Check logs for errors
- [ ] Access http://localhost:5000
- [ ] Click "Start Agent" button

For Ubuntu deployment:
- [ ] Run `sudo bash deploy.sh`
- [ ] Edit `/home/ubuntu/job-agent/.env`
- [ ] Run `sudo systemctl start job-agent`
- [ ] Access http://your-server:5000
- [ ] Monitor logs: `sudo journalctl -u job-agent -f`

## 🚀 You're All Set!

Everything is ready to go. Start with:

```bash
python main.py dashboard
# Then open http://localhost:5000
```

Or deploy to Ubuntu:

```bash
sudo bash deploy.sh
```

Good luck with your job search! 🎯

---

**Questions?** Check the relevant documentation file above.
**Something broken?** See [README.md#troubleshooting](README.md#troubleshooting).
