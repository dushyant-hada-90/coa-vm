#!/usr/bin/env python3
"""EmoKnob inference — English voice cloning with emotion control."""

from __future__ import annotations

import argparse
import os
import pickle
import shutil
import sys
import tempfile
import time
import warnings
from pathlib import Path

# Quiet known third-party noise (inference still works without these).
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")
warnings.filterwarnings("ignore", message=".*weight_norm.*deprecated.*")
warnings.filterwarnings("ignore", message=".*AudioMetaData.*")
warnings.filterwarnings("ignore", message=".*CuDNN issue.*")
os.environ.setdefault("LOGURU_LEVEL", "WARNING")

import librosa
import soundfile as sf
import torch
from huggingface_hub import snapshot_download

MODEL = "metavoiceio/metavoice-1B-v0.1"
SEED = 1337
SAMPLE_RATE = 24000


def emoknob_home() -> Path:
    return Path(os.environ.get("EMOKNOB_HOME", Path.home() / "emoknob")).expanduser()


def setup_path(home: Path) -> None:
    mv = home / "src" / "metavoice-src-main"
    if not mv.is_dir():
        raise FileNotFoundError(f"Run bootstrap_emoknob.sh first. Missing: {mv}")
    sys.path.insert(0, str(mv))


def load_emo_dirs(home: Path) -> dict:
    pkl = home / "src" / "all_emo_dirs.pkl"
    if not pkl.is_file():
        raise FileNotFoundError(f"Missing emotion data: {pkl}")
    with open(pkl, "rb") as f:
        return pickle.load(f)


def prepare_ref_audio(path: str) -> tuple[str, bool]:
    """Return 24 kHz mono WAV path and whether caller should delete it."""
    audio, _ = librosa.load(path, sr=SAMPLE_RATE, mono=True)
    if path.lower().endswith(".wav"):
        try:
            info = sf.info(path)
            if info.samplerate == SAMPLE_RATE and info.channels == 1:
                return path, False
        except Exception:
            pass
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, SAMPLE_RATE)
    return tmp.name, True


def load_models(device: str, compile_model: bool, work_dir: Path):
    from fam.llm.adapters import FlattenedInterleavedEncodec2Codebook
    from fam.llm.fast_inference_utils import build_model, main as stage1
    from fam.llm.inference import (
        EncodecDecoder,
        InferenceConfig,
        Model,
        TiltedEncodec,
        TrainedBPETokeniser,
        get_cached_embedding,
        get_enhancer,
    )
    from fam.llm.utils import get_default_dtype, normalize_text

    dtype = get_default_dtype()
    precision = {"float16": torch.float16, "bfloat16": torch.bfloat16}[dtype]

    print(f"Loading {MODEL}...")
    model_dir = snapshot_download(repo_id=MODEL)
    work_dir.mkdir(parents=True, exist_ok=True)

    adapter = FlattenedInterleavedEncodec2Codebook(end_of_audio_token=1024)
    stage2 = Model(
        InferenceConfig(
            ckpt_path=str(Path(model_dir) / "second_stage.pt"),
            num_samples=1,
            seed=SEED,
            device=device,
            dtype=dtype,
            compile=False,
            init_from="resume",
            output_dir=str(work_dir),
        ),
        TrainedBPETokeniser,
        EncodecDecoder,
        data_adapter_fn=TiltedEncodec(end_of_audio_token=1024).decode,
    )

    print("Loading MetaVoice first stage...")
    model, tokenizer, smodel, model_size = build_model(
        precision=precision,
        checkpoint_path=Path(model_dir) / "first_stage.pt",
        spk_emb_ckpt_path=Path(model_dir) / "speaker_encoder.pt",
        device=device,
        compile=compile_model,
        compile_prefill=compile_model,
    )

    return {
        "device": device,
        "precision": precision,
        "adapter": adapter,
        "stage1": stage1,
        "stage2": stage2,
        "enhancer": get_enhancer("df"),
        "model": model,
        "tokenizer": tokenizer,
        "smodel": smodel,
        "model_size": model_size,
        "embed": get_cached_embedding,
        "normalize": normalize_text,
    }


def synthesize(ctx, *, text, ref_audio, emo_dir, strength, output: Path):
    device, precision = ctx["device"], ctx["precision"]
    text = ctx["normalize"](text)
    ref_path, cleanup = prepare_ref_audio(ref_audio)

    print(f"Reference: {ref_audio} -> {SAMPLE_RATE} Hz mono")
    print(f"Text: {text} | emotion strength: {strength}")

    try:
        emb = ctx["embed"](ref_path, ctx["smodel"]).to(device=device, dtype=precision)
        edited = emb + strength * torch.tensor(emo_dir, device=device, dtype=precision)

        t0 = time.time()
        tokens = ctx["stage1"](
            model=ctx["model"],
            tokenizer=ctx["tokenizer"],
            model_size=ctx["model_size"],
            prompt=text,
            spk_emb=edited,
            top_p=torch.tensor(0.95, device=device, dtype=precision),
            guidance_scale=torch.tensor(3.0, device=device, dtype=precision),
            temperature=torch.tensor(1.0, device=device, dtype=precision),
            device=device,
        )
        _, audio_ids = ctx["adapter"].decode([tokens])

        wavs = ctx["stage2"](
            texts=[text],
            encodec_tokens=[
                torch.tensor(audio_ids, dtype=torch.int32, device=device).unsqueeze(0)
            ],
            speaker_embs=edited.unsqueeze(0),
            batch_size=1,
            guidance_scale=None,
            top_p=None,
            top_k=200,
            temperature=1.0,
            max_new_tokens=None,
        )

        raw = Path(str(wavs[0]) + ".wav")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            enhanced = tmp.name
        try:
            ctx["enhancer"](str(raw), enhanced)
            shutil.copy2(enhanced, output)
        finally:
            if os.path.exists(enhanced):
                os.remove(enhanced)

        print(f"Done in {time.time() - t0:.1f}s -> {output}")
    finally:
        if cleanup and os.path.exists(ref_path):
            os.remove(ref_path)


def main():
    p = argparse.ArgumentParser(description="EmoKnob voice cloning (English only)")
    p.add_argument("--text", help="English text to synthesize")
    p.add_argument("--ref-audio", help="Reference WAV/MP3 for voice cloning")
    p.add_argument("--emotion", default="happy")
    p.add_argument("--strength", type=float, default=0.3)
    p.add_argument("--output", default="output.wav")
    p.add_argument("--compile", action="store_true", help="Enable torch.compile")
    p.add_argument("--list-emotions", action="store_true")
    p.add_argument("--device", default="cuda:0")
    args = p.parse_args()

    home = emoknob_home()
    setup_path(home)
    emo_dirs = load_emo_dirs(home)

    if args.list_emotions:
        for name in sorted(emo_dirs):
            print(name)
        return

    if not args.text or not args.ref_audio:
        p.error("--text and --ref-audio are required (or use --list-emotions)")
    if args.emotion not in emo_dirs:
        p.error(f"unknown emotion '{args.emotion}'")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU required")

    ctx = load_models(args.device, args.compile, Path("outputs"))
    synthesize(
        ctx,
        text=args.text,
        ref_audio=args.ref_audio,
        emo_dir=emo_dirs[args.emotion],
        strength=args.strength,
        output=Path(args.output),
    )


if __name__ == "__main__":
    main()
