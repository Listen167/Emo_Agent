# AI Module Layout

`ai/` is organized by capability. Backend code should depend on each package's service API, not directly on provider internals.

- `asr/`: speech-to-text. SenseVoice is tried first, then Whisper fallback.
- `emotion/`: text emotion prediction plus audio/text emotion fusion.
- `llm/`: OpenAI-compatible chat generation and prompt assembly.
- `tts/`: speech synthesis and TTS text sanitization.
- `rag/`: campus knowledge import and retrieval.
- `memory/`: reserved for long-term profile, mood timeline, and life-record summarization.
- `prompts/`: prompt templates, currently `chat_system.md`.

Design rule: orchestration belongs in `backend/app/services/conversation_orchestrator.py`; model/provider packages only expose focused capabilities.
