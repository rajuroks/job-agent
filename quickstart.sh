#!/bin/bash
# Quick Start Guide - Run this first time

echo "🤖 Dice Job Agent - Quick Start Setup"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"
echo ""

# Create venv
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Installing Playwright browsers..."
playwright install

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your Dice credentials:"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "2. Edit job filters in config/filters.json to your preferences"
echo ""
echo "3. Try the agent:"
echo "   python main.py run-once     # Test run (scrapes and applies once)"
echo ""
echo "4. Start the agent:"
echo "   python main.py start        # Runs scheduled job checks"
echo ""
echo "5. Access dashboard:"
echo "   python main.py dashboard    # Open http://localhost:5000"
echo ""
echo "======================================"
