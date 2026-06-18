#!/bin/bash

INSTANCE_NAME="coa-inference-node"
PROJECT_ID="sharp-leaf-451416-r4"
ZONE="europe-west4-a"

usage() {
    echo "Usage: $0 {start|stop|status|ssh}"
    echo ""
    echo "  start   - Start the VM"
    echo "  stop    - Stop the VM (halt billing, data preserved)"
    echo "  status  - Show whether the VM is on or off"
    echo "  ssh     - Connect to the VM via SSH"
    exit 1
}

start_vm() {
    echo "Starting $INSTANCE_NAME..."
    gcloud compute instances start "$INSTANCE_NAME" \
        --project="$PROJECT_ID" \
        --zone="$ZONE"
}

stop_vm() {
    echo "Stopping $INSTANCE_NAME..."
    gcloud compute instances stop "$INSTANCE_NAME" \
        --project="$PROJECT_ID" \
        --zone="$ZONE"
}

status_vm() {
    local status
    status=$(gcloud compute instances describe "$INSTANCE_NAME" \
        --project="$PROJECT_ID" \
        --zone="$ZONE" \
        --format='value(status)' 2>/dev/null)

    if [ -z "$status" ]; then
        echo "VM '$INSTANCE_NAME' not found or unable to query status."
        exit 1
    fi

    case "$status" in
        RUNNING)
            echo "on"
            ;;
        TERMINATED)
            echo "off"
            ;;
        STAGING|PROVISIONING)
            echo "starting ($status)"
            ;;
        STOPPING|SUSPENDING)
            echo "stopping ($status)"
            ;;
        *)
            echo "$status"
            ;;
    esac
}

ssh_vm() {
    gcloud compute ssh "$INSTANCE_NAME" \
        --project="$PROJECT_ID" \
        --zone="$ZONE"
}

case "${1:-}" in
    start)
        start_vm
        ;;
    stop)
        stop_vm
        ;;
    status)
        status_vm
        ;;
    ssh)
        ssh_vm
        ;;
    *)
        usage
        ;;
esac
