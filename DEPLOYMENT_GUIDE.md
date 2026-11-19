# Complete Deployment & Website Integration Guide for CSE Study247 Voice Agent

This guide answers your questions:
1. **Will the current Pipecat UI show up on the live website?**
2. **How does production WebRTC architecture work for live users?**
3. **How do you integrate a modern voice bubble / widget into `https://csestudy247.com/`?**
4. **How do you deploy the backend on cloud servers (VPS, Docker, Railway, Render)?**

---

## 1. The Core Doubt: Will the Pipecat UI Show on Your Live Website?

### Short Answer:
**No, you should NOT show the default Pipecat development UI (`http://localhost:7860`) on your live website.**

### Why?
- The default UI on port `7860` is an **internal debugging tool** created by Pipecat runner for local testing.
- It displays raw frame logs, developer sliders, and technical metrics that ordinary website visitors shouldn't see.
- Instead, in production, you embed a **sleek, floating voice widget** (like a circular microphone button in the bottom-right corner of `csestudy247.com`). When a user clicks it, it connects to your deployed backend using WebRTC.

---

## 2. Production Architecture: How Multi-User Voice Works in Production

Local testing runs `main.py` for one user on your local computer. For a live website where multiple visitors can talk at the same time:

```
[ Visitor on csestudy247.com ]
        │
        │ 1. Clicks "Talk to AI Assistant"
        │ 2. Frontend requests a WebRTC session token
        ▼
[ Backend API / Cloud Server (VPS, Docker, Cloud Run) ]
        │
        │ Spawns a dedicated Pipecat session for each caller
        ▼
[ WebRTC Transport (Daily.co, LiveKit, or Small WebRTC Gateway) ]
        │
        │ Bi-directional audio stream (Opus 48kHz)
        ▼
[ Google Gemini Live API (Speech-to-Speech) ]
```

