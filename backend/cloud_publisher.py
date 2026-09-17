import os
import sys
import json
import argparse
import httpx
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "social_state.json")
PLAN_FILE = os.path.join(BASE_DIR, "parsed_plan.json")
MEDIA_DIR = os.path.join(BASE_DIR, "generated_media")

def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def upload_image(token: str, author_urn: str, image_path: str) -> str:
    print(f"Uploading image: {image_path}")
    reg_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author_urn,
            "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
        }
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(reg_url, headers=headers, json=payload)
        if resp.status_code not in [200, 201]:
            raise RuntimeError(f"LinkedIn registerUpload failed ({resp.status_code}): {resp.text}")

        data = resp.json().get("value", {})
        asset_urn = data.get("asset")
        upload_url = data.get("uploadMechanism", {}).get(
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}
        ).get("uploadUrl")

        if not asset_urn or not upload_url:
            raise RuntimeError(f"Missing asset or uploadUrl in LinkedIn response: {resp.text}")

        with open(image_path, "rb") as f:
            img_bytes = f.read()

        put_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "image/png"
        }
        put_resp = client.put(upload_url, headers=put_headers, content=img_bytes)
        if put_resp.status_code not in [200, 201]:
            raise RuntimeError(f"Binary image upload failed ({put_resp.status_code}): {put_resp.text}")

        print(f"Image uploaded successfully! Asset URN: {asset_urn}")
        return asset_urn

def publish_ugc_post(token: str, author_urn: str, content: str, asset_urn: str, topic: str) -> str:
    print("Publishing post via LinkedIn ugcPosts API...")
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "IMAGE" if asset_urn else "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    if asset_urn:
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
            {
                "status": "READY",
                "description": {"text": topic[:100]},
                "media": asset_urn,
                "title": {"text": topic[:100]}
            }
        ]

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code not in [200, 201]:
            raise RuntimeError(f"LinkedIn ugcPosts publish failed ({resp.status_code}): {resp.text}")

        data = resp.json()
        post_id = data.get("id", "urn:li:share:published")
        print(f"Post published successfully! Platform ID: {post_id}")
        return post_id

def main():
    load_env()
    
    parser = argparse.ArgumentParser(description="Cloud LinkedIn Publisher")
    parser.add_argument("--day", type=int, default=None, help="Specific day number to publish")
    args = parser.parse_args()

    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN", "urn:li:person:qRDXBEmWAZ")

    if not token:
        print("ERROR: LINKEDIN_ACCESS_TOKEN environment variable is not set!")
        sys.exit(1)

    # Load state
    state = {"last_published_day": 0, "history": []}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                state = json.load(f)
            except Exception:
                pass

    target_day = args.day
    if target_day is None:
        target_day = state.get("last_published_day", 0) + 1

    if target_day > 30:
        print(f"All 30 days have been published! (Current target: {target_day})")
        sys.exit(0)

    # Load plan
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    post_data = next((p for p in posts if p.get("day") == target_day), None)
    if not post_data:
        print(f"ERROR: Post for day {target_day} not found in parsed_plan.json!")
        sys.exit(1)

    topic = post_data["title"].strip()
    hook = post_data.get("hook", "").strip()
    body = post_data.get("body", "").strip()
    lesson = post_data.get("lesson", "").strip()
    benefit = post_data.get("benefit", "").strip()
    hashtags = post_data.get("hashtags", "").strip()

    # Clean formatting (No Day X mentions, clean paragraphs)
    clean_benefit = benefit.replace("in the next 30 days", "in my daily engineering work and system builds")
    clean_benefit = clean_benefit.replace("I will share in the next 30 days", "I build into production systems")

    body_paragraphs = []
    for para in body.split("\n\n"):
        para_clean = " ".join(para.split())
        if para_clean:
            body_paragraphs.append(para_clean)
    formatted_body = "\n\n".join(body_paragraphs)

    full_content = f'"{hook}"\n\n{formatted_body}\n\n'
    if lesson:
        full_content += f"💡 Key Takeaway:\n{lesson}\n\n"
    if clean_benefit:
        full_content += f"🛠️ In Practice:\n{clean_benefit}\n\n"
    if hashtags:
        full_content += f"{hashtags}"
    full_content = full_content.strip()

    image_path = os.path.join(MEDIA_DIR, f"haroon_post_{target_day:02d}.png")
    if not os.path.exists(image_path):
        print(f"Warning: Specific image {image_path} not found. Searching fallback...")
        image_path = os.path.join(MEDIA_DIR, "haroon_post_01.png")

    print(f"\n==========================================")
    print(f"Executing Cloud Publish for Post #{target_day}: {topic}")
    print(f"==========================================")

    # 1. Upload 3D Image
    asset_urn = upload_image(token, author_urn, image_path)

    # 2. Publish post
    post_id = publish_ugc_post(token, author_urn, full_content, asset_urn, topic)

    # 3. Update state
    now_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    state["last_published_day"] = target_day
    state["last_published_at"] = now_utc
    state.setdefault("history", []).append({
        "day": target_day,
        "topic": topic,
        "published_at": now_utc,
        "platform_post_id": post_id,
        "status": "published"
    })

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    print(f"\nSuccessfully published Post #{target_day}!")
    print(f"State updated: last_published_day = {target_day}")

if __name__ == "__main__":
    main()
