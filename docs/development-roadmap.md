# Development Roadmap

## Current Priorities

1. Stabilize the chat pipeline.
2. Add a campus knowledge RAG module.
3. Add mood logs and long-term mood visualization.
4. Add life records with text and images.
5. Add an animated companion only after data and conversation quality are stable.

## RAG Preparation

Prepare documents with clear metadata:

- school
- college
- category
- title
- source URL
- publish date
- effective date
- raw content

Recommended first categories:

- course selection
- scholarship rules
- comprehensive evaluation
- recommendation for postgraduate study
- competitions
- volunteer service
- academic planning

Start with Markdown or plain text documents. Add PDF/DOCX parsing later.

## TTS Direction

Current code uses `edge-tts` first and does not enable local fallback by default.

No Hugging Face TTS model is required for the current implementation.

If you later want a local neural TTS model, evaluate these separately:

- `FunAudioLLM/CosyVoice2-0.5B`
- `fishaudio/fish-speech-1.5`
- `2Noise/ChatTTS`

These models are larger than the current project and should be run as a separate TTS service instead of being imported directly into the FastAPI request path.

## Suggested Backend Modules

- `chat`: existing real-time conversation.
- `knowledge`: document ingestion and retrieval.
- `mood`: daily mood logs and visualization data.
- `records`: life records, images, and timeline.
- `profile`: long-term user profile and preferences.

## Suggested AI Modules

- `ai/rag`: document retrieval and context building.
- `ai/memory`: mood timeline and user profile summaries.
- `ai/llm`: response generation and prompt policy.
- `ai/tts`: speech synthesis providers.
- `ai/asr`: speech recognition providers.

## Data Safety

Do not commit these paths:

- `backend/data/`
- `models/`
- `.env`
- uploaded audio
- generated TTS files
- user photos
