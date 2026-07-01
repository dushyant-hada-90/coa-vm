#!/bin/bash
# Shared environment loader for coa-vm scripts.
# Sources .env from the repo root when present; falls back to defaults.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
fi

# VM lifecycle (vm.sh)
: "${PROJECT_ID:=sharp-leaf-451416-r4}"
: "${ZONE:=europe-west4-a}"
: "${INSTANCE_NAME:=coa-inference-node}"

# Instance creation (create_instance.sh)
: "${MACHINE_TYPE:=n1-standard-8}"
: "${GPU_TYPE:=nvidia-tesla-v100}"
: "${GPU_COUNT:=1}"
: "${IMAGE_PROJECT:=ubuntu-os-cloud}"
: "${IMAGE_FAMILY:=ubuntu-2204-lts}"
: "${BOOT_DISK_SIZE:=150GB}"
: "${BOOT_DISK_TYPE:=pd-ssd}"

# EmoKnob paths (bootstrap / inference)
: "${EMOKNOB_HOME:=$HOME/emoknob}"
: "${COA_VM_HOME:=$HOME/coa-vm}"
