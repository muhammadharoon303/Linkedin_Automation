import os
import sys
sys.path.insert(0, os.path.abspath("."))

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
from app.models.post import Post
from app.models.account import SocialAccount
from app.services.scheduler_service import check_and_publish_due_posts

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_01_linkedin_authorization_url_generation():
    # Pass client_id parameter
    resp = client.get("/api/v1/oauth/linkedin/authorize-url?client_id=test_client_12345")
    assert resp.status_code == 200
    data = resp.json()
    assert "authorize_url" in data
    assert "w_member_social" in data["authorize_url"]
    assert "openid" in data["authorize_url"]
    assert "test_client_12345" in data["authorize_url"]
    print(f"\n[PASS] Official LinkedIn OAuth URL generated successfully:\n{data['authorize_url']}")

def test_02_connect_linkedin_account():
    payload = {
        "platform": "linkedin",
        "account_name": "Senior Software Architect (Personal Profile)",
        "account_urn": "urn:li:person:mock_haroon_dev",
        "access_token": "AQX_mock_secure_linkedin_access_token_60days",
        "expires_in_days": 60
    }
    resp = client.post("/api/v1/oauth/connect-manual", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["platform"] == "linkedin"
    assert data["account_name"] == payload["account_name"]
    assert "access_token" not in data  # Never leak token in response
    print(f"\n[PASS] Connected LinkedIn Account ID: {data['id']}")

def test_03_list_accounts_security_check():
    resp = client.get("/api/v1/oauth/accounts")
    assert resp.status_code == 200
    accounts = resp.json()
    assert len(accounts) > 0
    # Ensure sensitive credentials are stripped from API response
    for acc in accounts:
        assert "access_token" not in acc
        assert "refresh_token" not in acc
    print(f"\n[PASS] Verified {len(accounts)} accounts returned with tokens redacted.")

def test_04_master_switch_controls():
    # Turn OFF
    resp = client.post("/api/v1/analytics/master-switch", json={"enabled": False})
    assert resp.status_code == 200
    assert resp.json()["master_auto_posting"] is False

    # Check status
    get_resp = client.get("/api/v1/analytics/master-switch")
    assert get_resp.status_code == 200
    assert get_resp.json()["master_auto_posting"] is False

    # Turn ON
    client.post("/api/v1/analytics/master-switch", json={"enabled": True})
    assert client.get("/api/v1/analytics/master-switch").json()["master_auto_posting"] is True
    print("\n[PASS] Master Auto-Posting toggle verified (persistent in SQLite).")

def test_05_scheduler_and_logging_execution():
    # Create project & due post
    proj_resp = client.post("/api/v1/projects", json={
        "name": "Live Scheduler Test",
        "description": "Testing automatic execution without daily user confirmation"
    })
    proj_id = proj_resp.json()["id"]

    post_resp = client.post("/api/v1/posts", json={
        "project_id": proj_id,
        "platform": "tiktok", # TikTok adapter marks script ready for mobile recording
        "day_number": 1,
        "topic": "Why Consistency is Key",
        "content": "[HOOK]: Stop quitting your content after 3 days.\n[CTA]: Follow for more.",
        "scheduled_time": (datetime.utcnow()).isoformat(),
        "auto_publish": True
    })
    post_id = post_resp.json()["id"]

    # Trigger scheduler runner directly
    import asyncio
    asyncio.run(check_and_publish_due_posts())

    # Verify post status updated
    verify_resp = client.get(f"/api/v1/posts/{post_id}")
    assert verify_resp.status_code == 200
    updated_post = verify_resp.json()
    assert updated_post["status"] == "published"
    print(f"\n[PASS] Automated scheduler processed post {post_id} -> Status: {updated_post['status']}")

    # Verify logs
    logs_resp = client.get("/api/v1/analytics/logs")
    assert logs_resp.status_code == 200
    logs = logs_resp.json()
    assert len(logs) > 0
    print(f"[PASS] Retrieved {len(logs)} audit logs from SQLite.")

def test_06_analytics_overview():
    resp = client.get("/api/v1/analytics/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_posts" in data
    assert "published_count" in data
    assert "success_rate_percent" in data
    assert "platforms" in data
    print(f"\n[PASS] Analytics Overview: {data}")
