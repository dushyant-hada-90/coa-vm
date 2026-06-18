import os
import torch
from omnivoice import OmniVoice
import soundfile as sf

def main():
    if not torch.cuda.is_available():
        raise RuntimeError("NVIDIA GPU context not detected.")
    
    ref_audio_path = "modi.mp3"
    if not os.path.exists(ref_audio_path):
        raise FileNotFoundError(f"Missing reference file: '{ref_audio_path}'")

    print("Loading OmniVoice model into V100...")
    model = OmniVoice.from_pretrained(
        "k2-fsa/OmniVoice", 
        device_map="cuda:0", 
        dtype=torch.float16
    )
    
    # 1. WHAT THE REFERENCE AUDIO IS ACTUALLY SAYING (The Transcript)
    # Provide the exact words spoken in modi.mp3 so the model aligns perfectly.
    reference_transcript = "साथियो, कुछ लोग देश की महिलाओं के सपने टूटने को सरकार की नाकामी बता रहे हैं। लेकिन ये विषय कामयाबी" 
    
    # 2. THE NEW TEXT YOU WANT TO GENERATE
    target_text = "भाइयों और बहनों, हमारे इस नए क्लाउड सर्वर पर ऑडियो क्लोनिंग पूरी तरह से काम कर रही है।"
    
    print("Running aligned cross-lingual voice synthesis...")
    audio_tensors = model.generate(
        text=target_text,
        prompt_audio=ref_audio_path,
        prompt_text=reference_transcript  # <--- This guides the phoneme alignment
    )
    
    output_path = "cloned_output.mp3"
    sf.write(output_path, audio_tensors[0], 24000)
    print(f"\nSuccess! Aligned audio saved to: {output_path}")

if __name__ == "__main__":
    main()