"""
ImageGuard Web Dashboard
Flask application for managing and browsing container images
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import docker
import os
import json
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SECRET_KEY'] = 'imageguard-secret-key-change-in-production'

# Initialize Docker client
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"Warning: Could not connect to Docker: {e}")
    docker_client = None


def format_size(bytes_size):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def format_date(date_str):
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except:
        return date_str


@app.route('/')
def index():
    """Dashboard home page"""
    stats = get_dashboard_stats()
    return render_template('index.html', stats=stats)


@app.route('/images')
def images():
    """Image catalog page"""
    image_list = get_all_images()
    stats = get_dashboard_stats()
    return render_template('images.html', images=image_list, stats=stats)


@app.route('/build')
def build():
    """Build configuration page"""
    base_images = get_base_images()
    runtimes = get_available_runtimes()
    components = get_available_components()
    return render_template('build.html', 
                         base_images=base_images,
                         runtimes=runtimes,
                         components=components)


@app.route('/custom')
def custom():
    """Custom vendor images page"""
    return render_template('custom.html')


@app.route('/about')
def about():
    """Documentation and about page"""
    return render_template('about.html')


@app.route('/image/<path:image_name>/<tag>')
def image_details(image_name, tag):
    """Image details page"""
    import requests
    from datetime import datetime
    
    try:
        # Get manifest to get digest and other details
        manifest_response = requests.get(
            f'http://localhost:5051/v2/{image_name}/manifests/{tag}',
            headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
        )
        
        # Try to pull image info from local Docker
        full_image = f"localhost:5051/{image_name}:{tag}"
        image_info = None
        if docker_client:
            try:
                img = docker_client.images.get(full_image)
                image_info = img
            except:
                pass
        
        # Detect tags
        name_lower = image_name.lower()
        tag_lower = tag.lower()
        tags = []
        tag_colors = {
            'ubuntu': '#E95420', 'alpine': '#0D597F', 'redhat': '#EE0000',
            'python': '#3776AB', 'java': '#007396', 'nodejs': '#339933',
            'go': '#00ADD8', 'prometheus': '#E6522C', 'tenable': '#00B388',
            'nessus': '#00B388', 'oracle': '#F80000', 'debian': '#A81D33'
        }
        
        for key, color in tag_colors.items():
            # Check in both image name and tag
            if key in name_lower or key in tag_lower:
                tags.append({'name': key, 'color': color})
            # Special checks
            elif key == 'python' and ('py3' in name_lower or 'py2' in name_lower or 'py3' in tag_lower):
                tags.append({'name': key, 'color': color})
            elif key == 'ubuntu' and ('ub20' in name_lower or 'ub22' in name_lower or 'ub' in tag_lower):
                tags.append({'name': key, 'color': color})
        
        # Get OS info
        os_name = "Linux"
        if 'alpine' in name_lower:
            os_name = "Alpine Linux"
        elif 'ubuntu' in name_lower or 'ub20' in name_lower or 'ub22' in name_lower or 'ubuntu' in tag_lower:
            os_name = "Ubuntu Linux"
        elif 'redhat' in name_lower or 'ubi' in name_lower:
            os_name = "Red Hat Enterprise Linux"
        elif 'oracle' in name_lower or 'oracle' in tag_lower:
            os_name = "Oracle Linux"
        elif 'debian' in name_lower or 'debian' in tag_lower:
            os_name = "Debian Linux"
        elif 'nessus' in name_lower:
            os_name = "Tenable Nessus Security Scanner"
        
        # Get icon
        icon = '📦'
        if 'alpine' in name_lower:
            icon = '🏔️'
        elif 'ubuntu' in name_lower or 'ub' in name_lower or 'ubuntu' in tag_lower:
            icon = '🟧'
        elif 'redhat' in name_lower:
            icon = '🔴'
        elif 'nessus' in name_lower or 'tenable' in name_lower:
            icon = '🔒'
        elif 'oracle' in name_lower or 'oracle' in tag_lower:
            icon = '🔴'
        
        # Build image data
        image_data = {
            'name': image_name,
            'tag': tag,
            'registry': 'localhost:5051',
            'icon': icon,
            'description': f'Production-ready {os_name} container image',
            'tags': tags,
            'os': os_name,
            'architecture': 'amd64',
            'id': image_info.short_id.replace('sha256:', '') if image_info else 'N/A',
            'digest': manifest_response.headers.get('Docker-Content-Digest', 'N/A') if manifest_response.status_code == 200 else 'N/A',
            'size': format_size(image_info.attrs['Size']) if image_info else 'N/A',
            'runnable_size': format_size(image_info.attrs['Size']) if image_info else 'N/A',
            'created': format_date(image_info.attrs['Created']) if image_info else 'Recently',
            'vulnerabilities': {
                'total': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        return render_template('image_details.html', image=image_data)
    
    except Exception as e:
        print(f"Error fetching image details: {e}")
        return f"Error loading image details: {str(e)}", 404


@app.route('/image/<path:image_name>/tags')
def image_tags(image_name):
    """Show all tags for an image"""
    import requests
    
    try:
        # Get tags from registry
        tags_response = requests.get(f'http://localhost:5051/v2/{image_name}/tags/list')
        tags_data = tags_response.json()
        tags = tags_data.get('tags', [])
        
        # Sort tags in reverse order (newer first)
        tags.sort(reverse=True)
        
        # Detect icon
        name_lower = image_name.lower()
        icon = '📦'
        if 'alpine' in name_lower:
            icon = '🏔️'
        elif 'ubuntu' in name_lower or 'ub' in name_lower:
            icon = '🟧'
        elif 'redhat' in name_lower:
            icon = '🔴'
        
        tags_list = [{'tag': tag} for tag in tags]
        
        return render_template('image_tags.html', 
                             image_name=image_name, 
                             tags=tags_list,
                             icon=icon)
    
    except Exception as e:
        print(f"Error fetching tags: {e}")
        return f"Error loading tags: {str(e)}", 404


@app.route('/api/certified-images')
def get_certified_images():
    """Get images from certified registry"""
    import requests
    try:
        # Get catalog from certified registry
        response = requests.get('http://localhost:5051/v2/_catalog')
        catalog = response.json()
        
        images = []
        for repo in catalog.get('repositories', []):
            # Get tags for each repository
            tags_response = requests.get(f'http://localhost:5051/v2/{repo}/tags/list')
            tags_data = tags_response.json()
            
            for tag in tags_data.get('tags', []):
                images.append({
                    'name': repo,
                    'tag': tag,
                    'full_name': f"{repo}:{tag}",
                    'registry': 'localhost:5051'
                })
        
        return jsonify(images)
    except Exception as e:
        print(f"Error fetching certified images: {e}")
        return jsonify([])


@app.route('/api/certified-images-grouped')
def get_certified_images_grouped():
    """Get grouped images from certified registry (by name)"""
    import requests
    try:
        # Get catalog from certified registry
        response = requests.get('http://localhost:5051/v2/_catalog')
        catalog = response.json()
        
        grouped_images = []
        for repo in catalog.get('repositories', []):
            # Get tags count for each repository
            tags_response = requests.get(f'http://localhost:5051/v2/{repo}/tags/list')
            tags_data = tags_response.json()
            tags = tags_data.get('tags', [])
            
            grouped_images.append({
                'name': repo,
                'tag_count': len(tags),
                'tags': tags,
                'registry': 'localhost:5051'
            })
        
        return jsonify(grouped_images)
    except Exception as e:
        print(f"Error fetching grouped images: {e}")
        return jsonify([])


@app.route('/api/fetch-vendor-images', methods=['POST'])
def fetch_vendor_images():
    """Fetch available images from Docker Hub"""
    import requests
    
    data = request.json
    docker_hub_url = data.get('dockerHubUrl', '').strip()
    display_name = data.get('displayName', '').strip()
    
    if not docker_hub_url:
        return jsonify({
            'status': 'error',
            'message': 'Docker Hub URL is required'
        }), 400
    
    try:
        # Parse Docker Hub URL - handle both web URLs and simple format
        # Web URL format: https://hub.docker.com/r/username/repository
        # Simple format: username/repository or just repository
        
        if 'hub.docker.com' in docker_hub_url:
            # Extract from web URL
            parts = docker_hub_url.split('/')
            # Find the index after 'r' or '_' in the URL
            if '/r/' in docker_hub_url:
                r_index = parts.index('r')
                namespace = parts[r_index + 1]
                repository = parts[r_index + 2] if len(parts) > r_index + 2 else parts[r_index + 1]
            elif '/_/' in docker_hub_url:
                # Official image
                underscore_index = parts.index('_')
                namespace = 'library'
                repository = parts[underscore_index + 1] if len(parts) > underscore_index + 1 else parts[-1]
            else:
                # Try to extract last part
                namespace = parts[-2] if len(parts) >= 2 else 'library'
                repository = parts[-1]
        else:
            # Simple format
            parts = docker_hub_url.split('/')
            
            if len(parts) == 1:
                # Official image (e.g., redis, postgres)
                namespace = 'library'
                repository = parts[0]
            else:
                # User image (e.g., prom/prometheus)
                namespace = parts[0]
                repository = parts[1]
        
        # Fetch tags from Docker Hub API
        api_url = f'https://registry.hub.docker.com/v2/repositories/{namespace}/{repository}/tags'
        response = requests.get(api_url, params={'page_size': 50})
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'Failed to fetch images from Docker Hub. Status: {response.status_code}'
            }), 400
        
        data = response.json()
        results = data.get('results', [])
        
        # Format images with OS detection
        images = []
        for result in results:
            tag_name = result.get('name', 'latest')
            
            # Detect OS from tag name
            tag_lower = tag_name.lower()
            os_name = 'Linux'
            if 'alpine' in tag_lower:
                os_name = 'Alpine'
            elif 'ubuntu' in tag_lower or 'jammy' in tag_lower or 'focal' in tag_lower:
                os_name = 'Ubuntu'
            elif 'debian' in tag_lower or 'bullseye' in tag_lower or 'bookworm' in tag_lower:
                os_name = 'Debian'
            elif 'centos' in tag_lower:
                os_name = 'CentOS'
            elif 'rhel' in tag_lower or 'ubi' in tag_lower:
                os_name = 'Red Hat'
            elif 'oracle' in tag_lower:
                os_name = 'Oracle'
            
            # Extract date from tag (format: YYYYMMDD)
            import re
            date_match = re.search(r'(\d{8})(?!\d)', tag_name)
            date_str = None
            if date_match:
                date_raw = date_match.group(1)
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(date_raw, '%Y%m%d')
                    date_str = date_obj.strftime('%d %b %Y')
                except:
                    date_str = None
            
            images.append({
                'name': f'{namespace}/{repository}' if namespace != 'library' else repository,
                'tag': tag_name,
                'os': os_name,
                'date': date_str,
                'full_name': f'{docker_hub_url}:{tag_name}'
            })
        
        return jsonify({
            'status': 'success',
            'images': images,
            'count': len(images)
        })
    
    except Exception as e:
        print(f"Error fetching vendor images: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/download-vendor-images', methods=['POST'])
def download_vendor_images():
    """Download vendor images from Docker Hub and push to base OS registry"""
    data = request.json
    images = data.get('images', [])
    
    if not docker_client:
        return jsonify({
            'status': 'error',
            'message': 'Docker client not available'
        }), 500
    
    if not images:
        return jsonify({
            'status': 'error',
            'message': 'No images provided'
        }), 400
    
    try:
        downloaded = 0
        failed = []
        
        for img in images:
            image_name = img.get('name')
            tag = img.get('tag', 'latest')
            full_name = f"{image_name}:{tag}"
            
            try:
                print(f"Pulling image from Docker Hub: {full_name}")
                # Pull from Docker Hub
                pulled_image = docker_client.images.pull(image_name, tag=tag)
                
                # Tag for base OS registry (localhost:5050)
                # Use just the repository name without namespace for local registry
                repo_parts = image_name.split('/')
                local_repo_name = repo_parts[-1] if len(repo_parts) > 1 else image_name
                registry_tag = f"localhost:5050/{local_repo_name}:{tag}"
                
                pulled_image.tag(registry_tag)
                print(f"Tagged image as: {registry_tag}")
                
                # Push to base OS registry (without authentication)
                print(f"Pushing to base OS registry: {registry_tag}")
                for line in docker_client.images.push(registry_tag, stream=True, decode=True):
                    if 'error' in line:
                        raise Exception(line['error'])
                    print(line)
                
                # Remove local copies after successful push
                try:
                    docker_client.images.remove(full_name, force=True)
                    print(f"Removed local image: {full_name}")
                except:
                    pass  # Ignore if already removed
                
                try:
                    docker_client.images.remove(registry_tag, force=True)
                    print(f"Removed local tagged image: {registry_tag}")
                except:
                    pass  # Ignore if already removed
                
                downloaded += 1
                print(f"Successfully pushed {registry_tag} to base OS registry")
            except Exception as e:
                error_msg = str(e)
                print(f"Failed to process {full_name}: {error_msg}")
                failed.append(f"{full_name} - {error_msg}")
        
        if downloaded > 0:
            message = f"Downloaded and pushed {downloaded} image(s) to base OS registry (localhost:5050)"
            if failed:
                message += f"\n\nFailed to process {len(failed)} image(s):\n" + "\n".join(failed)
            
            return jsonify({
                'status': 'success',
                'downloaded': downloaded,
                'failed': len(failed),
                'message': message
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Failed to download any images. Errors: {"; ".join(failed)}'
            }), 500
    
    except Exception as e:
        print(f"Error downloading images: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/build', methods=['POST'])
def trigger_build():
    """API endpoint to trigger image build"""
    data = request.json
    
    if not docker_client:
        return jsonify({
            'status': 'error',
            'message': 'Docker client not available. Please check Docker connection.'
        }), 500
    
    try:
        # Get runtime, default to None if empty
        runtime = data.get('runtime', '') or None
        
        # Generate Dockerfile content
        dockerfile_content = generate_dockerfile(
            data['baseImage'],
            runtime,
            data['components'],
            data['imageName'],
            data['imageTag']
        )
        
        # Build the image
        image_tag = f"{data['imageName']}:{data['imageTag']}"
        
        # Create a temporary directory for build context
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dockerfile_path = os.path.join(tmpdir, 'Dockerfile')
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            # Build the image
            print(f"Building image: {image_tag}")
            image, build_logs = docker_client.images.build(
                path=tmpdir,
                tag=image_tag,
                rm=True,
                forcerm=True
            )
            
            # Collect build logs
            logs = []
            for log in build_logs:
                if 'stream' in log:
                    logs.append(log['stream'].strip())
                    print(log['stream'].strip())
            
            # Perform security scan
            scan_result = perform_security_scan(image_tag)
            
            # Update image with security scan metadata using a new Dockerfile layer
            # Create a new Dockerfile that adds labels to the scanned image
            with tempfile.TemporaryDirectory() as tmpdir2:
                label_dockerfile = f"""FROM {image_tag}
