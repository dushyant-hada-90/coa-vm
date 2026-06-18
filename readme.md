# Council of Agents (CoA) — Inference Node Runbook

Manage the `coa-inference-node` GCP VM from your **local terminal** using `vm.sh`. Lifecycle commands cannot be run from inside an SSH session.

```bash
chmod +x vm.sh   # first time only
```

## VM Commands

| Command | Description |
|---------|-------------|
| `./vm.sh start` | Start the VM (allocates CPU + V100 GPU) |
| `./vm.sh stop` | Stop the VM (halts billing, keeps disk data) |
| `./vm.sh status` | Check if VM is `on` or `off` |
| `./vm.sh ssh` | SSH into the VM |

Typical workflow:

```bash
./vm.sh start
./vm.sh status    # wait until it prints "on"
./vm.sh ssh
```

## Voice Cloning

Once connected via SSH:

```bash
cd ~/coa-vm
python3 clone_voice.py
```

Place the reference audio (e.g. `modi.mp3`) in the folder before running. Output is saved as `output.wav`.
