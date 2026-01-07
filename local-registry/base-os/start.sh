#!/bin/bash
# Start the Base OS Images Registry

echo "Starting ImageGuard Base OS Registry..."

# Check if container already exists
if [ "$(docker ps -aq -f name=imageguard-base-registry)" ]; then
    echo "Container exists. Starting it..."
    docker start imageguard-base-registry
else
    echo "Creating new container..."
    docker run -d \
        -p 5050:5000 \
        -v "$(pwd)/data:/var/lib/registry" \
        --name imageguard-base-registry \
        --restart always \
        registry:2
fi

echo ""
echo "✓ Base OS Registry running on localhost:5050"
echo "To stop: docker stop imageguard-base-registry"
echo "To remove: docker rm imageguard-base-registry"
