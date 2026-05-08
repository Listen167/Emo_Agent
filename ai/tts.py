import asyncio
import edge_tts
from pathlib import Path

def synthesize(text: str, session_id: str, emotion: str) -> str:
    rate = "+15%" if emotion == "happy" else "-5%" if emotion == "sad" else "0%"
    voice = "zh-CN-YunxiNeural"
    
    out_dir = Path(f"./data/tts/{session_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{emotion}_{len(text)}.mp3"
    
    comm = edge_tts.Communicate(text, voice, rate=rate)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(comm.save(str(out_path)))
    return str(out_path)