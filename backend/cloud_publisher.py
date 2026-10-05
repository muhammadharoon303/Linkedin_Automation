import os
import sys
import json
import argparse
import httpx
import time
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

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

def upload_video(token: str, author_urn: str, video_path: str) -> str:
    print(f"Uploading animated video to LinkedIn: {video_path}")
    reg_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
            "owner": author_urn,
            "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
        }
    }
    with httpx.Client(timeout=45.0) as client:
        resp = client.post(reg_url, headers=headers, json=payload)
        if resp.status_code not in [200, 201]:
            raise RuntimeError(f"LinkedIn video registerUpload failed ({resp.status_code}): {resp.text}")

        data = resp.json().get("value", {})
        asset_urn = data.get("asset")
        upload_url = data.get("uploadMechanism", {}).get(
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}
        ).get("uploadUrl")

        if not asset_urn or not upload_url:
            raise RuntimeError(f"Missing video asset or uploadUrl: {resp.text}")

        with open(video_path, "rb") as f:
            video_bytes = f.read()

        put_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "video/mp4"
        }
        put_resp = client.put(upload_url, headers=put_headers, content=video_bytes)
        if put_resp.status_code not in [200, 201]:
            raise RuntimeError(f"Binary video upload failed ({put_resp.status_code}): {put_resp.text}")

        print(f"Video uploaded successfully! Asset URN: {asset_urn}")
        return asset_urn

def publish_ugc_post(token: str, author_urn: str, content: str, asset_urn: str, topic: str, media_category: str = "IMAGE") -> str:
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
                "shareMediaCategory": media_category if asset_urn else "NONE"
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
    category = post_data.get("category", "ENGINEERING").strip()
    hook = post_data.get("hook", "").strip()
    body = post_data.get("body", "").strip()
    lesson = post_data.get("lesson", "").strip()
    benefit = post_data.get("benefit", "").strip()
    hashtags = post_data.get("hashtags", "").strip()

    # 1. High-Impact Scroll-Stopping Hook
    clean_hook = hook.rstrip(".")
    if not clean_hook.endswith("?"):
        clean_hook = f"{clean_hook}."

    # 2. Body formatted into crisp readable paragraphs
    body_paragraphs = []
    for para in body.split("\n\n"):
        para_clean = " ".join(para.split())
        if para_clean:
            body_paragraphs.append(para_clean)
    formatted_body = "\n\n".join(body_paragraphs)

    # 3. What I Do in Production Architecture
    clean_benefit = benefit.replace("in the next 30 days", "in scalable enterprise systems")
    clean_benefit = clean_benefit.replace("I will share in the next 30 days", "I build into production systems")
    clean_benefit = clean_benefit.replace("Day ", "Part ")

    # 4. Community CTA and Strategic Target Hashtags by niche
    text_signature = f"{category} {topic} {hashtags}".upper()
    if "SECURITY" in text_signature or "CYBER" in text_signature or "INFOSEC" in text_signature:
        cta = "How often do you audit your own production codebases for security edge cases? Let's discuss below 👇"
        targeted_tags = "#CyberSecurity #WebSecurity #AppSec #SoftwareDevelopment #DevSecOps #BackendEngineering #TechLeadership"
    elif "FLUTTER" in text_signature or "MOBILE" in text_signature:
        cta = "How do you handle state isolation and UI rebuilds in your production apps? Let's discuss below 👇"
        targeted_tags = "#FlutterDev #MobileArchitecture #CleanArchitecture #Dart #FullStack #SoftwareEngineering #TechLeadership"
    elif "BACKEND" in text_signature or "FASTAPI" in text_signature or "API" in text_signature:
        cta = "What is your go-to architecture for high-throughput async microservices? Share your stack below 👇"
        targeted_tags = "#FastAPI #BackendEngineering #Python #SystemDesign #Microservices #SoftwareArchitecture #CloudNative"
    elif "AGENT" in text_signature or "OLLAMA" in text_signature or "LLM" in text_signature:
        cta = "Are you deploying local quantized LLMs or cloud APIs for your agentic workflows? Drop your thoughts below 👇"
        targeted_tags = "#AgenticAI #LocalLLM #Ollama #GenerativeAI #AIArchitecture #Python #TechInnovation"
    elif "VISION" in text_signature or "MEDIAPIPE" in text_signature or "TRACKING" in text_signature:
        cta = "What is the biggest latency hurdle you've faced with real-time CV pipelines? Let's talk below 👇"
        targeted_tags = "#ComputerVision #MediaPipe #OpenCV #AugmentedReality #AI #EdgeComputing #DeepLearning"
    elif "IOT" in text_signature or "ESP32" in text_signature or "MOTOR" in text_signature or "HCI" in text_signature:
        cta = "How do you architect telemetry pipelines between microcontrollers and web interfaces? Let's discuss 👇"
        targeted_tags = "#IoT #ESP32 #HardwareToCloud #EmbeddedSystems #WebSockets #Industry40 #TechMakers"
    else:
        cta = "What is the single biggest architectural lesson that changed how you build software? Drop your thoughts below 👇"
        targeted_tags = "#SoftwareEngineering #SystemArchitecture #FullStack #TechLeadership #Programming #DeveloperCommunity"

    all_tags = list(dict.fromkeys(targeted_tags.split() + hashtags.split()))
    final_hashtags = " ".join(all_tags[:7])

    full_content = (
        f"{clean_hook}\n\n"
        f"{formatted_body}\n\n"
        f"⚙️ What I Do & How I Architect It:\n"
        f"{clean_benefit}\n\n"
        f"💡 Senior Engineering Takeaway:\n"
        f"{lesson}\n\n"
        f"💬 {cta}\n\n"
        f"🎯 Specialization: Full-Stack Architecture • High-Throughput APIs • AI Systems\n\n"
        f"{final_hashtags}"
    ).strip()

    video_dir = os.path.join(BASE_DIR, "generated_videos")
    video_path = os.path.join(video_dir, f"haroon_post_{target_day:02d}_animated.mp4")
    image_path = os.path.join(MEDIA_DIR, f"haroon_post_{target_day:02d}.png")
    if not os.path.exists(image_path):
        image_path = os.path.join(MEDIA_DIR, "haroon_post_01.png")

    print(f"\n==========================================")
    print(f"Executing Cloud Publish for Post #{target_day}: {topic}")
    print(f"==========================================")

    asset_urn = None
    media_category = "NONE"

    # Prioritize animated video
    if os.path.exists(video_path):
        print(f"Found animated video: {video_path}")
        asset_urn = upload_video(token, author_urn, video_path)
        media_category = "VIDEO"
        time.sleep(3)
    elif os.path.exists(image_path):
        print(f"Found visual image: {image_path}")
        asset_urn = upload_image(token, author_urn, image_path)
        media_category = "IMAGE"

    # 2. Publish post
    post_id = publish_ugc_post(token, author_urn, full_content, asset_urn, topic, media_category=media_category)

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
