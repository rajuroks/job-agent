from flask import Flask, render_template_string, jsonify, request
from datetime import datetime, timedelta
from src.database import JobDatabase
from src.config import config
from src.scheduler import scheduler
import json

app = Flask(__name__)
db = JobDatabase()

# HTML template for dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Agent Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .stat-card .number {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }
        .config-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .config-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .config-group {
            margin-bottom: 20px;
        }
        .config-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .config-group input,
        .config-group select,
        .config-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
            font-family: inherit;
        }
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }
        .checkbox-group label {
            display: flex;
            align-items: center;
            margin: 0;
            width: auto;
        }
        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin-right: 5px;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
        }
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        .btn-danger {
            background: #ff6b6b;
            color: white;
        }
        .btn-danger:hover {
            background: #ee5a52;
        }
        .applications-table {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .applications-table h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #f5f5f5;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #667eea;
            color: #333;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .status-badge {
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .status-submitted {
            background: #d4edda;
            color: #155724;
        }
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Job Agent Dashboard</h1>
            <p>Automated Dice Job Application Agent</p>
        </header>

        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Jobs Found (Today)</h3>
                <div class="number" id="stat-jobs-found">0</div>
            </div>
            <div class="stat-card">
                <h3>Jobs Matched (Today)</h3>
                <div class="number" id="stat-jobs-matched">0</div>
            </div>
            <div class="stat-card">
                <h3>Applications (Today)</h3>
                <div class="number" id="stat-applications">0</div>
            </div>
            <div class="stat-card">
                <h3>Agent Status</h3>
                <div class="number" id="agent-status" style="color: #ff6b6b; font-size: 1.2em;">STOPPED</div>
            </div>
        </div>

        <!-- Configuration -->
        <div class="config-section">
            <h2>⚙️ Configuration</h2>

            <div class="config-group">
                <label><strong>Employment Types</strong></label>
                <div class="checkbox-group">
                    <label><input type="checkbox" id="emp-fulltime" value="Full-Time"> Full-Time</label>
                    <label><input type="checkbox" id="emp-contract" value="Contract"> Contract</label>
                    <label><input type="checkbox" id="emp-hybrid" value="Hybrid"> Hybrid</label>
                    <label><input type="checkbox" id="emp-remote" value="Remote"> Remote</label>
                </div>
            </div>

            <div class="config-group">
                <label><strong>Required Keywords</strong></label>
                <textarea id="keywords" placeholder="Enter keywords separated by comma (e.g., Python, JavaScript, AWS)" rows="3"></textarea>
            </div>

            <div class="config-group">
                <label><strong>Posted Date</strong></label>
                <select id="posted-date">
                    <option value="1">Today</option>
                    <option value="3">Last 3 days</option>
                    <option value="7">Last 7 days</option>
                    <option value="0">No preference</option>
                </select>
            </div>

            <div class="config-group">
                <label><strong>Check Interval (minutes)</strong></label>
                <input type="number" id="check-interval" placeholder="60" min="5" step="5">
            </div>

            <div class="config-group">
                <label><input type="checkbox" id="auto-apply"> Enable Auto-Apply</label>
            </div>

            <div class="config-group">
                <label><strong>Max Applications Per Day</strong></label>
                <input type="number" id="max-applications" placeholder="50" min="1" step="1">
            </div>

            <div class="button-group">
                <button class="btn-primary" onclick="saveConfig()">💾 Save Configuration</button>
                <button class="btn-secondary" onclick="loadConfig()">🔄 Reload Configuration</button>
            </div>
        </div>

        <!-- Controls -->
        <div class="config-section">
            <h2>🎮 Controls</h2>
            <div class="button-group">
                <button class="btn-primary" onclick="startAgent()">▶️ Start Agent</button>
                <button class="btn-danger" onclick="stopAgent()">⏹️ Stop Agent</button>
                <button class="btn-secondary" onclick="runOnce()">⏭️ Run Once</button>
            </div>
        </div>

        <!-- Recent Applications -->
        <div class="applications-table">
            <h2>📋 Recent Applications (Last 7 Days)</h2>
            <table id="applications-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Job Title</th>
                        <th>Company</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="applications-tbody">
                    <tr><td colspan="4" style="text-align: center;">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Load configuration on page load
        window.addEventListener('load', () => {
            loadConfig();
            loadStats();
            loadApplications();
            updateAgentStatus();
            setInterval(updateAgentStatus, 5000);
        });

        function loadConfig() {
            fetch('/api/config')
                .then(r => r.json())
                .then(data => {
                    // Load employment types
                    document.getElementById('emp-fulltime').checked = data.job_filters.employment_type.includes('Full-Time');
                    document.getElementById('emp-contract').checked = data.job_filters.employment_type.includes('Contract');
                    document.getElementById('emp-hybrid').checked = data.job_filters.employment_type.includes('Hybrid');
                    document.getElementById('emp-remote').checked = data.job_filters.employment_type.includes('Remote');

                    // Load other settings
                    document.getElementById('keywords').value = data.job_filters.keywords.join(', ');
                    document.getElementById('posted-date').value = data.job_filters.posted_date || 1;
                    document.getElementById('check-interval').value = data.scheduler.check_interval_minutes;
                    document.getElementById('auto-apply').checked = data.application_settings.auto_apply;
                    document.getElementById('max-applications').value = data.application_settings.max_applications_per_day;
                })
                .catch(err => console.error('Error loading config:', err));
        }

        function saveConfig() {
            const config = {
                job_filters: {
                    employment_type: Array.from(document.querySelectorAll('.checkbox-group input:checked'))
                        .map(el => el.value),
                    keywords: document.getElementById('keywords').value.split(',').map(k => k.trim()).filter(k => k),
                    posted_date: parseInt(document.getElementById('posted-date').value) || 1,
                    locations: [],
                    exclude_companies: []
                },
                application_settings: {
                    auto_apply: document.getElementById('auto-apply').checked,
                    apply_delay_seconds: 2,
                    max_applications_per_day: parseInt(document.getElementById('max-applications').value) || 50,
                    enable_notifications: true
                },
                scheduler: {
                    check_interval_minutes: parseInt(document.getElementById('check-interval').value) || 60,
                    enabled: true
                }
            };

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            })
            .then(r => r.json())
            .then(data => alert('Configuration saved!'))
            .catch(err => alert('Error saving configuration: ' + err));
        }

        function startAgent() {
            fetch('/api/agent/start', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    alert('Agent started!');
                    updateAgentStatus();
                })
                .catch(err => alert('Error: ' + err));
        }

        function stopAgent() {
            fetch('/api/agent/stop', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    alert('Agent stopped!');
                    updateAgentStatus();
                })
                .catch(err => alert('Error: ' + err));
        }

        function runOnce() {
            fetch('/api/agent/run-once', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    alert('Running job cycle...');
                    setTimeout(loadStats, 2000);
                    setTimeout(loadApplications, 2000);
                })
                .catch(err => alert('Error: ' + err));
        }

        function loadStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('stat-jobs-found').textContent = data.jobs_found;
                    document.getElementById('stat-jobs-matched').textContent = data.jobs_matched;
                    document.getElementById('stat-applications').textContent = data.applications_submitted;
                })
                .catch(err => console.error('Error loading stats:', err));
        }

        function loadApplications() {
            fetch('/api/applications')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.getElementById('applications-tbody');
                    if (data.applications.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No applications yet</td></tr>';
                        return;
                    }
                    tbody.innerHTML = data.applications.map(app => `
                        <tr>
                            <td>${new Date(app.date).toLocaleString()}</td>
                            <td>${app.job_title}</td>
                            <td>${app.company}</td>
                            <td><span class="status-badge status-submitted">${app.status}</span></td>
                        </tr>
                    `).join('');
                })
                .catch(err => console.error('Error loading applications:', err));
        }

        function updateAgentStatus() {
            fetch('/api/agent/status')
                .then(r => r.json())
                .then(data => {
                    const statusEl = document.getElementById('agent-status');
                    if (data.is_running) {
                        statusEl.textContent = 'RUNNING';
                        statusEl.style.color = '#28a745';
                    } else {
                        statusEl.textContent = 'STOPPED';
                        statusEl.style.color = '#ff6b6b';
                    }
                })
                .catch(err => console.error('Error checking status:', err));
        }

        // Auto-reload stats
        setInterval(loadStats, 30000);
        setInterval(loadApplications, 60000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'job_filters': config.job_filters,
        'application_settings': config.application_settings,
        'scheduler': config.scheduler
    })

@app.route('/api/config', methods=['POST'])
def save_config():
    data = request.get_json()
    config.job_filters = data.get('job_filters', {})
    config.application_settings = data.get('application_settings', {})
    config.scheduler = data.get('scheduler', {})
    config.save_filters()
    return jsonify({'success': True, 'message': 'Configuration saved'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = db.get_today_stats()
    return jsonify(stats)

@app.route('/api/applications', methods=['GET'])
def get_applications():
    applications = db.get_recent_applications(days=7)
    return jsonify({'applications': applications})

@app.route('/api/agent/start', methods=['POST'])
def start_agent():
    scheduler.start()
    return jsonify({'success': True, 'message': 'Agent started'})

@app.route('/api/agent/stop', methods=['POST'])
def stop_agent():
    scheduler.stop()
    return jsonify({'success': True, 'message': 'Agent stopped'})

@app.route('/api/agent/run-once', methods=['POST'])
def run_once():
    scheduler.run_once()
    return jsonify({'success': True, 'message': 'Running job cycle'})

@app.route('/api/agent/status', methods=['GET'])
def get_agent_status():
    status = scheduler.get_status()
    return jsonify(status)

def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    app.run(host=host, port=port, debug=debug)
