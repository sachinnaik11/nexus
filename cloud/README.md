# 🌐 NEXUS 24/7 CLOUD NODE ARCHITECTURE

This module allows **NEXUS V1 to run 24 hours a day, 7 days a week in the cloud**, completely uninterrupted—even if your Windows laptop is shut down and your phone is switched off!

---

## 🚀 How It Works When Both Devices Are Offline

```
┌────────────────────────────────────────────────────────┐
│               24/7 NEXUS CLOUD NODE                    │
│      (Runs continuously on Free Cloud / VPS)           │
│                                                        │
│  [Autopilot Engine] ──> Researches viral YouTube SEO   │
│                     ──> Creates YouTube Shorts memes   │
│                     ──> Checks upload deadlines        │
│                                                        │
│  [Gemini 3.5 Cloud] ──> Generates high-CTR packages    │
│                                                        │
│  [Telegram Bot]     ──> Alerts you on ANY smartphone / │
│                         web browser with [Approve]     │
└───────────────────────────┬────────────────────────────┘
                            │ (Syncs when you wake up)
                            ▼
┌────────────────────────────────────────────────────────┐
│               DESKTOP NEXUS V1 (Windows)               │
│                                                        │
│  When your laptop powers on:                           │
│  • Pulls all approved drafts from the cloud            │
│  • Imports viral titles & meme cards into memory       │
│  • Opens YouTube Studio & CapCut ready for action      │
└────────────────────────────────────────────────────────┘
```

---

## ⚡ 1. How to Test the Cloud Server Locally

You can test the cloud node right on your PC right now:

```bash
python -m cloud.nexus_cloud_server
```

You will see:
```text
NEXUS 24/7 CLOUD SERVER ONLINE at http://0.0.0.0:8000
Health check endpoint: http://localhost:8000/health
Desktop sync endpoint: http://localhost:8000/api/sync
```

Test it in your browser or with curl:
- Open `http://localhost:8000/health` to view live server status.
- Trigger an autonomous draft:
  ```bash
  curl -X POST http://localhost:8000/api/generate_draft -H "Content-Type: application/json" -d "{\"topic\": \"GTA 5 secret mission\"}"
  ```

---

## 📱 2. How to Connect Telegram Bot (Control from Any Phone/Browser)

1. Open Telegram on your phone or computer.
2. Search for `@BotFather` and click **Start**.
3. Send `/newbot`, give it a name (e.g., `MyNexusAssistantBot`), and choose a username.
4. BotFather will give you a **Bot Token** (e.g. `123456789:ABCdef...`).
5. Open your `.env` file and add:
   ```env
   TELEGRAM_BOT_TOKEN="your_bot_token_here"
   ```
6. Start a chat with your new bot and send `/start`.
7. Now, whenever a viral draft or upload reminder is ready, NEXUS will ping your Telegram! You can reply `approve draft_...` from anywhere in the world.

---

## ☁️ 3. Deploying 24/7 in the Cloud (Free Options)

### Option A: Render (Free Web Service)
1. Push this repository to your GitHub account (make sure `.env` is never pushed; Git already ignores it).
2. Go to [render.com](https://render.com) and create a free account.
3. Click **New +** -> **Web Service** -> select your repo.
4. Render will automatically detect `cloud/render.yaml` or you can set:
   - **Build Command**: `pip install -r cloud/requirements.txt`
   - **Start Command**: `python -m cloud.nexus_cloud_server`
5. In the **Environment Variables** tab, add:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `TELEGRAM_BOT_TOKEN`: (Optional) Your Telegram bot token
   - `CHANNEL_NICHE`: `Gaming & Tech Entertainment`
6. Click **Deploy**! Render will give you a live URL like `https://nexus-cloud-xxxx.onrender.com`.
7. In your local `.env`, set:
   ```env
   NEXUS_CLOUD_URL="https://nexus-cloud-xxxx.onrender.com"
   ```

### Option B: Railway / Fly.io / HuggingFace Spaces / VPS
You can also deploy anywhere with Docker using `cloud/Dockerfile`:
```bash
docker build -f cloud/Dockerfile -t nexus-cloud .
docker run -p 8000:8000 -e GEMINI_API_KEY="your_key" nexus-cloud
```
