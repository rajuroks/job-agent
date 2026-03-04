# Complete Job Agent Configuration Examples

## Example 1: Python Developer (Mid-Level)

```json
{
  "job_filters": {
    "employment_type": ["Full-Time", "Hybrid"],
    "keywords": ["Python", "Django", "REST API", "PostgreSQL"],
    "exclude_keywords": ["unpaid", "internship", "entry-level"],
    "min_salary": 80000,
    "locations": ["USA", "Remote"],
    "exclude_companies": ["Startup A", "Company B"]
  },
  "application_settings": {
    "auto_apply": true,
    "apply_delay_seconds": 3,
    "max_applications_per_day": 30,
    "enable_notifications": true
  },
  "scheduler": {
    "check_interval_minutes": 120,
    "enabled": true
  }
}
```

## Example 2: Data Engineer (Contract)

```json
{
  "job_filters": {
    "employment_type": ["Contract"],
    "keywords": ["Spark", "Hadoop", "Python", "AWS", "Data Pipeline"],
    "exclude_keywords": ["startup", "equity only"],
    "min_salary": 120000,
    "locations": ["Remote"],
    "exclude_companies": []
  },
  "application_settings": {
    "auto_apply": true,
    "apply_delay_seconds": 5,
    "max_applications_per_day": 20,
    "enable_notifications": true
  },
  "scheduler": {
    "check_interval_minutes": 60,
    "enabled": true
  }
}
```

## Example 3: Senior Full-Stack (Remote-Only)

```json
{
  "job_filters": {
    "employment_type": ["Remote"],
    "keywords": ["Senior", "Full-Stack", "React", "Node.js", "AWS", "TypeScript"],
    "exclude_keywords": ["junior", "unpaid", "training"],
    "min_salary": 150000,
    "locations": ["Remote"],
    "exclude_companies": []
  },
  "application_settings": {
    "auto_apply": true,
    "apply_delay_seconds": 2,
    "max_applications_per_day": 50,
    "enable_notifications": true
  },
  "scheduler": {
    "check_interval_minutes": 60,
    "enabled": true
  }
}
```

## Example 4: DevOps/SRE (Hybrid)

```json
{
  "job_filters": {
    "employment_type": ["Full-Time", "Hybrid", "Remote"],
    "keywords": ["DevOps", "Kubernetes", "Docker", "Terraform", "AWS", "CI/CD"],
    "exclude_keywords": ["support", "helpdesk"],
    "min_salary": 100000,
    "locations": ["USA", "Remote"],
    "exclude_companies": []
  },
  "application_settings": {
    "auto_apply": true,
    "apply_delay_seconds": 2,
    "max_applications_per_day": 40,
    "enable_notifications": true
  },
  "scheduler": {
    "check_interval_minutes": 90,
    "enabled": true
  }
}
```

## Example 5: Frontend Developer (Flexible)

```json
{
  "job_filters": {
    "employment_type": ["Full-Time", "Contract", "Hybrid", "Remote"],
    "keywords": ["React", "Vue", "Angular", "JavaScript", "CSS", "Responsive Design"],
    "exclude_keywords": ["unpaid", "volunteer"],
    "min_salary": 75000,
    "locations": ["USA", "Remote"],
    "exclude_companies": []
  },
  "application_settings": {
    "auto_apply": true,
    "apply_delay_seconds": 2,
    "max_applications_per_day": 50,
    "enable_notifications": true
  },
  "scheduler": {
    "check_interval_minutes": 60,
    "enabled": true
  }
}
```

## Tips for Configuration

### 1. Keyword Strategy
- **Specific Keywords**: Fewer matches but higher quality
  ```json
  "keywords": ["Senior Python", "AWS Certified", "Microservices"]
  ```
  
- **Broad Keywords**: More matches, may need filtering
  ```json
  "keywords": ["Python", "AWS", "Backend"]
  ```

### 2. Salary Considerations
- Research average salary for your role/location
- Set min_salary 10-20% below market (to avoid missing good matches)
- Adjust seasonally if needed

### 3. Employment Type Strategy
- Remote: More flexibility, wider opportunity pool
- Hybrid: Growing trend, good work-life balance
- Full-Time: Traditional, more stable
- Contract: Higher pay, more variety

### 4. Application Rate
- Conservative: `max_applications_per_day: 20-30`
- Moderate: `max_applications_per_day: 30-50`
- Aggressive: `max_applications_per_day: 50+`

### 5. Check Frequency
- Busy Job Market: `check_interval_minutes: 30`
- Normal: `check_interval_minutes: 60`
- Less Urgent: `check_interval_minutes: 120-240`

## Dynamic Configuration Examples

### Weekday vs Weekend
```bash
# Run different configs at different times
0 9 * * 1-5 /home/ubuntu/job-agent/run-weekday-config.sh
0 10 * * 0,6 /home/ubuntu/job-agent/run-weekend-config.sh
```

### Seasonal Adjustments
```json
// Q1 - New Year Job Surge
"max_applications_per_day": 50

// Summer - Fewer postings
"max_applications_per_day": 20
```

## Monitoring Configuration

Once you have your config set up, monitor these metrics:

1. **Job Found Trend**: Increasing means more activity in your field
2. **Match Rate**: Matched/Found ratio tells if filters are right
3. **Application Success Rate**: Track interview callbacks
4. **Time to Application**: How long between posting and application

## Advanced: Custom Filters

You can extend the job_matcher.py for custom logic:

```python
def custom_filter(self, job):
    # Add salary negotiability score
    # Add company culture match score
    # Add commute time calculation
    # Add visa sponsorship check
    pass
```

## Configuration Validation

Before deploying, test with:
```bash
python main.py run-once
# Check if jobs found, matched, and applied correctly
```

## Backup Configurations

Keep multiple configs for different job searches:
```
config/
├── filters.json              # Default
├── filters-senior.json       # Senior roles only
├── filters-contract.json     # Contract work
├── filters-startup.json      # Startup jobs
└── filters-remote.json       # Remote only
```

Switch between them:
```python
# Modify config.py to accept config path parameter
python main.py start --config config/filters-senior.json
```
