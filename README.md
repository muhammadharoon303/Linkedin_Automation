# 🚀 Autonomous Social AI Content Engine & LinkedIn Publisher

An end-to-end, zero-click, 100% automated social media content engine built with **FastAPI (Python)**, **Flutter (Dart)**, and **Google Gemini AI**. Designed to generate, design, schedule, and publish high-authority technical posts and photorealistic 3D visuals to LinkedIn with zero manual intervention.

---

## 🌟 Key Features

- **100% Headless Automated Publishing**: Direct integration with LinkedIn's official `ugcPosts` and `assets` REST API. Posts go live without opening any browser or clicking buttons.
- **AI-Powered 3D Visual Generation**: Tailored, cinematic 16:9 3D AI visual generation using Google Gemini / Imagen for every technical topic.
- **Smart Queue Scheduling**: Integrated `APScheduler` monitors the queue and auto-publishes during high-engagement peak time windows (Mon-Fri).
- **Cross-Platform Mobile App**: Flutter companion app for real-time publishing telemetry, campaign inspection, and manual override.
- **Local AI Ready**: Supports local LLMs via Ollama alongside cloud models for caption generation and prompt engineering.

---

## 🏗️ Architecture

```
linkedin_Project/
├── backend/                  # FastAPI Backend & Scheduling Service
│   ├── app/
│   │   ├── api/v1/           # OAuth, Posts, Campaigns, Analytics Endpoints
│   │   ├── models/           # SQLAlchemy DB Models (Post, Campaign, Account, Log)
│   │   ├── services/         # Publishers (LinkedIn, etc.), Card Generator, Scheduler
│   │   └── main.py           # FastAPI Application Entrypoint
│   ├── generated_media/      # 3D Photorealistic AI Graphics & Infocards
│   ├── .env.example          # Environment Variable Configuration Template
│   └── requirements.txt      # Python Dependencies
├── mobile_app/               # Cross-Platform Flutter Mobile Companion
│   ├── lib/                  # Screens, Providers, Models, Widgets
│   └── pubspec.yaml          # Flutter Dependencies
└── README.md
```

---

## ⚡ Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Configure your credentials in `backend/.env`:
- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- `LINKEDIN_REDIRECT_URI`
- `GEMINI_API_KEY`

Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Flutter Mobile App

```bash
cd mobile_app
flutter pub get
flutter run
```

---

## 🛡️ License
MIT License. Built with ❤️ by Muhammad Haroon.