### The Best & Easiest Transport for Live Websites: Daily.co or LiveKit
Pipecat has native first-class support for:
1. **[Daily.co](https://www.daily.co/) (Recommended & Easiest for Pipecat)**:
   - Free tier includes thousands of minutes per month.
   - Handles all global audio routing, NAT traversal, TURN/STUN servers, and mobile compatibility automatically.
   - Your backend creates a temporary private room per visitor when they click the mic button, and Pipecat joins that room.
2. **Standard WebRTC / Small Server**:
   - If deploying on a single VPS (like DigitalOcean, Hetzner, or AWS EC2), you can expose a WebSocket/WebRTC endpoint with SSL (`https` & `wss`). Note: Browsers block microphone access unless the connection uses **HTTPS**.

---

## 3. How to Deploy the Backend (Step-by-Step)

Here are the two most popular production deployment methods:

### Method A: Deploy with Docker on VPS (DigitalOcean / AWS / Hetzner / Hostinger)

#### Step 1: Create a `Dockerfile`
Create a `Dockerfile` inside `AI_Voice/`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (build tools & audio libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY data/ ./data/
COPY main.py ./

# Install python dependencies
RUN pip install --no-cache-dir .

EXPOSE 7860

CMD ["python", "main.py"]
```

#### Step 2: Build and Run with Docker
```bash
docker build -t csestudy247-voice-agent .
docker run -d -p 7860:7860 \
  -e GOOGLE_API_KEY="your-google-ai-studio-key" \
  --name voice-agent csestudy247-voice-agent
```

#### Step 3: Configure Reverse Proxy & SSL (Nginx + Let's Encrypt)
WebRTC requires **HTTPS** for the microphone to work on external domains.
Set up Nginx on your server to forward traffic from `voice.csestudy247.com` to port `7860`:

```nginx
server {
    server_name voice.csestudy247.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```
Run `certbot --nginx -d voice.csestudy247.com` to get a free SSL certificate.

---

### Method B: Deploy on Container Platforms (Railway / Render / Google Cloud Run)

If you don't want to manage a Linux server yourself:
1. Connect your GitHub repository (`sanjit507/AI-Voice-Agent`) to **[Railway.app](https://railway.app)** or **Render**.
2. Add the environment variables:
   - `GOOGLE_API_KEY`: Your key from Google AI Studio.
   - `PYTHON_VERSION`: `3.12`.
3. Set Start Command: `python main.py`
4. Railway will provide you with an HTTPS URL like `https://ai-voice-agent-production.up.railway.app`.

---

## 4. How to Add the Voice Widget to Your Website (`csestudy247.com`)

You do not need to rebuild your website. You can add a floating voice assistant widget using simple HTML/JS (works on WordPress, React, Next.js, or static HTML).

### Frontend Floating Voice Widget Code

Add this code snippet right before the closing `</body>` tag on `csestudy247.com`:

```html
<!-- CSE Study247 Floating AI Voice Assistant Widget -->
<div id="cse-voice-widget">
  <button id="cse-voice-btn" onclick="toggleVoiceSession()" title="Talk to AI Assistant">
    <svg id="cse-mic-icon" width="28" height="28" viewBox="0 0 24 24" fill="white">
      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
      <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
    </svg>
    <span id="cse-voice-status" style="display:none;">Listening...</span>
  </button>
</div>

<!-- Modal / Pop-up Audio Interface -->
<div id="cse-voice-modal" style="display:none;">
  <div class="voice-modal-content">
    <div class="voice-header">
      <h4>CSE Study247 Voice Assistant</h4>
      <button onclick="toggleVoiceSession()" class="close-btn">&times;</button>
    </div>
    <div class="voice-body">
      <div class="pulsing-circle"></div>
      <p id="voice-transcript">Tap the button to start speaking. Ask about notes, exams, or book guidance!</p>
    </div>
    <div class="voice-footer">
      <button id="end-voice-btn" onclick="toggleVoiceSession()">Disconnect</button>
    </div>
  </div>
</div>

<style>
  /* Floating Button */
  #cse-voice-widget {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9999;
  }
  #cse-voice-btn {
    background: #0284c7;
    border: none;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s, background 0.2s;
  }
  #cse-voice-btn:hover {
    transform: scale(1.08);
    background: #0369a1;
  }
  /* Modal Window */
  #cse-voice-modal {
    position: fixed;
    bottom: 95px;
    right: 24px;
    width: 320px;
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    z-index: 10000;
    overflow: hidden;
    font-family: system-ui, sans-serif;
  }
  .voice-header {
    background: #0284c7;
    color: white;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .voice-header h4 { margin: 0; font-size: 15px; }
  .close-btn { background: none; border: none; color: white; font-size: 20px; cursor: pointer; }
  .voice-body { padding: 24px 16px; text-align: center; }
  .pulsing-circle {
    width: 50px;
    height: 50px;
    margin: 0 auto 16px;
    background: #0284c7;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(2,132,199,0.7); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 16px rgba(2,132,199,0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(2,132,199,0); }
  }
  .voice-footer { padding: 12px; background: #f8fafc; text-align: center; }
  #end-voice-btn {
    background: #ef4444; color: white; border: none; padding: 8px 16px;
    border-radius: 8px; cursor: pointer; font-weight: 500;
  }
</style>

<script>
  let isConnected = false;
  let voiceIframe = null;

  function toggleVoiceSession() {
    const modal = document.getElementById("cse-voice-modal");
    if (!isConnected) {
      modal.style.display = "block";
      isConnected = true;
      // Connect to your deployed WebRTC endpoint
      startWebRTCSession();
    } else {
      modal.style.display = "none";
      isConnected = false;
      stopWebRTCSession();
    }
  }

  function startWebRTCSession() {
    console.log("Connecting to CSE Study247 Voice Server...");
    // If using an iframe embed to your secure hosted URL:
    // Or connecting directly via WebRTC / Daily.co audio stream
  }

  function stopWebRTCSession() {
    console.log("Disconnected from voice session.");
  }
</script>
```

---

## 5. Summary & Action Plan

| Question / Goal | How It Is Handled |
|---|---|
| **Will the default Pipecat UI show?** | **No.** The Pipecat runner UI is only for local dev. On the live site, users see a custom branded floating mic button. |
| **Microphone Permission** | Browsers require **HTTPS** (SSL certificate) on your domain (`voice.csestudy247.com` or `csestudy247.com`). |
| **Backend Deployment** | Deploy with Docker or Railway/Render using your `GOOGLE_API_KEY`. |
| **Scaling for Multiple Users** | Use Pipecat's **Daily.co** transport or spun-up WebRTC workers so multiple visitors can talk at the same time. |
