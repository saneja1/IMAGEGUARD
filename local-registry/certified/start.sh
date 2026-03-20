#!/bin/bash
# Start the Certified Images Registry with UI

echo "Starting ImageGuard Certified Images Registry..."

# Start the registry container
if [ "$(docker ps -aq -f name=imageguard-certified-registry)" ]; then
    echo "Registry container exists. Starting it..."
    docker start imageguard-certified-registry
else
    echo "Creating registry container..."
    docker run -d \
        -p 5051:5000 \
        -v "$(pwd)/data:/var/lib/registry" \
        --name imageguard-certified-registry \
        --restart always \
        -e "REGISTRY_HTTP_HEADERS_Access-Control-Allow-Origin=[http://localhost:8082]" \
        -e "REGISTRY_HTTP_HEADERS_Access-Control-Allow-Methods=[HEAD,GET,OPTIONS,DELETE]" \
        -e "REGISTRY_HTTP_HEADERS_Access-Control-Allow-Headers=[Authorization,Accept,Cache-Control]" \
        -e "REGISTRY_HTTP_HEADERS_Access-Control-Expose-Headers=[Docker-Content-Digest]" \
        -e "REGISTRY_STORAGE_DELETE_ENABLED=true" \
        registry:2
fi

# Create network if it doesn't exist
docker network inspect imageguard-net >/dev/null 2>&1 || docker network create imageguard-net

# Connect registry to network
docker network connect imageguard-net imageguard-certified-registry 2>/dev/null || true

# Start the UI container
if [ "$(docker ps -aq -f name=imageguard-registry-ui)" ]; then
    echo "UI container exists. Starting it..."
    docker start imageguard-registry-ui
else
    echo "Creating UI container..."
    docker run -d \
        -p 8082:80 \
        --name imageguard-registry-ui \
        --restart always \
        -e SINGLE_REGISTRY=true \
        -e REGISTRY_TITLE="ImageGuard Certified Images" \
        -e REGISTRY_URL=http://localhost:5051 \
        -e DELETE_IMAGES=true \
        -e SHOW_CONTENT_DIGEST=true \
        joxit/docker-registry-ui:latest
fi

echo ""
echo "✓ Certified Images Registry running on localhost:5051"
echo "✓ Registry UI available at http://localhost:8082"
echo ""
echo "To stop registry: docker stop imageguard-certified-registry"
echo "To stop UI: docker stop imageguard-registry-ui"
