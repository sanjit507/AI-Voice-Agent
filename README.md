# CSE Study247 AI Voice Agent (Powered by Pipecat & Google Gemini Live)

A real-time, bidirectional conversational AI voice agent built with [Pipecat](https://docs.pipecat.ai/) and Google's **Gemini Live API** (native speech-to-speech audio streaming). 

This voice assistant is designed for **[CSE Study247](https://csestudy247.com/)**, helping students, job seekers, and engineering aspirants explore computer science study materials, semester notes, competitive exam guides (GATE, ISRO, SBTE Bihar), modern AI/coding roadmaps, and schedule 1-on-1 guidance sessions.

---

## 🌟 Key Features

- **Native Speech-to-Speech**: Ultra-low latency voice conversation powered by Google Gemini Live (`models/gemini-2.5-flash-native-audio-preview`).
- **CSE Study247 Knowledge Retrieval**:
  - Verified local knowledge base covering [csestudy247.com](https://csestudy247.com/) resources:
    - Core CS notes (DSA, C/C++, Python, Java, OS, DBMS, CN, TOC).
    - Competitive exam syllabi & PYQs (GATE CS/DA, ISRO, DRDO, UGC NET, BPSC Teacher).
    - State university & polytechnic board resources (SBTE Bihar Diploma, BEU Bihar, BCECE LE).
    - Developer roadmaps (AI Voice Agents, Pipecat, Gemini Live, LangChain, RAG, FastAPI).
    - Job/internship notifications and practice mock tests.
  - Optional semantic retrieval via **pipecat-moss**.
- **Interactive Mentorship & Guidance Booking**:
  - Dynamic slot availability generation (morning, afternoon, evening).
  - SQLite persistent storage with unique booking reference IDs and email validation.
- **Natural Voice Handling**:
  - Silero VAD (Voice Activity Detection) for precise turn-taking.
  - Barge-in & interruption support so users can speak naturally at any point.
  - Natural audio filler responses during tool execution.
- **WebRTC In-Browser Interface**:
  - Instant browser client served via Pipecat's development runner at `http://localhost:7860`.

---

## 📁 Repository Structure

```text
AI_Voice/
|-- main.py                      # Main entry point (WebRTC bot / CLI bookings / MOSS index)
|-- pyproject.toml               # Project metadata & dependencies
|-- .env.template                # Template for environment variables (API keys)
|-- data/
|   |-- guidance_bookings.db     # SQLite database for scheduled guidance sessions
|   `-- knowledge_base/          # Verified markdown knowledge base
|       |-- csestudy247_overview.md
|       |-- csestudy247_courses_and_roadmaps.md
|       `-- dsa_python_course_full_curriculum.md
|-- src/
|   `-- campusx_voice_agent/
|       |-- agent.py             # Bot wiring: Gemini Live service, aggregators, pipeline
|       |-- tools.py             # Function tools: KB search, slot availability, booking
|       |-- knowledge_base.py    # Local keyword search engine
|       |-- pipeline.py          # Pipecat WebRTC transport & turn management
|       |-- bookings.py          # CLI table viewer for stored bookings
|       |-- moss.py              # Optional MOSS semantic retrieval processor
|       `-- config.py            # Path & environment settings
`-- stages/                      # Step-by-step educational pipeline stages (00 to 10)
```

---

## 📋 Prerequisites

- **Python**: 3.12+
- **Google AI Studio API Key**: Free API key with access to Gemini Live native-audio models from [Google AI Studio](https://aistudio.google.com/).
- **Web Browser**: Chrome, Edge, Firefox, or Brave (WebRTC support with microphone permission).

---

## 🚀 Quick Start Guide

### 1. Clone & Enter the Repository

```bash
git clone https://github.com/sanjit507/AI-Voice-Agent.git
cd AI-Voice-Agent/AI_Voice
```

### 2. Set Up Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Using `pip`:
```bash
pip install -e ".[dev]"
```

Or using `uv` (recommended for faster dependency resolution):
```bash
uv sync --dev
```

---

## ⚙️ Configuration

1. Copy `.env.template` to `.env`:
   ```bash
   # Windows
   copy .env.template .env

   # Linux / macOS
   cp .env.template .env
   ```

2. Add your **Google AI Studio API Key** inside `.env`:
   ```env
   GOOGLE_API_KEY=your_actual_google_api_key_here
   GOOGLE_GEMINI_MODEL=models/gemini-2.5-flash-native-audio-preview-12-2025
   GOOGLE_GEMINI_VOICE=Puck
   ```

*(Note: `.env` and virtual environments are strictly ignored in `.gitignore` to protect your credentials.)*

---

## 🎙️ Running the Voice Agent

### 1. Start the Voice Agent (WebRTC UI)

```bash
# With standard Python
python main.py

# Or with uv
uv run python main.py
```

- Open your browser at: **`http://localhost:7860`**
- Grant microphone access when prompted.
- Start speaking naturally to interact with the assistant!

---

### 2. View Scheduled Guidance Bookings

View all sessions booked by callers through the voice assistant:

```bash
python main.py bookings
# or
uv run python main.py bookings
```

---

### 3. (Optional) Build MOSS Semantic Index

If you choose to enable MOSS semantic RAG:

```bash
python main.py moss-index
```

---

## 💬 Sample Questions You Can Ask the Bot

| Category | Example Question |
|----------|------------------|
| **About Platform** | *"What is CSE Study247 and what resources are available on your website?"* |
| **Study Materials** | *"Do you provide handwritten notes for Data Structures and Operating Systems?"* |
| **Exam Prep** | *"Do you have previous year question papers for GATE CS and ISRO?"* |
| **State Boards** | *"Do you have notes and syllabus for SBTE Bihar Computer Science diploma?"* |
| **Tech Roadmaps** | *"Can I learn how to build AI Voice Agents on csestudy247.com?"* |
| **Pricing** | *"Are the notes and mock tests on csestudy247.com free?"* |
| **Support** | *"How can I contact the CSE Study247 team?"* |
| **Book Session** | *"I would like to book a free 20-minute guidance session."* |

---

## 🛠️ Step-by-Step Learning Stages

The `stages/` folder documents the evolution from scratch to a full agent:

| Stage | Script | Purpose |
|-------|--------|---------|
| `00` | `00_empty_project.py` | Environment setup and sanity check |
| `01` | `01_transport_and_frames.py` | WebRTC transport and incoming audio frames |
| `02` | `02_cloud_stt.py` | Real-time speech-to-text transcript processing |
| `03` | `03_turn_detection_and_context.py` | Silero VAD turn boundaries and context aggregation |
| `04` | `04_llm_without_identity.py` | Direct LLM responses without persona |
| `05` | `05_system_prompt.py` | Persona grounding, guardrails, and conversation rules |
| `06` | `06_moss_create_index.py` | Offline vector index generation |
| `07` | `07_moss_rag_before_llm.py` | RAG retrieval context injection before generation |
| `08` | `08_tts_audio_frames.py` | Text-to-speech audio frame synthesis |
| `09` | `09_conversation_memory.py` | Bidirectional streaming and multi-turn context |
| `10` | `10_final_voice_agent.py` | Complete agent with function calling, SQLite booking, and interruption support |

---

## 📄 License

This project is licensed under the MIT License.
