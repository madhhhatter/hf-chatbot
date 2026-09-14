# HF Chatbot

A containerized AI chatbot powered by [microsoft/Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct), served through Hugging Face's Inference Providers (via Featherless AI) and deployed as a single Dockerized service on Render.

**🔗 Live demo:** [https://https://hf-chatbot-0yxx.onrender.com//static/index.html](https://https://hf-chatbot-0yxx.onrender.com//static/index.html)
*(Free-tier hosting — first request after a period of inactivity may take 30–60s to spin up.)*

---

## Architecture

```
┌─────────────┐      POST /chat      ┌──────────────┐      Inference Providers      ┌────────────────┐
│  Browser UI  │ ───────────────────▶ │   FastAPI     │ ─────────────────────────────▶ │  Featherless AI │
│ (static/)    │ ◀─────────────────── │  (Dockerized) │ ◀───────────────────────────── │  Phi-3-mini-4k  │
└─────────────┘      JSON reply       └──────────────┘         via Hugging Face        └────────────────┘
                                              │
                                        Deployed on Render
                                        (single web service)
```

The frontend and backend are served from the same Dockerized FastAPI app — no model weights are hosted or loaded locally. Inference runs remotely via Hugging Face's [Inference Providers](https://huggingface.co/docs/inference-providers), routed to Featherless AI, keeping the container lightweight enough to run on a free-tier instance.

## What I built

- **Containerized FastAPI backend** — a REST API (`/chat`, `/health`) wrapped in a minimal Docker image, with the model itself running remotely rather than loaded in-process
- **Decoupled inference architecture** — chose to call a hosted inference provider instead of self-hosting model weights, trading a small amount of latency for a container that's a fraction of the size and doesn't require a GPU to deploy
- **CORS-secured API** — origin restricted to the app's own deployed domain rather than left open
- **Simple, dependency-light frontend** — a vanilla HTML/JS chat UI served as a static asset from the same service, no frontend framework overhead
- **End-to-end deployment pipeline** — from local Docker testing through to a live, publicly accessible URL, with secrets (Hugging Face token) injected via environment variables rather than hardcoded

## Tech stack

- **Backend:** Python, FastAPI, Uvicorn
- **Model access:** `huggingface_hub` InferenceClient → Hugging Face Inference Providers → Featherless AI
- **Model:** microsoft/Phi-3-mini-4k-instruct
- **Containerization:** Docker
- **Hosting:** Render (free tier)

## Running locally

```bash
# 1. Clone and install
git clone https://github.com/madhhhatter/hf-chatbot.git
cd hf-chatbot
pip install -r requirements.txt

# 2. Set your Hugging Face token (needs "Make calls to Inference Providers" permission)
export HF_TOKEN=hf_your_token_here

# 3. Run
uvicorn app:app --reload
```

Visit `http://localhost:8000/static/index.html` for the chat UI, or `http://localhost:8000/docs` for the interactive API docs.

## Running with Docker

```bash
docker build -t hf-chatbot .
docker run -p 8000:8000 -e HF_TOKEN=hf_your_token_here hf-chatbot
```

## Environment variables

| Variable   | Description                                               |
|------------|-------------------------------------------------------------|
| `HF_TOKEN` | Hugging Face access token with Inference Providers permission |

## Notes

- This app is stateless — no database or persistent storage is used, since each request is a single independent call to the model.
- Running on Render's free tier means the service spins down after ~15 minutes of inactivity; the first request afterward will be slow while it restarts.