LABEL imageguard.security_status="{scan_result['status']}"
LABEL imageguard.build_status="success"
LABEL imageguard.build_time="{datetime.now(timezone.utc).isoformat()}"
LABEL imageguard.vulnerabilities.critical="{scan_result['vulnerabilities']['critical']}"
LABEL imageguard.vulnerabilities.high="{scan_result['vulnerabilities']['high']}"
LABEL imageguard.vulnerabilities.medium="{scan_result['vulnerabilities']['medium']}"
LABEL imageguard.vulnerabilities.low="{scan_result['vulnerabilities']['low']}"
"""
                label_dockerfile_path = os.path.join(tmpdir2, 'Dockerfile')
                with open(label_dockerfile_path, 'w') as f:
                    f.write(label_dockerfile)
                
                # Rebuild with labels (this just adds metadata, no size increase)
                docker_client.images.build(
                    path=tmpdir2,
                    tag=image_tag,
                    rm=True,
                    forcerm=True
                )
            
            return jsonify({
                'status': 'success',
                'message': f'Image {image_tag} built successfully! Use "Sync to Certified Docker Hub" to push to registry.',
                'image_id': image.short_id,
                'config': data,
                'logs': logs[-20:],  # Last 20 log lines
                'security_scan': scan_result,
                'dockerfile': dockerfile_content
            })
    
    except Exception as e:
        print(f"Build error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Build failed: {str(e)}',
            'config': data
        }), 500


@app.route('/api/build-vendor', methods=['POST'])
def trigger_vendor_build():
    """API endpoint to trigger vendor image build (no runtime)"""
    data = request.json
    
    if not docker_client:
        return jsonify({
            'status': 'error',
            'message': 'Docker client not available. Please check Docker connection.'
        }), 500
    
    try:
        # Generate Dockerfile content for vendor image (without runtime)
        dockerfile_content = generate_vendor_dockerfile(
            data['baseImage'],
            data['components'],
            data['imageName'],
            data['imageTag']
        )
        
        # Build the image
        image_tag = f"{data['imageName']}:{data['imageTag']}"
        
        # Create a temporary directory for build context
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dockerfile_path = os.path.join(tmpdir, 'Dockerfile')
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            # Build the image
            print(f"Building vendor image: {image_tag}")
            image, build_logs = docker_client.images.build(
                path=tmpdir,
                tag=image_tag,
                rm=True,
                forcerm=True
            )
            
            # Collect build logs
            logs = []
            for log in build_logs:
                if 'stream' in log:
                    logs.append(log['stream'].strip())
                    print(log['stream'].strip())
            
            # Perform security scan (mock - always passes)
            scan_result = perform_security_scan(image_tag)
            
            return jsonify({
                'status': 'success',
                'message': f'Vendor image {image_tag} built successfully! Use "Sync to Certified Docker Hub" to push to registry.',
                'image_id': image.short_id,
                'config': data,
                'logs': logs[-20:],  # Last 20 log lines
                'security_scan': scan_result,
                'dockerfile': dockerfile_content
            })
    
    except Exception as e:
        print(f"Vendor build error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Vendor build failed: {str(e)}',
            'config': data
        }), 500


@app.route('/api/build-history')
def get_build_history():
    """Get history of images built through ImageGuard"""
    if not docker_client:
        return jsonify([])
    
    try:
        all_images = docker_client.images.list()
        build_history = []
        
        # Exact base image tags to exclude
        base_image_tags = [
            'localhost:5050/alpine:3.19',
            'localhost:5050/ubuntu:22.04',
            'localhost:5050/ubuntu:20.04',
            'localhost:5050/redhat/ubi9-minimal:latest',
            'alpine:3.19',
            'ubuntu:22.04',
            'ubuntu:20.04',
            'redhat/ubi9-minimal:latest'
        ]
        
        for img in all_images:
            # Skip images without tags
            if not img.tags:
                continue
            
            # Skip exact base images
            if img.tags[0] in base_image_tags:
                continue
            
            # Skip registry infrastructure images
            if any(x in img.tags[0].lower() for x in ['registry', 'joxit', 'docker-registry-ui']):
                continue
            
            # Parse image name and tag
            image_full = img.tags[0] if img.tags else img.short_id
            image_parts = image_full.split(':')
            image_name = image_parts[0]
            image_tag = image_parts[1] if len(image_parts) > 1 else 'latest'
            
            # Get metadata from labels or defaults
            labels = img.labels or {}
            base_os = labels.get('imageguard.base', 'unknown')
            runtime = labels.get('imageguard.runtime', 'unknown')
            build_status = labels.get('imageguard.build_status', 'built')
            security_status = labels.get('imageguard.security_status', 'passed')
            build_time = labels.get('imageguard.build_time', img.attrs['Created'])
            
            build_history.append({
                'name': image_name,
                'tag': image_tag,
                'base_os': base_os,
                'runtime': runtime,
                'build_status': build_status,
                'security_status': security_status,
                'created': build_time,
                'size': img.attrs['Size']
            })
        
        # Sort by creation time (most recent first)
        build_history.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify(build_history)
    
    except Exception as e:
        print(f"Error getting build history: {e}")
        return jsonify([])


@app.route('/api/security-scan/<path:image_tag>')
def get_security_scan(image_tag):
    """Get security scan details for a specific image"""
    # Mock security scan details
    scan_result = perform_security_scan(image_tag)
    return jsonify(scan_result)


@app.route('/api/dockerfile/<path:image_tag>')
def get_dockerfile(image_tag):
    """Get Dockerfile content for a specific image"""
    if not docker_client:
        return jsonify({'error': 'Docker client not available'}), 500
    
    try:
        # Try to get the image
        image = docker_client.images.get(image_tag)
        labels = image.labels or {}
        
        # Reconstruct Dockerfile from labels if available
        base = labels.get('imageguard.base', 'unknown')
        runtime = labels.get('imageguard.runtime', 'unknown')
        components = labels.get('imageguard.components', '').split(',') if labels.get('imageguard.components') else []
        
        # Parse image name and tag from image_tag
        parts = image_tag.split(':')
        name = parts[0]
        tag = parts[1] if len(parts) > 1 else 'latest'
        
        # Regenerate Dockerfile
        if base != 'unknown' and runtime != 'unknown':
            dockerfile_content = generate_dockerfile(base, runtime, components, name, tag)
        else:
            # Fallback if labels not found
            dockerfile_content = f"""# Dockerfile for {image_tag}
