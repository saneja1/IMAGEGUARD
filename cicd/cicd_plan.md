# IMAGEGUARD CI/CD FLOW - COMPLETE ARCHITECTURE
## Using Docker Hub Registry

================================================================================
## PHASE 1: ImageGuard Creates Certified Base Images (Pre-Build Phase)
================================================================================

### Components Selection:

```
+----------------+      +----------------+      +----------------+
|   Base OS      |      |   Runtime      |      |  Components    |
|                |      |                |      |                |
|  Ubuntu 20     |  +   |  Python 3.10   |  +   |  Prometheus    |
|  Ubuntu 22     |      |  Python 3.11   |      |  Agent         |
|  RedHat UBI9   |      |  Java 11/17    |      |                |
|  Alpine 3.19   |      |                |      |                |
+----------------+      +----------------+      +----------------+
        |                      |                      |
        +----------------------+----------------------+
                               |
                               v
```

### ImageGuard Build Pipeline:

```
                    +----------------------+
                    |   Flask Web App      |
                    |   (ImageGuard UI)    |
                    |  http://localhost    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  Docker Build        |
                    |  - Combine layers    |
                    |  - Add metadata      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  Security Scan       |
                    |  (Trivy)             |
                    |  - CVE detection     |
                    |  - Vulnerability     |
                    |    assessment        |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  Push to Local Repo  |
                    |  localhost:5051      |
                    +----------+-----------+
                               |
                               v
```

### ✅ CERTIFIED BASE IMAGES (Ready for Distribution):

- `localhost:5051/cf_ub20_py310_prom:v1`
- `localhost:5051/cf_redhat_ubi9_py311:v1`
- `localhost:5051/cf_alpine319_py310:v1`
- `localhost:5051/cf_ub22_py311_prom:v1`


================================================================================
## PHASE 2: Sync to Docker Hub (Public/Private Registry)
================================================================================

### Commands to Sync Images:

```bash
# Login to Docker Hub
docker login
Username: yourname
Password: ********

# Tag for Docker Hub
docker tag localhost:5051/cf_ub20_py310_prom:v1 \
    yourname/cf_ub20_py310_prom:v1

# Push to Docker Hub
docker push yourname/cf_ub20_py310_prom:v1
docker push yourname/cf_redhat_ubi9_py311:v1
docker push yourname/cf_alpine319_py310:v1
docker push yourname/cf_ub22_py311_prom:v1
```

### 🐳 DOCKER HUB (hub.docker.com)

**Images Available:**
- `yourname/cf_ub20_py310_prom:v1`
- `yourname/cf_redhat_ubi9_py311:v1`
- `yourname/cf_alpine319_py310:v1`
- `yourname/cf_ub22_py311_prom:v1`

**Benefits:**
- ✅ FREE: Public repos (unlimited)
- 💰 $5/mo: Private repos (unlimited)
- ✅ Accessible from anywhere (K8s nodes)

                                      │
                                      │

================================================================================
## PHASE 3: Developers Build Their Apps Using Your Certified Base
================================================================================

### Developer's Project Structure:

```
my-app/
├── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

### Sample Dockerfile (Using YOUR Certified Base):

```dockerfile
# Use ImageGuard certified base image
FROM yourname/cf_ub20_py310_prom:v1    # <-- YOUR BASE IMAGE!

WORKDIR /app
COPY app.py /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt
CMD ["python", "/app/app.py"]
```

### Sample app.py:

```python
print("Hello from my app!")
# Developer's business logic
```

### Developer Workflow:

```
                    +----------------------+
                    |  git add .           |
                    |  git commit -m "..." |
                    |  git push origin main|
                    +----------+-----------+

================================================================================
## PHASE 4: CI Pipeline (Continuous Integration - Build & Test)
================================================================================

```
                    +----------------------+
                    |  Jenkins Server      |
                    |  (Automation)        |
                    +----------+-----------+
                               |
                               v
```

### Step 1: Detect Code Change
- GitHub webhook notifies Jenkins
- Jenkins pulls latest code from repository

```bash
git clone https://github.com/user/my-app
```

