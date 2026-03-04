# Systemd Service Files for Ubuntu Deployment

## job-agent.service
Location: `/etc/systemd/system/job-agent.service`

Runs the main job application scheduler in background.

## job-agent-dashboard.service
Location: `/etc/systemd/system/job-agent-dashboard.service`

Runs the web dashboard for configuration and monitoring.

## nginx Configuration
Location: `/etc/nginx/sites-available/job-agent`

Reverse proxy for the dashboard (optional but recommended).

## Installation Steps

1. Copy service files to systemd directory
2. Enable and start services:
   ```bash
   sudo systemctl enable job-agent job-agent-dashboard
   sudo systemctl start job-agent job-agent-dashboard
   sudo systemctl status job-agent job-agent-dashboard
   ```

3. View logs:
   ```bash
   sudo journalctl -u job-agent -f
   sudo journalctl -u job-agent-dashboard -f
   ```

4. Access dashboard at: http://your-server-ip:5000
