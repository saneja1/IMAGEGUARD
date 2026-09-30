#!/bin/bash
# ImageGuard Base OS Registry — Usage: ./start.sh [start|stop|restart|recreate|status]
# recreate = remove container only, keep ./data (use after changing env/flags)

CONTAINER="imageguard-base-registry"
CMD="${1:-start}"

run_registry() {
  docker run -d \
    -p 5050:5000 \
    -v "$(pwd)/data:/var/lib/registry" \
    --name $CONTAINER \
    --restart always \
    -e REGISTRY_STORAGE_DELETE_ENABLED=true \
    registry:2
}

case "$CMD" in
  status)
    if [ "$(docker ps -q -f name=$CONTAINER)" ]; then
      echo "✓ $CONTAINER is RUNNING (port 5050)"
      docker ps --filter "name=$CONTAINER" --format "  ID: {{.ID}}  Status: {{.Status}}"
      docker inspect $CONTAINER --format '  Delete enabled: {{index .Config.Env 0}}' 2>/dev/null || true
      docker inspect $CONTAINER --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'DELETE|REGISTRY' || true
    elif [ "$(docker ps -aq -f name=$CONTAINER)" ]; then
      echo "✗ $CONTAINER is STOPPED"
    else
      echo "✗ $CONTAINER does not exist"
    fi
    ;;
  stop)
    echo "Stopping $CONTAINER..."
    docker stop $CONTAINER && echo "✓ Stopped"
    ;;
  restart)
    echo "Restarting $CONTAINER..."
    docker restart $CONTAINER && echo "✓ Restarted — Base OS Registry on localhost:5050"
    ;;
  recreate)
    echo "Recreating $CONTAINER (keeps ./data — images are preserved)..."
    docker stop $CONTAINER 2>/dev/null || true
    docker rm $CONTAINER 2>/dev/null || true
    run_registry
    echo "✓ Base OS Registry recreated on localhost:5050 (delete enabled)"
    ;;
  start)
    echo "Starting ImageGuard Base OS Registry..."
    if [ "$(docker ps -aq -f name=$CONTAINER)" ]; then
      docker start $CONTAINER
      echo "✓ Base OS Registry running on localhost:5050"
      echo "  Note: existing container keeps its old settings."
      echo "  To enable delete (or apply start.sh changes): ./start.sh recreate"
    else
      run_registry
      echo "✓ Base OS Registry running on localhost:5050 (delete enabled)"
    fi
    ;;
  *)
    echo "Usage: ./start.sh [start|stop|restart|recreate|status]"
    exit 1
    ;;
esac
