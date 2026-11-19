# Complete Project Documentation: Real-Time AI Voice Agent for CSE Study247

> **Platform**: [CSE Study247 (csestudy247.com)](https://csestudy247.com/)  
> **Technologies**: Python 3.12, Pipecat AI, Google Gemini Live API, WebRTC, Silero VAD, SQLite  
> **Repository**: [GitHub - sanjit507/AI-Voice-Agent](https://github.com/sanjit507/AI-Voice-Agent.git)  

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Key Features & Capabilities](#3-key-features--capabilities)
4. [Deep-Dive: How the Code Works](#4-deep-dive-how-the-code-works)
5. [Prerequisites](#5-prerequisites)
6. [Step-by-Step Installation & Setup](#6-step-by-step-installation--setup)
7. [Running the Voice Agent](#7-running-the-voice-agent)
8. [Testing & Sample Voice Prompts](#8-testing--sample-voice-prompts)
9. [Project Directory & File Guide](#9-project-directory--file-guide)
10. [Troubleshooting & FAQ](#10-troubleshooting--faq)

---

## 1. Project Overview

The **CSE Study247 AI Voice Agent** is a production-grade, real-time bidirectional conversational voice assistant. Unlike traditional voice bots that rely on slow, multi-step chains (converting audio to text via Whisper, waiting for an LLM response, and then running a separate text-to-speech synthesizer), this system uses **Google's Gemini Live API** (`models/gemini-2.5-flash-native-audio-preview`) via the **Pipecat framework**.

Gemini Live processes native incoming speech audio frames and produces direct streaming audio responses with near-zero latency, creating a smooth, natural telephone-like voice conversation directly in the browser.

### What the Voice Agent Does:
- **Answers Website & Study Inquiries**: Explains subjects, lecture notes (DSA, Python, Java, OS, DBMS, Networks), and download links on [csestudy247.com](https://csestudy247.com/).
- **Guides Exam Aspirants**: Provides syllabus details and previous year question paper (PYQ) references for **GATE CS/DA, ISRO, DRDO, UGC NET**, and **SBTE Bihar Polytechnic Diploma** exams.
- **Schedules Mentorship Calls**: Interactively checks calendar slots and books free 20-minute 1-on-1 career/study guidance sessions into an SQLite database.
- **Supports Natural Interruptions (Barge-in)**: Callers can speak or interrupt at any moment, and the bot immediately stops talking and listens.

---

## 2. High-Level Architecture

The following diagram illustrates how user voice streams flow through the browser, WebRTC layer, Pipecat pipeline, local tools, and Google Gemini Live:

```
[ User Microphone (Browser) ]
              │ (WebRTC Audio Stream)
              ▼
   [ Pipecat WebRTC Transport ]
              │
              ▼
    [ AudioTrace / VAD Layer ]  <--- Silero VAD (Detects human speech boundaries)
              │
              ▼
 [ LLMContext / Frame Aggregator ]
              │
              ├──────────► [ Google Gemini Live API ]
              │            (Native Audio In -> Native Audio Out)
              │                     │
              │ (Function Calling)  │ (Streaming Audio Frames)
              ▼                     ▼
[ Local Tools & Knowledge Base ]  [ Assistant Audio Output ]
 - search_knowledge_base_tool               │
 - get_available_guidance_slots             ▼
 - book_free_guidance_session     [ Browser Speaker Output ]
```

---

## 3. Key Features & Capabilities

| Feature | Description |
|---|---|
| **Native Speech-to-Speech** | Powered by Gemini Live preview models for sub-second responses without separate STT and TTS models. |
| **WebRTC Transport** | Operates over standard WebRTC with ultra-low latency directly in any modern web browser. |
| **Local Knowledge Retrieval** | Fast, deterministic text search across local markdown files for verified platform information. |
| **Automated Slot Booking** | SQLite-backed database system with input validation (email checks, slot collision prevention). |
| **Turn Detection & Barge-In** | Silero VAD detects user turns; users can interrupt the assistant without waiting for it to finish speaking. |
| **Spoken Filler Feedback** | While a database or tool query is running, the agent can stream brief conversational fillers ("Let me check that for you"). |

---

## 4. Deep-Dive: How the Code Works

### A. The Orchestrator (`main.py`)
`main.py` is the single CLI entry point:
- Running `python main.py` launches the Pipecat development runner on port `7860`.
- Running `python main.py bookings` prints a clean CLI table of all guidance sessions booked by callers.
- Running `python main.py moss-index` builds an offline semantic vector index (optional).

### B. Agent Pipeline (`src/csestudy247_voice_agent/agent.py`)
This file configures:
1. **`GeminiLiveLLMService`**: Connects with your Google AI Studio API key, setting the model to `gemini-2.5-flash-native-audio-preview` and selecting the voice (`Puck`).
2. **`LLMContext`**: Stores the initial system instruction and available tools.
3. **`LLMContextAggregatorPair`**: Pairs user audio input and bot responses to maintain active conversational history.
4. **`run_pipeline`**: Starts the asynchronous audio processing pipeline.

### C. Function Calling & Tools (`src/csestudy247_voice_agent/tools.py`)
The LLM can execute three deterministic Python functions:
1. **`search_knowledge_base_tool(query)`**: Scans local markdown knowledge files in `data/knowledge_base/` for verified facts on exams, syllabus, or notes.
2. **`get_available_guidance_slots(time_preference)`**: Generates available slots (morning, afternoon, evening) over the next 7 days, excluding already reserved times in the database.
3. **`book_free_guidance_session(caller_name, email, learning_goal, preferred_slot)`**: Validates details and writes the booking into `data/guidance_bookings.db` with a unique ID (e.g., `CX-A1B2C3D4`).

### D. Knowledge Base Engine (`src/csestudy247_voice_agent/knowledge_base.py`)
Performs token-overlap and phrase-matching over files in `data/knowledge_base/`:
- `csestudy247_overview.md`: Contains site overview, contact emails, mobile app details, and exam resources.
- `csestudy247_courses_and_roadmaps.md`: Contains tech roadmaps (DSA, AI/ML, Voice Agents, Web Dev) and FAQ answers.

---

## 5. Prerequisites

Before setting up the project, make sure you have:
1. **Operating System**: Windows 10/11, macOS, or Linux.
2. **Python**: Version **3.12** installed (verify via `python --version`).
3. **Google AI Studio Key**: A free API key from [Google AI Studio](https://aistudio.google.com/).
4. **Microphone & Browser**: Google Chrome, Microsoft Edge, Brave, or Firefox.

---

## 6. Step-by-Step Installation & Setup

### Step 1: Clone the Repository
Open your terminal (PowerShell, Command Prompt, or Bash) and clone the repo:
```bash
git clone https://github.com/sanjit507/AI-Voice-Agent.git
cd AI-Voice-Agent/AI_Voice
```

### Step 2: Create a Python 3.12 Virtual Environment
It is recommended to run this project inside a clean virtual environment:

**On Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
Install the project in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

*(Alternatively, if you use [uv](https://github.com/astral-sh/uv)):*
```bash
uv sync --dev
```

### Step 4: Configure Environment Variables
Copy `.env.template` to create your local `.env` file:

**On Windows:**
```powershell
copy .env.template .env
```

**On Linux / macOS:**
```bash
cp .env.template .env
```

Open `.env` in any text editor and fill in your Google API key:
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
GOOGLE_GEMINI_MODEL=models/gemini-2.5-flash-native-audio-preview-12-2025
GOOGLE_GEMINI_VOICE=Puck
```

> 🔒 **Security Note**: Never commit your `.env` file to GitHub. The project's `.gitignore` automatically prevents `.env` and `.venv/` from being pushed.

---

## 7. Running the Voice Agent

### Option 1: Start the Browser Voice Bot
Launch the server:
```bash
python main.py
```
*(or using uv: `uv run python main.py`)*

1. Look for terminal output showing:
   ```text
   Starting WebRTC development runner at http://localhost:7860
   ```
2. Open **`http://localhost:7860`** in your browser.
3. Click the connect/start button and **Allow Microphone Access** when prompted by your browser.
4. The assistant will greet you: *"Hello! Welcome to CSE Study247. How can I help you today?"*

### Option 2: View Guidance Bookings in Terminal
Whenever users schedule guidance sessions through voice, view them with:
```bash
python main.py bookings
```

---

## 8. Testing & Sample Voice Prompts

Speak clearly into your microphone to test different capabilities:

| Intent | Sample Spoken Question | Expected Assistant Action |
|---|---|---|
| **About Platform** | *"What is CSE Study247 and what do you offer?"* | Summarizes notes, exams, mobile app, and site features from KB. |
| **Notes & Subjects** | *"Do you provide handwritten notes for Data Structures and OS?"* | Confirms available subjects and mentions Love Babbar / Striver sheets. |
| **Exam Questions** | *"Can I get syllabus and question papers for GATE and ISRO?"* | Lists available GATE CS/DA and ISRO question paper archives. |
| **Bihar Polytechnic** | *"Do you have notes for SBTE Bihar Computer Science diploma?"* | Confirms semester syllabus, lab programs, and notes for SBTE Bihar. |
| **Modern Roadmaps** | *"Can I learn how to build AI Voice Agents here?"* | Describes tutorials covering Pipecat, Gemini Live, and LangChain. |
| **Book Session** | *"I want to book a free guidance session."* | Initiates multi-turn booking flow (asking goal, preferred slot, name, email). |
| **Contact Support** | *"How can I contact the support team?"* | Mentions `csestudy247help@gmail.com` and the website contact form. |

---

## 9. Project Directory & File Guide

```text
AI_Voice/
├── main.py                                  # Primary CLI controller
├── pyproject.toml                           # Package definition & dependencies
├── .env.template                            # Safe template for credentials
├── data/
│   ├── guidance_bookings.db                 # SQLite database storing bookings
│   └── knowledge_base/                      # Markdown files searched by the bot
│       ├── csestudy247_overview.md          # Platform & exam details
│       ├── csestudy247_courses_and_roadmaps.md # Roadmaps & FAQs
│       └── dsa_python_course_full_curriculum.md # DSA curriculum
├── src/
│   └── csestudy247_voice_agent/
│       ├── agent.py                         # Assembles the Gemini Live speech pipeline
│       ├── tools.py                         # Defines booking & search tool functions
│       ├── knowledge_base.py                # Local text search implementation
│       ├── pipeline.py                      # Pipecat WebRTC transport & turn strategies
│       ├── bookings.py                      # CLI printer for SQLite bookings
│       ├── moss.py                          # Optional MOSS semantic retrieval
│       ├── moss_index.py                    # Optional MOSS indexer
│       └── config.py                        # Path & environment configuration
└── stages/                                  # 11 step-by-step educational pipeline scripts
```

---

## 10. Troubleshooting & FAQ

### 1. Error: `Missing environment variable: GOOGLE_API_KEY`
- **Cause**: The `.env` file does not exist or does not contain `GOOGLE_API_KEY`.
- **Solution**: Ensure `.env` is created in the `AI_Voice/` folder with your key from Google AI Studio.

### 2. Browser shows "Connection Failed" or no audio is heard
- **Cause**: Browser blocked microphone access, or WebRTC could not bind to localhost.
- **Solution**:
  - Check the browser URL address bar and ensure microphone access is toggled to **Allow**.
  - Use Google Chrome or Microsoft Edge for best WebRTC compatibility.

### 3. Can I run this in languages other than English?
- **Yes**: Gemini Live supports multilingual conversations. You can speak to the bot in **Hinglish** or **Hindi**, and it will respond conversationally.

### 4. How do I add more study notes to the bot's knowledge?
- Simply create a new `.md` file inside `AI_Voice/data/knowledge_base/` with your content. The search tool will automatically index and include it on the next user query!

---

*Authored for [CSE Study247](https://csestudy247.com/) | Built with Pipecat & Google Gemini Live*
