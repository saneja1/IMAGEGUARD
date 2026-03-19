# ImageGuard Local Registry

This is your local Docker registry for storing pre-built container images.

## Components

- **Docker Registry v2*[text](base-os/data/docker/registry/v2/blobs)*: Stores container images on port 5000
- **Registry UI**: Web interface on port 8080 to browse and manage images
- **Persistent Storage**: Images stored in `./data` directory

## Quick Start

### 1. Start the Registry
```bash
cd /home/saneja/ImageGuard/local-registry
docker-compose up -d
```

### 2. Verify Registry is Running
```bash
docker-compose ps
```

### 3. Access Web UI
Open browser: http://localhost:8080

## Using the Registry

### Pull an image from Docker Hub
```bash
docker pull alpine:latest
```

### Tag it for your local registry
```bash
docker tag alpine:latest localhost:5000/alpine:latest
```

### Push to your local registry
```bash
docker push localhost:5000/alpine:latest
```

### Pull from your local registry
```bash
docker pull localhost:5000/alpine:latest
```

### List images in your registry
```bash
curl http://localhost:5000/v2/_catalog
```

### List tags for a specific image
```bash
curl http://localhost:5000/v2/alpine/tags/list
```

## Registry Structure for ImageGuard

Recommended naming convention for your pre-built images:

```
localhost:5000/imageguard/<os>-<language>-<components>:<version>

Examples:
- localhost:5000/imageguard/ubuntu-python3.11-prometheus:v1.0
- localhost:5000/imageguard/alpine-java17-vault:v1.0
- localhost:5000/imageguard/redhat-python3.11-puppet:v1.0
```

## Management

### Stop the registry
```bash
docker-compose down
```

### Stop and remove all data
```bash
docker-compose down -v
rm -rf data/*
```

### View logs
```bash
docker-compose logs -f registry
docker-compose logs -f registry-ui
```

## Features Enabled

- ✅ Image deletion (via UI and API)
- ✅ Persistent storage
- ✅ Web UI for browsing
- ✅ RESTful API on port 5000
- ✅ Automatic restart on system reboot

## Next Steps

1. Pull base OS images (Ubuntu, RedHat, Alpine)
2. Build custom images with languages and components
3. Scan images for vulnerabilities
4. Push scanned images to this registry
5. Integrate with CI/CD pipeline
