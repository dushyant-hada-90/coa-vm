#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/load_env.sh"

echo "========================================================"
echo "Creating GPU Instance: $INSTANCE_NAME"
echo "Project:               $PROJECT_ID"
echo "Zone:                  $ZONE"
echo "Machine type:          $MACHINE_TYPE"
echo "GPU:                   ${GPU_TYPE} x${GPU_COUNT}"
echo "Using Base Image:      $IMAGE_PROJECT/$IMAGE_FAMILY"
echo "========================================================"

CREATE_ARGS=(
    --project="$PROJECT_ID"
    --zone="$ZONE"
    --machine-type="$MACHINE_TYPE"
    --image-family="$IMAGE_FAMILY"
    --image-project="$IMAGE_PROJECT"
    --boot-disk-size="$BOOT_DISK_SIZE"
    --boot-disk-type="$BOOT_DISK_TYPE"
    --metadata=install-nvidia-driver=true
    --maintenance-policy=TERMINATE
)

# G2 machine types include L4 GPUs; N1 types need --accelerator.
if [[ "$MACHINE_TYPE" == g2-* ]]; then
    echo "G2 machine type detected — using embedded GPU (no --accelerator flag)."
else
    CREATE_ARGS+=(--accelerator=type="$GPU_TYPE",count="$GPU_COUNT")
fi

gcloud compute instances create "$INSTANCE_NAME" "${CREATE_ARGS[@]}"

echo "Deployment command completed."
