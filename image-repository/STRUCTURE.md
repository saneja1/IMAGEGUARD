# ImageGuard Repository Structure

```
/home/saneja/ImageGuard/image-repository/
├── base-os/
│   ├── alpine-3.19.tar             # Alpine Linux 3.19 (~7MB)
│   ├── ubuntu-22.04.tar            # Ubuntu 22.04 LTS (~30MB)
│   ├── ubuntu-20.04.tar            # Ubuntu 20.04 LTS (~28MB)
│   ├── redhat-ubi9-minimal.tar     # Red Hat UBI 9 Minimal (~100MB)
│   └── README.md
│
├── languages/
│   ├── python-3.9.tar              # Python 3.9 Docker image (REAL)
│   ├── python-3.10.tar             # Python 3.10 Docker image (REAL)
│   ├── python-3.11.tar             # Python 3.11 Docker image (REAL)
│   ├── java-11.mock                # OpenJDK 11 (mock)
│   ├── java-17.mock                # OpenJDK 17 LTS (mock)
│   └── README.md
│
└── components/
    ├── puppet-agent.mock           # Puppet Agent v7.28.0 (mock)
    ├── prometheus-agent.mock       # Prometheus Node Exporter v1.7.0 (mock)
    └── README.md
```

## Repository Design

### Base OS (base-os/)
Contains actual Docker images saved as tar files. These are pulled from Docker Hub and stored locally.
- 2 Ubuntu versions (20.04, 22.04)
- 1 Alpine version (3.19)
- 1 Red Hat version (UBI 9 Minimal)

### Languages (languages/)
Contains REAL Python Docker images as tar files and mock files for Java versions:
- **Python**: Real Docker images (3.9, 3.10, 3.11) saved as tar files
- **Java**: Mock files with metadata for OpenJDK 11 and 17

### Components (components/)
Mock files representing monitoring and management agents. Each file contains:
- Component details
- Configuration paths
- Dependencies
- Port requirements

## Workflow

1. **Pull** base OS images from Docker Hub
2. **Save** them as tar files in base-os/
3. **Reference** language and component mock files when building custom images
4. **Combine** OS + Language + Components to create final images
5. **Scan** final images for vulnerabilities
6. **Store** scanned images for deployment

## Example Combinations

- alpine-3.19 + python-3.11 + prometheus-agent
- ubuntu-22.04 + java-17 + puppet-agent
- ubuntu-20.04 + python-3.10 + prometheus-agent
- redhat-ubi9-minimal + python-3.9 + puppet-agent
