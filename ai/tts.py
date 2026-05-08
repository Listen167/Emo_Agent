import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

import torch
from pathlib import Path

_MODEL_PATH = Path("D:/PragramFile/VScode/Emo_Agent/models")

def synthesize(text: str, session_id: str, emotion: str) -> str:
    try:
        from transformers import SpeechT5ForTextToSpeech, SpeechT5Processor
        from datasets import load_dataset
        import soundfile as sf
        
        model_path = _MODEL_PATH / "speecht5_tts"
        processor_path = _MODEL_PATH / "speecht5_tts"
        
        model = SpeechT5ForTextToSpeech.from_pretrained(str(model_path))
        processor = SpeechT5Processor.from_pretrained(str(processor_path))
        
        if torch.cuda.is_available():
            model = model.to("cuda")
        
        embeddings_path = _MODEL_PATH / "cmu-arctic-xvectors"
        embeddings_dataset = load_dataset(str(embeddings_path), split="validation")
        speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
        if torch.cuda.is_available():
            speaker_embeddings = speaker_embeddings.to("cuda")
        
        inputs = processor(text=text, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        speech = model.generate_speech(inputs["input_ids"], speaker_embeddings)
        
        out_dir = Path("./data/tts")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{session_id}_{len(text)}.wav"
        
        speech = speech.cpu().numpy()
        sf.write(str(out_path), speech, 16000)
        
        return str(out_path)
    except Exception as e:
        print(f"[TTS Error] {e}")
        import traceback
        traceback.print_exc()
        return ""