# Build metadata not available
# This image was not built through ImageGuard or labels were not set

FROM {image.tags[0] if image.tags else 'unknown'}

# Image created: {image.attrs['Created']}
# Image ID: {image.short_id}
"""
        
        return jsonify({'dockerfile': dockerfile_content})
    
    except Exception as e:
        print(f"Error getting Dockerfile: {e}")
        return jsonify({'error': str(e)}), 404


@app.route('/api/sync-dockerhub', methods=['POST'])
def sync_dockerhub():
    """Sync built images to certified registry"""
    
    if not docker_client:
        return jsonify({
            'status': 'error',
            'message': 'Docker client not available'
        }), 500
    
    try:
        # Get all built images
        all_images = docker_client.images.list()
        # Skip exact base images and infrastructure images
        exact_skip_tags = ['alpine:3.19', 'ubuntu:22.04', 'ubuntu:20.04', 'redhat/ubi9-minimal:latest']
        skip_patterns = ['localhost:5050/', 'localhost:5051/', 'registry:', 'joxit/', 'docker-registry-ui']
        
        synced_count = 0
        synced_images = []
        failed_images = []
        
        for img in all_images:
            if not img.tags:
                continue
            
            # Skip unwanted images
            image_tag = img.tags[0]
            
            # Skip exact base images
            if image_tag in exact_skip_tags:
                continue
            
            # Skip infrastructure images and already synced images
            should_skip = any(pattern in image_tag.lower() for pattern in skip_patterns)
            if should_skip:
                continue
            
            # Push to certified registry
            try:
                result = push_to_certified_registry(image_tag)
                if result['status'] == 'success':
                    synced_count += 1
                    synced_images.append(image_tag)
                else:
                    failed_images.append(image_tag)
            except Exception as e:
                print(f"Failed to sync {image_tag}: {e}")
                failed_images.append(image_tag)
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully synced {synced_count} images to certified registry',
            'synced_count': synced_count,
            'synced_images': synced_images,
            'failed_images': failed_images
        })
    
    except Exception as e:
        print(f"Sync error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def push_to_certified_registry(image_tag):
    """Push built image to certified registry"""
    try:
        # Tag image for certified registry
        registry_tag = f"localhost:5051/{image_tag}"
        
        # Get the image
        image = docker_client.images.get(image_tag)
        
        # Tag it
        image.tag(registry_tag)
        print(f"Tagged {image_tag} as {registry_tag}")
        
        # Push to registry
        push_logs = []
        for line in docker_client.images.push(registry_tag, stream=True, decode=True):
            if 'status' in line:
                push_logs.append(line['status'])
                print(line['status'])
        
        return {
            'status': 'success',
            'registry': 'localhost:5051',
            'image': registry_tag,
            'message': f'Pushed to certified registry as {registry_tag}'
        }
    
    except Exception as e:
        print(f"Push error: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


def perform_security_scan(image_tag):
    """Perform security scan on built image using Trivy"""
    import subprocess
    import json
    
    try:
        # Run Trivy scan with JSON output
        result = subprocess.run(
            ['trivy', 'image', '--format', 'json', '--quiet', image_tag],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"Trivy scan failed: {result.stderr}")
            return {
                'status': 'error',
                'image': image_tag,
                'vulnerabilities': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                },
                'scanned_at': datetime.now(timezone.utc).isoformat(),
                'scanner': 'Trivy (error)',
                'error': 'Scan failed'
            }
        
        # Parse JSON output
        scan_data = json.loads(result.stdout)
        
        # Count vulnerabilities by severity and collect details
        vuln_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'unknown': 0
        }
        
        # Detailed vulnerability list
        detailed_vulns = []
        
        # Extract vulnerabilities from all results
        for result_item in scan_data.get('Results', []):
            target = result_item.get('Target', 'unknown')
            vulnerabilities = result_item.get('Vulnerabilities', [])
            if vulnerabilities:
                for vuln in vulnerabilities:
                    severity = vuln.get('Severity', 'UNKNOWN').lower()
                    if severity in vuln_counts:
                        vuln_counts[severity] += 1
                    else:
                        vuln_counts['unknown'] += 1
                    
                    # Collect detailed information
                    detailed_vulns.append({
                        'vulnerability_id': vuln.get('VulnerabilityID', 'N/A'),
                        'package_name': vuln.get('PkgName', 'N/A'),
                        'installed_version': vuln.get('InstalledVersion', 'N/A'),
                        'fixed_version': vuln.get('FixedVersion', 'Not available'),
                        'severity': vuln.get('Severity', 'UNKNOWN'),
                        'title': vuln.get('Title', 'No title'),
                        'description': vuln.get('Description', 'No description')[:200] + '...' if len(vuln.get('Description', '')) > 200 else vuln.get('Description', ''),
                        'target': target
                    })
        
        # Sort vulnerabilities by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4}
        detailed_vulns.sort(key=lambda x: severity_order.get(x['severity'], 5))
        
        # Determine overall status
        total_vulns = sum(vuln_counts.values())
        if vuln_counts['critical'] > 0:
            status = 'critical'
        elif vuln_counts['high'] > 0:
            status = 'high'
        elif vuln_counts['medium'] > 0:
            status = 'medium'
        elif total_vulns > 0:
            status = 'low'
        else:
            status = 'passed'
        
        return {
            'status': status,
            'image': image_tag,
            'vulnerabilities': {
                'critical': vuln_counts['critical'],
                'high': vuln_counts['high'],
                'medium': vuln_counts['medium'],
                'low': vuln_counts['low']
            },
            'detailed_vulnerabilities': detailed_vulns,
            'total_vulnerabilities': total_vulns,
            'scanned_at': datetime.now(timezone.utc).isoformat(),
            'scanner': f'Trivy {scan_data.get("SchemaVersion", "2")}'
        }
        
    except subprocess.TimeoutExpired:
        print(f"Trivy scan timeout for {image_tag}")
        return {
            'status': 'error',
            'image': image_tag,
            'vulnerabilities': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'scanned_at': datetime.now(timezone.utc).isoformat(),
            'scanner': 'Trivy (timeout)',
            'error': 'Scan timeout'
        }
    except Exception as e:
        print(f"Trivy scan error for {image_tag}: {str(e)}")
        return {
            'status': 'error',
            'image': image_tag,
            'vulnerabilities': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'scanned_at': datetime.now(timezone.utc).isoformat(),
            'scanner': 'Trivy (error)',
            'error': str(e)
        }



def generate_dockerfile(base_image, runtime, components, image_name, image_tag):
    """Generate Dockerfile content based on configuration"""
    from datetime import datetime, timezone
    
    # Base image already includes registry prefix if needed
    # Don't add localhost:5050 again if it's already there
    if not base_image.startswith('localhost:5050/'):
        registry_base = f"localhost:5050/{base_image}"
    else:
        registry_base = base_image
    
    # Detect OS type
    is_alpine = 'alpine' in base_image.lower()
    is_redhat = 'redhat' in base_image.lower() or 'ubi' in base_image.lower()
    
    dockerfile = f"""# ImageGuard Generated Dockerfile
