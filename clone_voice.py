import os
import time
import torch
import torchaudio
import numpy as np
from omnivoice import OmniVoice

def main():
    if not torch.cuda.is_available():
        raise RuntimeError("NVIDIA GPU context not detected. Make sure drivers are loaded.")
    
    # Check for the asset file (Make sure modi.mp3 is uploaded to your VM folder!)
    ref_file = "modi.mp3"
    if not os.path.exists(ref_file):
        raise FileNotFoundError(f"Please pull or upload '{ref_file}' into this directory.")

    print("Loading OmniVoice framework onto V100 system layers...")
    model = OmniVoice.from_pretrained(
        "k2-fsa/OmniVoice",
        device_map="cuda:0",
        dtype=torch.float16
    )

    print("Starting specialized cross-lingual inference...")
    start_time = time.time()

    # Using your exact parameters from the successful Colab run
    audio = model.generate(
        text="""
        भाइयो और बहनों आज देश में एक नया प्रयोग हो रहा है, पाँच AI एजेंट्स और एक इंसान सब एक साथ voice room में बहस करेंगे बिना script के बिना किसी पूर्व निर्धारित क्रम के एक दूसरे को टोकेंगे असहमत होंगे और जिससे बात की जाए वही जवाब देगा ये है हमारा Council of Agents [pause] — जहाँ AI सिर्फ बोलता नहीं बल्कि बहस करता है और इस अनोखी पहल पर काम कर रहे हैं हमारे युवा प्रतिभाशाली उद्यमी — Dushyant और Vaibhav ये प्रोजेक्ट बहुत जल्द लॉन्च हो रहा है तो तैयार रहिए क्योंकि आवाज़ का भविष्य अब आ रहा है — और ये भविष्य है दमदार है भारतीय है अभूतपूर्व धन्यवाद
        """,
        ref_audio=ref_file,
        ref_text="""
        साथियो, कुछ लोग देश की महिलाओं के सपने टूटने को सरकार की नाकामी बता रहे हैं। लेकिन ये विषय कामयाबी
        """
    )

    print(f"Inference complete in: {time.time() - start_time:.2f}s")

    # Post-processing array formatting safely
    wav = audio[0]
    if isinstance(wav, np.ndarray):
        wav = torch.from_numpy(wav)
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)

    output_filename = "output.wav"
    torchaudio.save(output_filename, wav, 24000)
    print(f"Success! Perfect audio asset saved to disk: {output_filename}")

if __name__ == "__main__":
    main()