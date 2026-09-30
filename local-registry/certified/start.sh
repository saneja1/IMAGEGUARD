#!/bin/bash
# ImageGuard Certified Registry + UI — Usage: ./start.sh [start|stop|restart|status]

REGISTRY="imageguard-certified-registry"
UI="imageguard-registry-ui"
CMD="${1:-start}"

case "$CMD" in
  status)
    echo "=== Certified Registry ==="
    if [ "$(docker ps -q -f name=$REGISTRY)" ]; then
      echo "✓ $REGISTRY is RUNNING (port 5051)"
      docker ps --filter "name=$REGISTRY" --format "  ID: {{.ID}}  Status: {{.Status}}"
    elif [ "$(docker ps -aq -f name=$REGISTRY)" ]; then
      echo "✗ $REGISTRY is STOPPED"
    else
      echo "✗ $REGISTRY does not exist"
    fi
    echo ""
    echo "=== Registry UI ==="
    if [ "$(docker ps -q -f name=$UI)" ]; then
      echo "✓ $UI is RUNNING (port 8082)"
      docker ps --filter "name=$UI" --format "  ID: {{.ID}}  Status: {{.Status}}"
    elif [ "$(docker ps -aq -f name=$UI)" ]; then
      echo "✗ $UI is STOPPED"
    else
      echo "✗ $UI does not exist"
    fi
    ;;
  stop)
    echo "Stopping $UI..."
    docker stop $UI && echo "✓ UI stopped"
    echo "Stopping $REGISTRY..."
    docker stop $REGISTRY && echo "✓ Registry stopped"
    ;;
  restart)
    echo "Restarting containers..."
    docker restart $REGISTRY && echo "✓ Registry restarted on localhost:5051"
    docker restart $UI && echo "✓ UI restarted on localhost:8082"
    ;;
  start)
    echo "Starting ImageGuard Certified Images Registry..."
    if [ "$(docker ps -aq -f name=$REGISTRY)" ]; then
      docker start $REGISTRY
    else
      docker run -d \
        -p 5051:5000 \
        -v "$(pwd)/data:/var/lib/registry" \
        --name $REGISTRY \
        --restart always \
        -e "REGISTRY_HTTP_HEADERS_Access-Control-Allow-Origin=[http://localhost:8082]" \
        -e "REGISTRY_HTTP_HEADERS_Access-Control-Allow-Methods=[HEAD,GET,OPTIONS,DELETE]" \
        -e "REGISTRY_HTTP_HEADERS_Access-Control-Allow-Headers=[Authorization,Accept,Cache-Control]" \
        -e "REGISTRY_HTTP_HEADERS_Access-Control-Expose-Headers=[Docker-Content-Digest]" \
        -e "REGISTRY_STORAGE_DELETE_ENABLED=true" \
        registry:2
    fi

    docker network inspect imageguard-net >/dev/null 2>&1 || docker network create imageguard-net
    docker network connect imageguard-net $REGISTRY 2>/dev/null || true

    if [ "$(docker ps -aq -f name=$UI)" ]; then
      docker start $UI
    else
      docker run -d \
        -p 8082:80 \
        --name $UI \
        --restart always \
        -e SINGLE_REGISTRY=true \
        -e REGISTRY_TITLE="ImageGuard Certified Images" \
        -e REGISTRY_URL=http://localhost:5051 \
        -e DELETE_IMAGES=true \
        -e SHOW_CONTENT_DIGEST=true \
        joxit/docker-registry-ui:latest
    fi

    echo "✓ Certified Registry running on localhost:5051"
    echo "✓ Registry UI available at http://localhost:8082"
    ;;
  *)
    echo "Usage: ./start.sh [start|stop|restart|status]"
    exit 1
    ;;
esac
