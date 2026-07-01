# CoA EmoKnob Inference Node

GCP VM runbook for [EmoKnob](https://github.com/tonychenxyz/emoknob) / MetaVoice-1B. **English only.**

## Local: VM lifecycle

```bash
chmod +x vm.sh
./vm.sh start    # wait for ./vm.sh status -> "on"
./vm.sh ssh
./vm.sh stop     # halt billing
```

Optional: `cp .env.example .env` to override project/zone (defaults in `load_env.sh`).

## VM: one-time setup

```bash
git clone https://github.com/dushyant-hada-90/coa-vm.git ~/coa-vm
cd ~/coa-vm && bash bootstrap_emoknob.sh
```

Takes ~15–30 min first time (PyTorch + model cache on first inference).

## VM: run inference

```bash
source ~/coa-vm/.venv/bin/activate
cd ~/coa-vm

python run_emoknob.py --list-emotions

python run_emoknob.py \
  --text "This is a great project with expressive speech." \
  --ref-audio palki.mp3 \
  --emotion happy \
  --strength 0.3 \
  --output output.wav
```

Reference audio is auto-resampled to 24 kHz mono (avoids DeepFilterNet warnings).

`outputs/` holds MetaVoice intermediates; final file is `--output` (default `output.wav`).

## If CUDA OOM on V100

1. Keep `--compile` off (default)
2. Recreate VM with L4: set `MACHINE_TYPE=g2-standard-8` in `.env`, delete instance, run `create_instance.sh`, re-bootstrap

## Files

| File | Role |
|------|------|
| `vm.sh` | start / stop / status / ssh |
| `create_instance.sh` | provision GPU VM |
| `bootstrap_emoknob.sh` | install deps + EmoKnob |
| `run_emoknob.py` | inference CLI |
| `load_env.sh` | shared config defaults |
