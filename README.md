# CampusX AI Voice Agent (Powered by Pipecat & Google Gemini Live)

A real-time, bidirectional voice agent built with [Pipecat](https://docs.pipecat.ai/) and Google's **Gemini Live API** (native speech-to-speech). This agent serves as a voice assistant for CampusX, guiding callers through courses (DSMP, DAMP), mentorship programs, and scheduling 20-minute guidance sessions with automated slot management.

---

## Key Features

- **Native Speech-to-Speech**: Ultra-low latency voice conversation powered by Google Gemini Live (`models/gemini-2.5-flash-native-audio-preview`).
- **CampusX Knowledge Retrieval**:
  - Local verified knowledge base for instant information on courses, curriculum, fees, and career support.
  - Optional semantic search integration via **pipecat-moss**.
- **Interactive Guidance Booking**:
  - Automated slot availability generation and booking management.
  - Persistent SQLite storage with unique booking reference IDs and email validation.
- **Natural Conversation Handling**: Real-time turn detection using Silero VAD, interruption / barge-in support, and intelligent filler audio during tool calls.
- **Browser-Ready WebRTC**: Instant web interface served via Pipecat's development runner.
- **Progressive Learning Stages**: Includes step-by-step example stages (`stages/00` to `stages/10`) demonstrating the evolution from basic WebRTC frames to a full production-ready voice agent.

---

## Core Components

| Module | Location | Purpose |
|--------|----------|---------|
| `main.py` | Root | Main executable CLI for running the bot, checking bookings, and building MOSS index |
| `agent.py` | `src/campusx_voice_agent/` | Bot assembly: Gemini Live service, context aggregation, tools, and audio pipeline |
| `tools.py` | `src/campusx_voice_agent/` | Function tools: knowledge search, slot availability, SQLite booking persistence |
| `pipeline.py` | `src/campusx_voice_agent/` | WebRTC transport setup, turn management strategies, and metrics reporting |
| `knowledge_base.py` | `src/campusx_voice_agent/` | Local document search engine |
| `moss.py` / `moss_index.py` | `src/campusx_voice_agent/` | Semantic RAG processor and indexing tools |
| `bookings.py` | `src/campusx_voice_agent/` | CLI table viewer for stored guidance bookings |
| `stages/` | `stages/` | Educational step-by-step implementations from raw frames to full agent |

---

## Prerequisites

- **Python**: 3.12+
- **Google AI Studio API Key**: Access to Gemini Live native-audio models
- **Modern Browser**: Chrome, Firefox, Edge, or Brave (WebRTC support with microphone permission)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>/AI_Voice

# Create virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies with pip
pip install -e ".[dev]"

# Or using uv (recommended for fast installs)
uv sync --dev
```

---

## Configuration

1. Copy `.env.template` to `.env`:
   ```bash
   cp .env.template .env
   ```
2. Configure your environment variables in `.env`:

```env
# Required: Google Gemini API Key (Google AI Studio)
GOOGLE_API_KEY=your-google-ai-studio-key

# Optional: Gemini model and voice configuration
GOOGLE_GEMINI_MODEL=models/gemini-2.5-flash-native-audio-preview-12-2025
GOOGLE_GEMINI_VOICE=Puck

# Optional: Custom database path for bookings (defaults to data/guidance_bookings.db)
# GUIDANCE_DB_PATH=data/guidance_bookings.db

# Optional: MOSS semantic retrieval configuration
# MOSS_PROJECT_ID=...
# MOSS_PROJECT_KEY=...
# MOSS_INDEX_NAME=...
# MOSS_TOP_K=5
# MOSS_ALPHA=0.8
# MOSS_MODEL_ID=moss-minilm
```

---

## Running the Agent

### 1. Launch the Voice Agent (WebRTC UI)

```bash
# With uv
uv run python main.py

# Or directly with python
python main.py
```

- Open your browser at **`http://localhost:7860`**.
- Grant microphone access.
- Start speaking naturally to interact with the voice agent.

### 2. View Saved Bookings

Check bookings stored in SQLite from the command line:

```bash
uv run python main.py bookings
```

### 3. (Optional) Build MOSS Semantic Index

If you are using MOSS for semantic knowledge base search:

```bash
uv run python main.py moss-index
```

---

## Step-by-Step Architecture Stages

The `stages/` directory contains complete standalone scripts demonstrating how the voice agent is constructed incrementally:

| Stage | Script | Description |
|-------|--------|-------------|
| `00` | `00_empty_project.py` | Verifies environment setup and base imports |
| `01` | `01_transport_and_frames.py` | WebRTC audio streaming into Pipecat frames |
| `02` | `02_cloud_stt.py` | Real-time speech-to-text transcript processing |
| `03` | `03_turn_detection_and_context.py` | Silero VAD, user turn boundaries, context aggregation |
| `04` | `04_llm_without_identity.py` | Basic LLM integration without business logic |
| `05` | `05_system_prompt.py` | Persona grounding, booking instructions, and conversation guardrails |
| `06` | `06_moss_create_index.py` | Semantic chunking and vector index creation |
| `07` | `07_moss_rag_before_llm.py` | Context enrichment with MOSS RAG before model generation |
| `08` | `08_tts_audio_frames.py` | Audio synthesis from assistant responses |
| `09` | `09_conversation_memory.py` | Bidirectional audio streaming with conversation memory |
| `10` | `10_final_voice_agent.py` | Complete agent with function calling, SQLite booking, interruption, and filler speech |

---

## Extending the Project

- **Add Knowledge Base Content**: Place `.md` or `.txt` files into `data/knowledge_base/`.
- **Add Function Tools**: Define your custom tool with `FunctionCallParams` in `src/campusx_voice_agent/tools.py` and register it in `GUIDANCE_TOOLS`.
- **Tune Bot Behavior**: Update prompt guidelines and policies in `GUIDANCE_SYSTEM_PROMPT` inside `src/campusx_voice_agent/tools.py`.

---

## License

This project is licensed under the MIT License.