# Image: {image_name}:{image_tag}
# Base: {base_image} (from local registry)
# Runtime: {runtime if runtime else 'none (vendor image)'}
# Components: {', '.join(components) if components else 'none'}

FROM {registry_base}

# Set environment to non-interactive to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

"""

    if is_alpine:
        dockerfile += """# Update package manager and install prerequisites (Alpine)
RUN apk update && apk add --no-cache wget curl ca-certificates

"""
    elif is_redhat:
        dockerfile += """# Update package manager and install prerequisites (RedHat UBI)
RUN microdnf update -y && microdnf install -y wget tar gzip && microdnf clean all

"""
    else:
        dockerfile += """# Update package manager and install prerequisites
RUN apt-get update && apt-get install -y wget curl ca-certificates && apt-get clean && rm -rf /var/lib/apt/lists/*

"""

    # Add runtime installation only if runtime is specified
    if runtime:
        runtime_type = ''.join([c for c in runtime if not c.isdigit() and c != '.'])
        
        if runtime_type == 'python':
            version = runtime.replace('python', '')
            if is_alpine:
                # Alpine uses python3 package directly
                dockerfile += f"""# Python runtime installation (Alpine)
RUN apk add --no-cache python3 py3-pip

"""
            elif is_redhat:
                dockerfile += f"""# Python runtime installation (RedHat UBI)
RUN microdnf install -y python3 python3-pip && microdnf clean all

"""
            else:
                # For Ubuntu/Debian - simplified approach without PPA
                # Most Ubuntu versions have python3 available
                dockerfile += f"""# Python runtime installation
RUN apt-get update && \\
    apt-get install -y python3 python3-pip python3-venv && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

"""
        elif runtime_type == 'java':
            version = runtime.replace('java', '')
            if is_alpine:
                # Alpine Java package
                dockerfile += f"""# Java runtime installation (Alpine)
RUN apk add --no-cache openjdk{version}

"""
            elif is_redhat:
                dockerfile += f"""# Java runtime installation (RedHat UBI)
RUN microdnf install -y java-{version}-openjdk java-{version}-openjdk-devel && microdnf clean all

"""
            else:
                dockerfile += f"""# Java runtime installation
RUN apt-get update && apt-get install -y openjdk-{version}-jdk && apt-get clean && rm -rf /var/lib/apt/lists/*

"""
        elif runtime_type == 'node':
            version = runtime.replace('node', '')
            if is_alpine:
                dockerfile += f"""# Node.js runtime installation (Alpine)
RUN apk add --no-cache nodejs npm

"""
            elif is_redhat:
                dockerfile += f"""# Node.js runtime installation (RedHat UBI)
RUN microdnf install -y nodejs npm && microdnf clean all

"""
            else:
                dockerfile += f"""# Node.js runtime installation
RUN curl -fsSL https://deb.nodesource.com/setup_{version}.x | bash - && apt-get install -y nodejs && apt-get clean && rm -rf /var/lib/apt/lists/*

"""
        elif runtime_type == 'go':
            version = runtime.replace('go', '')
            if is_alpine:
                dockerfile += f"""# Go runtime installation (Alpine)
RUN apk add --no-cache go

"""
            elif is_redhat:
                dockerfile += f"""# Go runtime installation (RedHat UBI)
RUN microdnf install -y golang && microdnf clean all

"""
            else:
                dockerfile += f"""# Go runtime installation
RUN wget https://go.dev/dl/go{version}.linux-amd64.tar.gz && tar -C /usr/local -xzf go{version}.linux-amd64.tar.gz && rm go{version}.linux-amd64.tar.gz
ENV PATH="/usr/local/go/bin:$PATH"

"""

    # Add components
    if components:
        dockerfile += "# Install components\n\n"
        
        if 'prometheus' in components:
            dockerfile += """# Prometheus Agent
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz && tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz && cp node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/ && rm -rf node_exporter-1.7.0.linux-amd64*

"""
        
        if 'puppet' in components:
            dockerfile += """# Puppet Agent
RUN wget https://apt.puppet.com/puppet7-release-focal.deb && dpkg -i puppet7-release-focal.deb && apt-get update && apt-get install -y puppet-agent && rm puppet7-release-focal.deb

"""
        
        if 'vault' in components:
            dockerfile += """# HashiCorp Vault Client
RUN wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip && apt-get update && apt-get install -y unzip && unzip vault_1.15.0_linux_amd64.zip && mv vault /usr/local/bin/ && rm vault_1.15.0_linux_amd64.zip

"""
        
        if 'logging' in components:
            dockerfile += """# Custom Logging Agent
RUN apt-get update && apt-get install -y rsyslog && apt-get clean && rm -rf /var/lib/apt/lists/*

"""

    # Add final setup
    dockerfile += f"""# Set working directory
WORKDIR /app

# Add metadata labels
LABEL maintainer="ImageGuard"
LABEL imageguard.base="{base_image}"
LABEL imageguard.runtime="{runtime}"
LABEL imageguard.components="{','.join(components) if components else ''}"
LABEL imageguard.built="{datetime.now(timezone.utc).isoformat()}"

# Default command
CMD ["/bin/bash"]
"""
    
    return dockerfile


def generate_vendor_dockerfile(base_image, components, image_name, image_tag):
    """Generate Dockerfile for vendor images (without runtime)"""
    from datetime import datetime, timezone
    
    # Base image is already in the correct format (localhost:5050/...)
    
    # Detect OS type
    is_alpine = 'alpine' in base_image.lower()
    is_redhat = 'redhat' in base_image.lower() or 'ubi' in base_image.lower()
    
    dockerfile = f"""# ImageGuard Generated Dockerfile (Vendor Image)
# Image: {image_name}:{image_tag}
# Base: {base_image}
# Components: {', '.join(components) if components else 'none'}

FROM {base_image}

# Set environment to non-interactive to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

"""

    if is_alpine:
        dockerfile += """# Update package manager and install prerequisites (Alpine)
RUN apk update && apk add --no-cache wget curl ca-certificates

"""
    elif is_redhat:
        dockerfile += """# Update package manager and install prerequisites (RedHat UBI)
RUN microdnf update -y && microdnf install -y wget tar gzip && microdnf clean all

"""
    else:
        dockerfile += """# Update package manager and install prerequisites
RUN apt-get update && apt-get install -y wget curl ca-certificates && apt-get clean && rm -rf /var/lib/apt/lists/*

"""

    # Add components if any
    if components:
        dockerfile += "# Install components\n\n"
        
        if 'prometheus' in components:
            dockerfile += """# Prometheus Agent
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz && tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz && cp node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/ && rm -rf node_exporter-1.7.0.linux-amd64*

"""
        
        if 'puppet' in components:
            if not is_alpine:
                dockerfile += """# Puppet Agent
RUN wget https://apt.puppet.com/puppet7-release-focal.deb && dpkg -i puppet7-release-focal.deb && apt-get update && apt-get install -y puppet-agent && rm puppet7-release-focal.deb

"""
        
        if 'vault' in components:
            if is_alpine:
                dockerfile += """# HashiCorp Vault Client
RUN wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip && apk add --no-cache unzip && unzip vault_1.15.0_linux_amd64.zip && mv vault /usr/local/bin/ && rm vault_1.15.0_linux_amd64.zip

"""
            else:
                dockerfile += """# HashiCorp Vault Client
RUN wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip && apt-get update && apt-get install -y unzip && unzip vault_1.15.0_linux_amd64.zip && mv vault /usr/local/bin/ && rm vault_1.15.0_linux_amd64.zip

"""
        
        if 'logging' in components:
            if is_alpine:
                dockerfile += """# Custom Logging Agent
RUN apk add --no-cache rsyslog

"""
            else:
                dockerfile += """# Custom Logging Agent
RUN apt-get update && apt-get install -y rsyslog && apt-get clean && rm -rf /var/lib/apt/lists/*

"""

    # Add final setup
    dockerfile += f"""# Set working directory
WORKDIR /app

# Add metadata labels
LABEL maintainer="ImageGuard"
LABEL imageguard.base="{base_image}"
LABEL imageguard.type="vendor"
LABEL imageguard.components="{','.join(components) if components else ''}"
LABEL imageguard.built="{datetime.now(timezone.utc).isoformat()}"

# Default command
CMD ["/bin/bash"]
"""
    
    return dockerfile


@app.route('/api/images')
def api_images():
    """API endpoint for image data"""
    images = get_all_images()
    return jsonify(images)


def get_dashboard_stats():
    """Get dashboard statistics"""
    stats = {
        'total_images': 0,
        'base_images': 0,
        'runtime_images': 0,
        'recent_builds': 0
    }
    
    if docker_client:
        try:
            images = docker_client.images.list()
            stats['total_images'] = len(images)
            
            # Count base images (alpine, ubuntu, redhat)
            base_tags = ['alpine', 'ubuntu', 'redhat']
            for img in images:
                if img.tags:
                    for tag in img.tags:
                        if any(base in tag.lower() for base in base_tags):
                            stats['base_images'] += 1
                            break
        except Exception as e:
            print(f"Error getting stats: {e}")
    
    return stats


def get_all_images():
    """Get all Docker images with metadata (excluding base OS images)"""
    images = []
    
    # Base image names to exclude
    base_image_names = ['alpine', 'ubuntu', 'redhat', 'ubi9']
    
    if docker_client:
        try:
            for img in docker_client.images.list():
                # Skip images without tags
                if not img.tags:
                    continue
                
                # Skip base images
                is_base = any(base in img.tags[0].lower() for base in base_image_names)
                if is_base:
                    continue
                
                image_data = {
                    'id': img.short_id.replace('sha256:', ''),
                    'tags': img.tags,
                    'size': format_size(img.attrs['Size']),
                    'created': format_date(img.attrs['Created'])
                }
                images.append(image_data)
        except Exception as e:
            print(f"Error getting images: {e}")
    
    return images


def get_base_images():
    """Get available base OS images from the base OS registry"""
    import requests
    base_images = []
    
    try:
        # Get catalog of repositories from base OS registry
        catalog_response = requests.get('http://localhost:5050/v2/_catalog')
        if catalog_response.status_code == 200:
            repositories = catalog_response.json().get('repositories', [])
            
            # For each repository, get its tags
            for repo in repositories:
                tags_response = requests.get(f'http://localhost:5050/v2/{repo}/tags/list')
                if tags_response.status_code == 200:
                    tags = tags_response.json().get('tags', [])
                    
                    # Add each tag as a separate option
                    for tag in tags:
                        # Format display name
                        display_name = f"{repo}:{tag}"
                        if 'nessus' in repo.lower():
                            display_name = f"Tenable Nessus - {tag}"
                        elif 'alpine' in repo.lower():
                            display_name = f"Alpine Linux - {tag}"
                        elif 'ubuntu' in repo.lower():
                            display_name = f"Ubuntu - {tag}"
                        elif 'redhat' in repo.lower() or 'ubi' in repo.lower():
                            display_name = f"Red Hat UBI - {tag}"
                        
                        base_images.append({
                            'name': display_name,
                            'tag': f'localhost:5050/{repo}:{tag}'
                        })
    except Exception as e:
        print(f"Error fetching base images from registry: {e}")
        # Fallback to hardcoded list if registry is unavailable
        base_images = [
            {'name': 'Alpine Linux 3.19', 'tag': 'localhost:5050/alpine:3.19'},
            {'name': 'Ubuntu 22.04 LTS', 'tag': 'localhost:5050/ubuntu:22.04'},
            {'name': 'Ubuntu 20.04 LTS', 'tag': 'localhost:5050/ubuntu:20.04'},
            {'name': 'Red Hat UBI 9 Minimal', 'tag': 'localhost:5050/redhat/ubi9-minimal:latest'}
        ]
    
    return base_images


def get_available_runtimes():
    """Get available runtime options"""
    return [
        {'name': 'Python 3.9', 'value': 'python3.9'},
        {'name': 'Python 3.10', 'value': 'python3.10'},
        {'name': 'Python 3.11', 'value': 'python3.11'},
        {'name': 'Java 11', 'value': 'java11'},
        {'name': 'Java 17', 'value': 'java17'},
        {'name': 'Node.js 18', 'value': 'node18'},
        {'name': 'Node.js 20', 'value': 'node20'},
        {'name': 'Go 1.21', 'value': 'go1.21'}
    ]


def get_available_components():
    """Get available component options"""
    return [
        {'name': 'Prometheus Agent', 'value': 'prometheus'},
        {'name': 'Puppet Agent', 'value': 'puppet'},
        {'name': 'HashiCorp Vault Client', 'value': 'vault'},
        {'name': 'Custom Logging Agent', 'value': 'logging'}
    ]


def format_size(bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"


def format_date(date_string):
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_string


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
