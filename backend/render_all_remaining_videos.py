import os
import sys
import json
import asyncio
import sqlite3

# Ensure utf-8 stdout
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.services.video_generator import create_post_video

PLAN_FILE = os.path.join(BASE_DIR, "parsed_plan.json")
MEDIA_DIR = os.path.join(BASE_DIR, "generated_media")
VIDEO_DIR = os.path.join(BASE_DIR, "generated_videos")
DB_PATH = os.path.join(BASE_DIR, "social_ai.db")

async def render_all():
    os.makedirs(VIDEO_DIR, exist_ok=True)
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for post in posts:
        day = post["day"]
        video_path = os.path.join(VIDEO_DIR, f"haroon_post_{day:02d}_animated.mp4")
        
        if os.path.exists(video_path):
            print(f"[SKIP] Post #{day} already rendered: {video_path}")
        else:
            bg_path = os.path.join(MEDIA_DIR, f"haroon_post_{day:02d}.png")
            if not os.path.exists(bg_path):
                bg_path = os.path.join(MEDIA_DIR, "haroon_post_01.png")

            category = post.get("category", "ENGINEERING")
            title = post.get("title", "")
            hook = post.get("hook", "")
            lesson = post.get("lesson", "")

            print(f"[RENDERING] Post #{day}: {title}...")
            try:
                await create_post_video(
                    bg_path=bg_path,
                    output_video_path=video_path,
                    category=category,
                    title=title,
                    hook=hook,
                    lesson=lesson
                )
                print(f"[DONE] Post #{day} saved: {video_path}")
            except Exception as e:
                print(f"[ERROR] Failed to render Post #{day}: {e}")

        # Update SQLite DB if present
        if os.path.exists(video_path):
            cursor.execute(
                "UPDATE posts SET media_path = ? WHERE day_number = ?",
                (video_path, day)
            )
            conn.commit()

    conn.close()
    print("\nAll videos rendered and database updated successfully!")

if __name__ == "__main__":
    asyncio.run(render_all())
