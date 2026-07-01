#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/load_env.sh"

VENV="${COA_VM_HOME}/.venv"
PIP="${VENV}/bin/pip"
PY="${VENV}/bin/python"
MV="${EMOKNOB_HOME}/src/metavoice-src-main"
TORCH="https://download.pytorch.org/whl/cu118"

echo "=== EmoKnob bootstrap ==="

sudo apt-get update -qq
sudo apt-get install -y build-essential git ffmpeg libsndfile1 curl software-properties-common

if ! command -v python3.10 &>/dev/null; then
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update -qq
    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
fi

if [ -d "${EMOKNOB_HOME}/.git" ]; then
    git -C "${EMOKNOB_HOME}" pull --ff-only
else
    git clone https://github.com/tonychenxyz/emoknob.git "${EMOKNOB_HOME}"
fi

mkdir -p "${COA_VM_HOME}"
[ -d "${VENV}" ] || python3.10 -m venv "${VENV}"
"${PIP}" install -q --upgrade pip setuptools wheel

echo ">>> PyTorch cu118"
"${PIP}" install torch==2.1.2+cu118 torchaudio==2.1.2+cu118 torchvision==0.16.2+cu118 \
    --index-url "${TORCH}"
"${PIP}" install numpy==1.24.4

echo ">>> audiocraft stack"
"${PIP}" install av==12.3.0
"${PIP}" install audiocraft==1.3.0 --no-deps
"${PIP}" install transformers==4.33.1
"${PIP}" install einops hydra-core hydra_colorlog librosa soundfile tqdm \
    flashy julius encodec demucs num2words sentencepiece lameenc torchmetrics \
    "protobuf==3.20.3" "spacy==3.6.1"
"${PIP}" install xformers==0.0.22.post7 --no-deps
"${PIP}" install torchtext==0.16.0 --no-deps

echo ">>> EmoKnob deps"
"${PIP}" install tiktoken==0.5.1 "pydantic==1.10.10" "huggingface-hub>=0.15.1,<1.0" \
    pydub deepfilternet ninja

echo ">>> Patch MetaVoice for torch 2.1.2"
TARGET="${MV}/fam/llm/fast_inference_utils.py"
"${PY}" - "${TARGET}" <<'PY'
import re, sys
from pathlib import Path
path = Path(sys.argv[1])
text = path.read_text()
if "fx_graph_cache" in text and "hasattr(torch._inductor.config" in text:
    print("already patched")
    raise SystemExit(0)
pat = re.compile(
    r"torch\._inductor\.config\.coordinate_descent_tuning = True\s+"
    r"torch\._inductor\.config\.triton\.unique_kernel_names = True\s+"
    r"torch\._inductor\.config\.fx_graph_cache = \(\s*True.*?\n\s*\)",
    re.DOTALL,
)
rep = (
    "try:\n    torch._inductor.config.coordinate_descent_tuning = True\n"
    "    torch._inductor.config.triton.unique_kernel_names = True\n"
    "    if hasattr(torch._inductor.config, 'fx_graph_cache'):\n"
    "        torch._inductor.config.fx_graph_cache = True\n"
    "except AttributeError:\n    pass"
)
new, n = pat.subn(rep, text, count=1)
if n != 1:
    sys.exit(f"patch failed: {path}")
path.write_text(new)
print(f"patched {path}")
PY

echo ">>> MetaVoice install"
"${PIP}" install -e "${MV}"

echo ">>> Verify"
"${PY}" -c "import torch; assert torch.cuda.is_available(); print('cuda ok', torch.cuda.get_device_name(0))"
"${PY}" -c "from audiocraft.models import EncodecModel; import fam; print('imports ok')"
"${PY}" "${COA_VM_HOME}/run_emoknob.py" --list-emotions | head -5
echo "=== bootstrap complete ==="
