# Emo Agent

Emo Agent is a campus-focused emotional companion chat project. It supports text or voice input, speech-to-text, emotion analysis, LLM response generation, optional TTS playback, chat history storage, and a first usable RAG flow for campus knowledge.

## Features

- Text and voice chat.
- ASR: SenseVoice first, Whisper fallback.
- Emotion analysis: text emotion prediction plus audio/text fusion.
- LLM response: OpenAI-compatible API, emotion-aware system prompt.
- TTS: supports `kokoro`, `edge`, and `windows` providers. `kokoro` is recommended for stable local Chinese speech.
- Chat history: stores user and assistant messages with timestamps.
- RAG: imports Markdown campus documents and retrieves relevant chunks for answers.

## Project Structure

```text
Emo_Agent/
├─ ai/
│  ├─ asr/              # speech-to-text provider and service
│  ├─ emotion/          # text emotion provider and fusion service
│  ├─ llm/              # prompt assembly and LLM service
│  ├─ tts/              # TTS provider, service, and text sanitizer
│  ├─ rag/              # knowledge import and retrieval
│  ├─ memory/           # reserved for long-term memory
│  └─ prompts/          # prompt templates
├─ backend/             # FastAPI backend
│  ├─ app/
│  │  ├─ api/           # HTTP routes
│  │  ├─ core/          # config and database
│  │  ├─ models/        # SQLAlchemy models
│  │  ├─ schemas/       # Pydantic schemas
│  │  └─ services/      # conversation orchestration
│  └─ requirements.txt
├─ frontend/            # Vue 3 frontend
├─ knowledge/raw/       # Markdown files for RAG import
├─ tests/               # basic unit tests
└─ docs/                # development notes
```

## Backend Setup

```powershell
cd backend
pip install -r requirements.txt
copy .env.example .env
python main.py
```

Edit `backend/.env` before running real LLM calls:

```env
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL=deepseek-chat
RAG_ENABLED=false
TTS_PROVIDER=edge
TTS_ALLOW_WINDOWS_FALLBACK=false
```

For local Kokoro Chinese TTS:

```env
TTS_ENABLED=true
TTS_PROVIDER=kokoro
KOKORO_MODEL_DIR=D:\PragramFile\VScode\Emo_Agent\models\kokoro-zh
KOKORO_VOICE=zf_001
KOKORO_LANG_CODE=z
KOKORO_SAMPLE_RATE=24000
KOKORO_SPEED=1.0
```

The available Chinese voice names are the `.pt` files under `models/kokoro-zh/voices/`, for example `zf_001` or `zm_009`.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:5173`

Backend default URL: `http://localhost:8000`

## RAG Knowledge Import

Put campus knowledge Markdown files in `knowledge/raw/`. Each file can use simple front matter:

```markdown
---
title: 国家励志奖学金评定说明
school: 示例大学
college: 计算机学院
category: 奖学金
source: https://example.edu/policy
year: 2026
---

正文内容...
```

Import documents:

```powershell
python -m ai.rag.ingest --dir knowledge/raw
```

Enable retrieval in `backend/.env`:

```env
RAG_ENABLED=true
```

## Tests

Run basic unit tests from the project root:

```powershell
python -m unittest discover -s tests
```

Current basic coverage:

- LLM prompt assembly.
- TTS text sanitization.
- Pipeline no-audio/no-text fallback reply.

## Git Ignore Policy

The repository should not upload runtime data, local models, environment files, build output, or dependencies.

Ignored examples:

- `backend/data/`
- `models/`
- `.env`
- `frontend/node_modules/`
- `frontend/dist/`
- `*.wav`, `*.mp3`, `*.webm`
- SQLite database files

Before pushing:

```powershell
git status
git add .
git commit -m "Refactor AI services and add RAG foundation"
git push origin main
```
