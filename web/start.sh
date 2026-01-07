#!/bin/bash

# ImageGuard Web Dashboard Startup Script

echo "🛡️  Starting ImageGuard Web Dashboard..."
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if we're in the correct directory
if [ ! -f "$SCRIPT_DIR/app.py" ]; then
    echo "Error: app.py not found in $SCRIPT_DIR"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
fi

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask is not installed. Installing dependencies..."
    pip install -q -r "$PROJECT_DIR/requirements.txt"
fi

# Check if Docker is accessible
if ! docker info &> /dev/null; then
    echo "⚠️  Warning: Docker is not running or not accessible."
    echo "   The web dashboard will start, but some features may not work."
    echo "   To enable full functionality:"
    echo "   - Start Docker: sudo systemctl start docker"
    echo "   - OR add your user to docker group: sudo usermod -aG docker $USER"
    echo ""
fi

# Start the Flask application
echo "Starting Flask application on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

cd "$SCRIPT_DIR"
export FLASK_APP=app.py
export FLASK_ENV=development

python3 app.py
