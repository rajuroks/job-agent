#!/bin/bash
# Ubuntu Server Deployment Script for Dice Job Agent

set -e

echo "=================================================="
echo "Dice Job Agent - Ubuntu Deployment Script"
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "This script must be run as root (sudo)"
  exit 1
fi

# Variables
DEPLOY_USER="ubuntu"
DEPLOY_HOME="/home/$DEPLOY_USER"
APP_DIR="$DEPLOY_HOME/job-agent"
VENV_DIR="$APP_DIR/venv"

echo ""
echo "Step 1: Update system packages..."
apt-get update
apt-get upgrade -y

echo ""
echo "Step 2: Install system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    chromium-browser \
    nginx \
    curl \
    wget \
    git

echo ""
echo "Step 3: Create application directory..."
if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
    chown -R $DEPLOY_USER:$DEPLOY_USER "$APP_DIR"
else
    echo "Directory $APP_DIR already exists"
fi

echo ""
echo "Step 4: Clone/Setup job-agent..."
if [ ! -d "$APP_DIR/.git" ]; then
    echo "Please clone the repository to $APP_DIR first:"
    echo "  cd $APP_DIR && git clone <repo> ."
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "Step 5: Create Python virtual environment..."
sudo -u $DEPLOY_USER python3 -m venv "$VENV_DIR"

echo ""
echo "Step 6: Install Python dependencies..."
sudo -u $DEPLOY_USER "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u $DEPLOY_USER "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

echo ""
echo "Step 7: Install Playwright browsers..."
sudo -u $DEPLOY_USER "$VENV_DIR/bin/playwright" install

echo ""
echo "Step 8: Setup environment variables..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    chown $DEPLOY_USER:$DEPLOY_USER "$APP_DIR/.env"
    echo "Created .env file - EDIT with your Dice credentials:"
    echo "  nano $APP_DIR/.env"
else
    echo ".env already exists"
fi

echo ""
echo "Step 9: Setup systemd services..."
cp "$APP_DIR/job-agent.service" /etc/systemd/system/
cp "$APP_DIR/job-agent-dashboard.service" /etc/systemd/system/
systemctl daemon-reload

echo ""
echo "Step 10: Enable services..."
systemctl enable job-agent
systemctl enable job-agent-dashboard

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit your Dice credentials:"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. Update job filters:"
echo "   nano $APP_DIR/config/filters.json"
echo ""
echo "3. Start services:"
echo "   sudo systemctl start job-agent"
echo "   sudo systemctl start job-agent-dashboard"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status job-agent"
echo "   sudo systemctl status job-agent-dashboard"
echo ""
echo "5. Access dashboard:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "6. View logs:"
echo "   sudo journalctl -u job-agent -f"
echo "   sudo journalctl -u job-agent-dashboard -f"
echo ""
echo "=================================================="
