import os
import torch
from omnivoice import OmniVoice
import soundfile as sf

def main():
    # 1. Verify CUDA/GPU context is active
    if not torch.cuda.is_available():
        raise RuntimeError("NVIDIA GPU context not detected. Run 'nvidia-smi' to verify drivers.")
    
    print(f"Using GPU acceleration on: {torch.cuda.get_device_name(0)}")
    
    # 2. Check for reference voice file
    ref_audio_path = "modi.wav"
    if not os.path.exists(ref_audio_path):
        raise FileNotFoundError(f"Missing reference file: '{ref_audio_path}'. Please place it in this directory.")

    print("Loading OmniVoice framework into V100 VRAM...")
    # FP16 precision keeps memory foot-print optimized for fast cross-handshakes
    model = OmniVoice.from_pretrained(
        "k2-fsa/OmniVoice", 
        device_map="cuda:0", 
        dtype=torch.float16
    )
    
    # 3. Define target script text
    prompt_text = "My fellow citizens, the audio cloning pipeline execution on this European cloud node is operational."
    print(f"Cloning voice profile from '{ref_audio_path}' using text: '{prompt_text}'")
    
    # 4. Generate the voice clone arrays
    audio_tensors = model.generate(
        text=prompt_text,
        prompt_audio=ref_audio_path  # Feeds the reference audio properties to the generation pipeline
    )
    
    # 5. Write the resulting cloned output to disk
    output_path = "cloned_output.wav"
    sf.write(output_path, audio_tensors[0], 24000)
    print(f"\nSuccess! Cloned voice output saved cleanly to: {output_path}")

if __name__ == "__main__":
    main()