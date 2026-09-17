import os
import sys
sys.path.insert(0, os.path.abspath("."))

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_01_health_and_ollama_status():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["database"] == "sqlite_connected"
    print(f"\n[PASS] /health check: {data}")

def test_02_list_ollama_models():
    resp = client.get("/api/v1/ai/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert len(data["models"]) > 0
    print(f"\n[PASS] /api/v1/ai/models: Found {len(data['models'])} models -> {data['models']}")

def test_03_direct_ai_generation():
    payload = {
        "platform": "linkedin",
        "topic": "Why Founders Must Automate Organic Content",
        "model": "llama3.2:latest",
        "tone": "Thought-Provoking & Direct",
        "hook_style": "Contrarian / Thought-Provoking",
        "hashtag_count": 3,
        "call_to_action": "What is your #1 growth hurdle right now?"
    }
    resp = client.post("/api/v1/ai/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert len(data["content"]) > 30
    print(f"\n[PASS] /api/v1/ai/generate succeeded:\n{data['content'][:250]}...\n")

def test_04_create_project():
    payload = {
        "name": "Omnichannel SaaS Launch",
        "description": "Multi-platform developer brand for local AI tools",
        "target_audience": "Software engineers and indie founders",
        "tone_preference": "Authoritative & Actionable"
    }
    resp = client.post("/api/v1/projects", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == payload["name"]
    assert "id" in data
    print(f"\n[PASS] /api/v1/projects: Created project ID: {data['id']}")
    return data["id"]

def test_05_upload_and_analyze_document():
    # First create project
    proj_resp = client.post("/api/v1/projects", json={
        "name": "AI Automation Playbook",
        "description": "Content strategy for local LLM tools"
    })
    proj_id = proj_resp.json()["id"]

    doc_payload = {
        "title": "Local LLMs vs Cloud APIs Comprehensive Architecture",
        "raw_content": """
Topic: Local LLM Content Automation Engine
Description: A local-first, privacy-preserving AI social media publishing system built with Flutter, FastAPI, Ollama, and SQLite.
Benefits:
- 100% free with zero token fees or monthly recurring API costs
- Absolute data privacy: internal documents and drafts never leave your device
- Works completely offline without internet dependency
Applications:
- Multi-platform cross-posting across LinkedIn and TikTok
- Automated 30-day topical pillar scheduling
- Automated ghostwriting from developer commits and engineering notes
Technologies:
- Flutter 3.x for Android client
- FastAPI and Python 3.11 backend
- Ollama runtime with Quantized Llama3.2 models
- SQLite relational database with SQLAlchemy ORM
"""
    }

    resp = client.post(f"/api/v1/projects/{proj_id}/documents", json=doc_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == doc_payload["title"]
    assert len(data["topics"]) > 0
    assert len(data["benefits"]) > 0
    assert len(data["applications"]) > 0
    assert len(data["technologies"]) > 0
    assert len(data["content_plan"]) > 0
    print(f"\n[PASS] Document Analysis: Extracted {len(data['topics'])} topics and {len(data['content_plan'])} plan days.")

def test_06_dual_platform_generation_linkedin_and_tiktok():
    proj_resp = client.post("/api/v1/projects", json={
        "name": "Founder Content Pipeline",
        "description": "Dual LinkedIn & TikTok generation test"
    })
    proj_id = proj_resp.json()["id"]

    req_payload = {
        "project_id": proj_id,
        "day_number": 1,
        "topic": "Why We Switched From OpenAI to Local Ollama",
        "model": "llama3.2:latest"
    }

    resp = client.post("/api/v1/campaigns/daily-generate", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()
    
    # Verify LinkedIn Post
    linkedin = data["linkedin_post"]
    assert linkedin["platform"] == "linkedin"
    assert len(linkedin["content"]) > 40
    print(f"\n[PASS] Dual Generation - LinkedIn Post:\n{linkedin['content'][:250]}...\n")

    # Verify TikTok Script from the same project data
    tiktok = data["tiktok_script"]
    assert tiktok["platform"] == "tiktok"
    assert len(tiktok["content"]) > 40
    print(f"[PASS] Dual Generation - TikTok Script:\n{tiktok['content'][:250]}...\n")

def test_07_create_campaign_and_list_posts():
    proj_resp = client.post("/api/v1/projects", json={
        "name": "Campaign Test Workspace",
        "description": "Validating multi-day scheduling"
    })
    proj_id = proj_resp.json()["id"]

    now = datetime.utcnow()
    campaign_payload = {
        "title": "LinkedIn & TikTok Blitz Smoke Test",
        "start_date": now.isoformat(),
        "end_date": now.isoformat(),
        "platforms": ["linkedin"],
        "posting_hours": [9],
        "auto_posting": True,
        "model": "llama3.2:latest"
    }

    resp = client.post(f"/api/v1/projects/{proj_id}/campaigns", json=campaign_payload)
    assert resp.status_code == 200
    camp_data = resp.json()
    camp_id = camp_data["id"]
    assert camp_data["total_posts"] > 0
    print(f"\n[PASS] Campaign created: {camp_data['title']} with {camp_data['total_posts']} scheduled posts.")

    # Retrieve campaign posts
    posts_resp = client.get(f"/api/v1/campaigns/{camp_id}/posts")
    assert posts_resp.status_code == 200
    posts = posts_resp.json()
    assert len(posts) == camp_data["total_posts"]

    # Verify updating a post
    post_id = posts[0]["id"]
    update_resp = client.patch(f"/api/v1/posts/{post_id}", json={
        "topic": "Updated Topic: Advanced Local AI Benchmarks",
        "status": "draft"
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "draft"

    # Verify manual publish trigger
    pub_resp = client.post(f"/api/v1/posts/{post_id}/publish-now")
    assert pub_resp.status_code == 200
    assert pub_resp.json()["status"] == "published"
    assert pub_resp.json()["published_time"] is not None
    print(f"[PASS] Post {post_id} status updated to published successfully!")
