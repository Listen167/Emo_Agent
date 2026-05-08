import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

import torch
import numpy as np
from transformers import WhisperForConditionalGeneration, WhisperProcessor, pipeline

_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_MODEL_PATH = Path("D:/PragramFile/VScode/Emo_Agent/models")
_ASR_MODEL = None
_ASR_PROCESSOR = None
_TEXT_PIPE = None

def _load_asr():
    global _ASR_MODEL, _ASR_PROCESSOR
    if _ASR_MODEL is None:
        model_path = _MODEL_PATH / "whisper-base"
        _ASR_MODEL = WhisperForConditionalGeneration.from_pretrained(str(model_path))
        _ASR_PROCESSOR = WhisperProcessor.from_pretrained(str(model_path))
        if _DEVICE == "cuda":
            _ASR_MODEL = _ASR_MODEL.to("cuda")
        _ASR_MODEL.eval()
    return _ASR_MODEL, _ASR_PROCESSOR

def _load_text():
    global _TEXT_PIPE
    if _TEXT_PIPE is None:
        model_path = _MODEL_PATH / "chinese-sentiment"
        _TEXT_PIPE = pipeline("text-classification", model=str(model_path), device=0 if _DEVICE == "cuda" else -1)
    return _TEXT_PIPE

def transcribe(audio_path: str) -> str:
    import librosa
    
    model, processor = _load_asr()
    audio, sr = librosa.load(str(audio_path), sr=16000)
    
    if len(audio) < 1600:
        return ""
    
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
    input_features = inputs.input_features
    
    if _DEVICE == "cuda":
        input_features = input_features.to("cuda")
    
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="<|zh|>", task="transcribe")
    
    with torch.no_grad():
        predicted_ids = model.generate(
            input_features, 
            forced_decoder_ids=forced_decoder_ids,
            max_new_tokens=256,
            temperature=0.0
        )
    
    result = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    print(f"[ASR] Result: {result}")
    return result

def predict_audio(path: str) -> np.ndarray:
    labels = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
    return np.array([0.2, 0.3, 0.1, 0.1, 0.1, 0.2])

def predict_text(text: str) -> np.ndarray:
    labels = ["neutral", "happy", "sad", "angry", "anxious", "surprised"]
    try:
        pipe = _load_text()
        res = pipe(text[:512])[0]
        label_map = {"positive": "happy", "negative": "sad", "neutral": "neutral"}
        mapped = label_map.get(res["label"], "neutral")
        vec = np.zeros(6)
        vec[labels.index(mapped)] = res["score"]
        return vec
    except:
        vec = np.zeros(6)
        vec[0] = 0.6
        return vec