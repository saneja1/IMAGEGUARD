# ImageGuard Web Dashboard

Flask-based web interface for managing and browsing container images in the ImageGuard platform.

## Features

- **Dashboard**: Overview of your container image inventory with statistics
- **Image Catalog**: Browse all available container images with metadata
- **Build Interface**: Configure and trigger new image builds with custom combinations
- **Security Scanner**: View security scan results and vulnerability reports

## Installation

1. **Install dependencies:**
```bash
cd /home/saneja/ImageGuard
pip install -r requirements.txt
```

2. **Ensure Docker is running:**
```bash
sudo systemctl start docker
sudo systemctl status docker
```

3. **Run the application:**
```bash
cd web
python app.py
```

Or use the startup script:
```bash
./web/start.sh
```

## Access

Once running, access the web dashboard at:
- **URL**: http://localhost:5000
- **Dashboard**: http://localhost:5000/
- **Images**: http://localhost:5000/images
- **Build**: http://localhost:5000/build
- **Security**: http://localhost:5000/security

## API Endpoints

- `GET /` - Dashboard home page
- `GET /images` - Image catalog page
- `GET /build` - Build configuration page
- `GET /security` - Security scan results page
- `GET /api/images` - JSON API for image data
- `POST /api/build` - Trigger image build (JSON)

## Configuration

The Flask app runs with the following default settings:
- **Host**: 0.0.0.0 (accessible from all interfaces)
- **Port**: 5000
- **Debug Mode**: Enabled (disable in production)

## Integration with ImageGuard Modules

This web interface integrates with:
- **Module 1**: Base Image Management - displays available base OS images
- **Module 2**: Runtime Layer Builder - shows runtime options
- **Module 3**: Component Integration - lists available components
- **Module 4**: Security Scanning Engine - displays scan results
- **Module 5**: Local Registry Manager - connects to Docker daemon

## Development

To modify the interface:
1. HTML templates are in `templates/`
2. Static CSS is embedded in `templates/base.html`
3. Python Flask routes are in `app.py`

## Next Steps

As you implement the ImageGuard modules, update the following functions in `app.py`:
- `trigger_build()` - Connect to build orchestrator
- `get_security_scans()` - Integrate with security scanner
- `get_all_images()` - Enhance with registry manager integration