### Step 2: Pull Dockerfile + Application Code
Files retrieved:
- `Dockerfile` (references YOUR certified base from Docker Hub)
- `app.py` (developer's code)
- `requirements.txt`

### Step 3: Docker Build

```bash
docker build -t my-final-app:v1 .
```

**Image Layers:**
```
+------------------------------------------+
|  Layer 1: yourname/cf_ub20_py310_prom   | <-- YOUR BASE (FROM DOCKER HUB)
|           (OS + Python + Prometheus)     |
+------------------------------------------+
|  Layer 2: Developer's app.py             | <-- THEIR CODE
+------------------------------------------+
|  Layer 3: Dependencies installed         |
+------------------------------------------+
```

**Result:** `my-final-app:v1` ✅

### Step 4: Security Scan (Optional but Recommended)

```bash
trivy image my-final-app:v1
```
- Verify still secure
- Check for new vulnerabilities in app dependencies
- Fail build if critical issues found

### Step 5: Tag Image for Docker Hub

```bash
docker tag my-final-app:v1 yourname/my-final-app:v1
```

### Step 6: Push to Docker Hub

```bash
docker login
docker push yourname/my-final-app:v1
```

✅ **Final app image ready for deployment!**

```
                    +----------------------+
                    | 🐳 DOCKER HUB        |
                    | Final Image:         |
                    | yourname/            |
                    | my-final-app:v1      |
                    +----------+-----------+
                               |
                               v

================================================================================
## PHASE 5: CD Pipeline (Continuous Deployment - Deploy to Kubernetes)
================================================================================

### Method A: Direct kubectl command

```bash
kubectl set image deployment/myapp \
    myapp=yourname/my-final-app:v1
```

### Method B: Apply deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: myapp
        image: yourname/my-final-app:v1    # <-- FROM DOCKER HUB
        ports:
        - containerPort: 8080
```

```bash
kubectl apply -f deployment.yaml
```

### Kubernetes Deployment Flow:

```
                    +----------------------+
                    | Kubernetes Cluster   |
                    | (Manual VMs)         |
                    | VM1, VM2, VM3        |
                    +----------+-----------+
                               |
                K8s nodes pull image from Docker Hub
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
+---------------+      +---------------+      +---------------+
|   Pod 1       |      |   Pod 2       |      |   Pod 3       |
|   Running     |      |   Running     |      |   Running     |
|               |      |               |      |               |
| my-final-app  |      | my-final-app  |      | my-final-app  |
| :v1           |      | :v1           |      | :v1           |
+---------------+      +---------------+      +---------------+
```

### Rolling Update Process:
1. Old version running → K8s nodes pull new image from Docker Hub
2. Creates new pods with `yourname/my-final-app:v1`
3. Gradually replaces old pods
4. Zero downtime deployment ✅

### Docker Hub Authentication (for private repos):

```bash
# Create Kubernetes secret for Docker Hub
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \

================================================================================
## 🎯 KEY BENEFITS
================================================================================

✅ **SECURITY**
   - Developers MUST use pre-scanned base images (enforce with policy)

✅ **SPEED**
   - Developers don't build from scratch, just add their code
   - Build time: Seconds instead of minutes

✅ **COMPLIANCE**
   - All production apps use certified components
   - Audit trail: Know exactly what's in every image

✅ **CONSISTENCY**
   - Standardized base across all teams

✅ **AUTOMATION**
   - Fully automated pipeline from code push to deployment

✅ **COST**
   - FREE with public repos, or $5/month for unlimited private repos
   - No GCR costs, works perfectly with manual K8s VMs


================================================================================
## 💰 DOCKER HUB PRICING COMPARISON
================================================================================

### FREE TIER:
- Unlimited public repositories
- 1 private repository
- 200 container pulls per 6 hours
- **Perfect for:** Certified base images (make them public!)

### PRO ($5/month):
- Unlimited private repositories
- 5,000 container pulls per day
- **Perfect for:** Private certified bases + app images

### TEAM ($7/user/month):
- Everything in Pro
- Team collaboration features
- **Perfect for:** Multiple developers/teams


================================================================================
## 📦 FILES TO CREATE
================================================================================

1. **sync-to-dockerhub.sh** → Script to push certified images to Docker Hub

2. **Jenkinsfile** → CI/CD pipeline automation configuration

3. **deployment.yaml** → Kubernetes deployment configuration

4. **dockerhub-secret.yaml** → K8s secret for Docker Hub authentication

5. **sample-app/** → Example app showing how developers use your bases
   - app.py
   - Dockerfile
   - requirements.txt

6. **README-CICD.md** → Setup and usage instructions


================================================================================
## 🔧 QUICK SETUP FOR DOCKER HUB
================================================================================

### Step 1: Create Docker Hub account
Visit: https://hub.docker.com

### Step 2: Login on your machine
```bash
docker login
```

### Step 3: Push your certified images
```bash
docker tag localhost:5051/cf_ub20_py310_prom:v1 yourname/cf_ub20_py310_prom:v1
docker push yourname/cf_ub20_py310_prom:v1
```

### Step 4: Configure K8s to pull from Docker Hub
```bash
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=yourname \
  --docker-password=yourpassword
```

### Step 5: Use in deployments
```yaml
image: yourname/my-final-app:v1
imagePullSecrets:
- name: dockerhub-secret
```

================================================================================
                         🔧 QUICK SETUP FOR DOCKER HUB
═════════════════════════════════════════════════════════════════════════════════════════

  Step 1: Create Docker Hub account at hub.docker.com
  
  Step 2: Login on your machine
    docker login
  
  Step 3: Push your certified images
    docker tag localhost:5051/cf_ub20_py310_prom:v1 yourname/cf_ub20_py310_prom:v1
    docker push yourname/cf_ub20_py310_prom:v1
  
  Step 4: Configure K8s to pull from Docker Hub
    kubectl create secret docker-registry dockerhub-secret \
      --docker-server=https://index.docker.io/v1/ \
      --docker-username=yourname \
      --docker-password=yourpassword
  
  Step 5: Use in deployments
    image: yourname/my-final-app:v1
    imagePullSecrets:
    - name: dockerhub-secret

═════════════════════════════════════════════════════════════════════════════════════════