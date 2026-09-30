#!/bin/bash
# ImageGuard Web Dashboard — Usage: ./web/start.sh [start|stop|restart|status]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/venv/flask.pid"
CMD="${1:-start}"

case "$CMD" in
  status)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
      echo "✓ Flask dashboard is RUNNING (port 5000) — PID $(cat $PID_FILE)"
    else
      echo "✗ Flask dashboard is NOT running"
    fi
    ;;
  stop)
    if [ -f "$PID_FILE" ]; then
      kill "$(cat $PID_FILE)" 2>/dev/null && echo "✓ Flask dashboard stopped"
      rm -f "$PID_FILE"
    else
      pkill -f "python3.*app.py" && echo "✓ Flask dashboard stopped" || echo "Not running"
    fi
    ;;
  restart)
    $0 stop
    sleep 1
    $0 start
    ;;
  start)
    echo "Starting ImageGuard Web Dashboard..."

    if [ ! -f "$SCRIPT_DIR/app.py" ]; then
      echo "Error: app.py not found in $SCRIPT_DIR"; exit 1
    fi

    if ! command -v python3 &> /dev/null; then
      echo "Error: Python 3 is not installed."; exit 1
    fi

    if [ ! -d "$PROJECT_DIR/venv" ]; then
      echo "Creating virtual environment..."
      python3 -m venv "$PROJECT_DIR/venv"
    fi

    source "$PROJECT_DIR/venv/bin/activate"

    if ! python3 -c "import flask" 2>/dev/null; then
      echo "Installing dependencies..."
      pip install -q -r "$PROJECT_DIR/requirements.txt"
    fi

    if ! docker info &> /dev/null; then
      echo "⚠️  Warning: Docker not accessible. Some features may not work."
    fi

    cd "$SCRIPT_DIR"
    export FLASK_APP=app.py
    export FLASK_ENV=development

    echo "Starting Flask on http://localhost:5000"
    echo "Press Ctrl+C to stop"
    echo ""

    python3 app.py &
    echo $! > "$PID_FILE"
    wait
    ;;
  *)
    echo "Usage: ./web/start.sh [start|stop|restart|status]"
    exit 1
    ;;
esac
