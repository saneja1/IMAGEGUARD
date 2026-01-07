# Base OS Images

This directory contains base operating system images pulled from Docker Hub.

## Images:
- **alpine-3.19.tar** - Alpine Linux 3.19 (lightweight, ~7MB)
- **ubuntu-22.04.tar** - Ubuntu 22.04 LTS (~30MB)
- **ubuntu-20.04.tar** - Ubuntu 20.04 LTS (~28MB)
- **redhat-ubi9-minimal.tar** - Red Hat Universal Base Image 9 Minimal (~100MB)

## Usage:
```bash
# Load an image
docker load -i alpine-3.19.tar

# List loaded images
docker images
```
