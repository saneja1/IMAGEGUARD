# ImageGuard Local Registries

Two separate Docker registries store different stages of the image pipeline.

## Registries

| Registry | Port | Purpose |
|---|---|---|
| Base OS Registry | `5050` | Raw base OS images (Ubuntu, Alpine, RedHat) |
| Certified Registry | `5051` | Built & security-scanned images |
| Registry UI | `8082` | Web browser for the certified registry |

---

## Base OS Registry — `localhost:5050`

Stores the raw base OS images that are the foundation for all ImageGuard builds.

### Start
```bash
cd /home/saneja/ImageGuard/local-registry/base-os
./start.sh
```

### Verify
```bash
curl http://localhost:5050/v2/_catalog
```

### Stop
```bash
docker stop imageguard-base-registry
```

### Data location
```
local-registry/base-os/data/
```

---

## Certified Registry — `localhost:5051`

Stores images that have been built through the ImageGuard build process. Also starts the Registry UI on `:8082`.

### Start
```bash
cd /home/saneja/ImageGuard/local-registry/certified
./start.sh
```

### Verify
```bash
curl http://localhost:5051/v2/_catalog
```

### Browse UI
Open: http://localhost:8082

### Stop
```bash
docker stop imageguard-certified-registry
docker stop imageguard-registry-ui
```

### Data location
```
local-registry/certified/data/
```

---

## Naming Convention

```
localhost:5051/imageguard/<os>-<runtime>-<components>:<version>

Examples:
  localhost:5051/imageguard/ubuntu22-python311-prometheus:v1.0
  localhost:5051/imageguard/alpine-python311-prometheus:v1.0
  localhost:5051/imageguard/redhat-python311-prometheus:v1.2
```

---

## Common Commands

### List all images in a registry
```bash
curl http://localhost:5050/v2/_catalog   # base OS
curl http://localhost:5051/v2/_catalog   # certified
```

### List tags for a specific image
```bash
curl http://localhost:5051/v2/alpine_py11_prom/tags/list
```

### View logs
```bash
docker logs imageguard-base-registry
docker logs imageguard-certified-registry
docker logs imageguard-registry-ui
```

### Check running containers
```bash
docker ps --filter "name=imageguard"
```


1. Pull base OS images (Ubuntu, RedHat, Alpine)
2. Build custom images with languages and components
3. Scan images for vulnerabilities
4. Push scanned images to this registry
5. Integrate with CI/CD pipeline
