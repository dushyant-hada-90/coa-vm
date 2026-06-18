#!/bash/bin

INSTANCE_NAME="coa-inference-node"
PROJECT_ID="sharp-leaf-451416-r4"
ZONE="europe-west4-a"
MACHINE_TYPE="n1-standard-8"
GPU_TYPE="nvidia-tesla-v100"
GPU_COUNT=1

# Using Google's universal standard Ubuntu image (Always available)
IMAGE_PROJECT="ubuntu-os-cloud"
IMAGE_FAMILY="ubuntu-2204-lts"

echo "========================================================"
echo "Creating GPU Instance: $INSTANCE_NAME"
echo "Project:               $PROJECT_ID"
echo "Zone:                  $ZONE"
echo "Using Base Image:      $IMAGE_PROJECT/$IMAGE_FAMILY"
echo "========================================================"

gcloud compute instances create "$INSTANCE_NAME" \
    --project="$PROJECT_ID" \
    --zone="$ZONE" \
    --machine-type="$MACHINE_TYPE" \
    --accelerator=type="$GPU_TYPE",count=$GPU_COUNT \
    --image-family="$IMAGE_FAMILY" \
    --image-project="$IMAGE_PROJECT" \
    --boot-disk-size=150GB \
    --boot-disk-type=pd-ssd \
    --metadata=install-nvidia-driver=true \
    --maintenance-policy=TERMINATE

echo "Deployment command completed."