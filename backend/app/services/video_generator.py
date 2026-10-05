import os
import sys
import asyncio
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "assets"))
AVATAR_PATH = os.path.join(ASSETS_DIR, "haroon_avatar.png")
BG_MUSIC_PATH = os.path.join(ASSETS_DIR, "ambient_bg_music.wav")

async def generate_voice(text: str, audio_path: str, voice: str = "en-US-ChristopherNeural") -> str:
    """Generates natural neural voiceover using Edge TTS."""
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate="+4%")
    await communicate.save(audio_path)
    return audio_path

def get_audio_duration(audio_path: str) -> float:
    cmd = [FFMPEG_EXE, "-i", audio_path]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    for line in res.stderr.split("\n"):
        if "Duration" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 15.0

def get_topic_bullets(category: str, title: str) -> list:
    cat_upper = category.upper()
    if "FLUTTER" in cat_upper or "MOBILE" in cat_upper:
        return [
            "• Decoupled Clean Architecture: UI widgets separated from business state.",
            "• Predictable State Management: Bloc & Riverpod streams with zero memory leaks.",
            "• Resilient Networking: Dio interceptors with offline persistence and retry logic.",
            "• High-Performance Rendering: Eliminating layout passes for 60fps native speed."
        ]
    elif "BACKEND" in cat_upper or "API" in cat_upper or "FASTAPI" in cat_upper:
        return [
            "• High-Throughput Async Architecture: FastAPI & Pydantic for sub-20ms latency.",
            "• Secure Gateway Design: JWT Bearer auth, Redis rate limiting, and RBAC.",
            "• Background Task Workers: Celery & Redis queuing for non-blocking execution.",
            "• Production Observability: Structured logging, OpenTelemetry, and health checks."
        ]
    elif "AI" in cat_upper or "AGENT" in cat_upper:
        return [
            "• Autonomous Agent Workflows: Multi-agent orchestration for end-to-end automation.",
            "• Local LLM Integration: Private offline inference with Ollama & quantized models.",
            "• Structured Function Calling: Strict JSON schemas enforcing deterministic outputs.",
            "• Resilient Fallbacks: Self-correcting prompt chains with automated error recovery."
        ]
    elif "VISION" in cat_upper or "AR" in cat_upper:
        return [
            "• Real-Time Spatial Tracking: OpenCV & MediaPipe running 60fps on edge devices.",
            "• Spatial Coordinate Mapping: 3D vector transformations for gesture interaction.",
            "• Multi-Threaded Video Pipelines: Zero-lag frame processing without UI thread blocking.",
            "• Robust Noise Filtering: Kalman filters smoothing erratic sensor readings."
        ]
    elif "IOT" in cat_upper or "ESP32" in cat_upper:
        return [
            "• Edge Hardware Integration: ESP32 microcontrollers with real-time sensor polling.",
            "• Low-Latency Telemetry: WebSockets & MQTT streaming hardware telemetry to web dashboards.",
            "• Industrial Safety Protocols: Hardware watchdog timers and failsafe state machines.",
            "• Cloud-to-Edge Sync: Bidirectional command routing for precision motor control."
        ]
    else:
        return [
            "• Enterprise Full-Stack Engineering: Scalable React & Next.js architectures.",
            "• End-to-End System Reliability: Automated CI/CD pipelines with comprehensive testing.",
            "• Production Database Design: Optimized relational schemas and caching strategies.",
            "• Human-Centered UI/UX: Accessible, ergonomic workflows built for high conversion."
        ]

def get_file_name_for_topic(category: str) -> str:
    cat = category.upper()
    if "FLUTTER" in cat or "MOBILE" in cat:
        return "flutter_architecture.dart"
    elif "BACKEND" in cat or "API" in cat or "FASTAPI" in cat:
        return "fastapi_service.py"
    elif "AI" in cat or "AGENT" in cat:
        return "agent_orchestrator.py"
    elif "VISION" in cat or "AR" in cat:
        return "computer_vision_engine.py"
    elif "IOT" in cat:
        return "iot_hardware_controller.cpp"
    return "enterprise_system.ts"

# Cache avatar image and circular mask
_cached_avatar = None
def get_avatar_image():
    global _cached_avatar
    if _cached_avatar is not None:
        return _cached_avatar
    if os.path.exists(AVATAR_PATH):
        try:
            av = Image.open(AVATAR_PATH).convert("RGBA").resize((84, 84), Image.Resampling.LANCZOS)
            mask = Image.new("L", (84, 84), 0)
            m_draw = ImageDraw.Draw(mask)
            m_draw.ellipse([(0, 0), (84, 84)], fill=255)
            _cached_avatar = (av, mask)
            return _cached_avatar
        except Exception:
            pass
    return None

def create_video_frame(bg_img: Image.Image, t: float, duration: float, category: str, title: str, hook: str, lesson: str, spoken_text: str) -> np.ndarray:
    width, height = 1280, 720
    progress = min(1.0, max(0.0, t / duration))

    # 1. Subtle cinematic Ken Burns zoom (1.00 to 1.05)
    zoom = 1.0 + 0.05 * progress
    zw, zh = int(width * zoom), int(height * zoom)
    frame_bg = bg_img.resize((zw, zh), Image.Resampling.BILINEAR)
    
    # Center crop
    x1 = (zw - width) // 2
    y1 = (zh - height) // 2
    frame = frame_bg.crop((x1, y1, x1 + width, y1 + height))
    
    # 2. Dark sapphire glassmorphic overlay
    overlay = Image.new("RGBA", (width, height), (11, 15, 23, 215))
    frame.paste(overlay, (0, 0), overlay)
    
    draw = ImageDraw.Draw(frame)

    # Subtle tech grid
    for gx in range(0, width, 80):
        draw.line([(gx, 0), (gx, height)], fill=(255, 255, 255, 12), width=1)
    for gy in range(0, height, 80):
        draw.line([(0, gy), (width, gy)], fill=(255, 255, 255, 12), width=1)

    # Fonts
    try:
        font_name = ImageFont.truetype("arialbd.ttf", 24)
        font_role = ImageFont.truetype("arial.ttf", 16)
        font_title = ImageFont.truetype("arialbd.ttf", 32)
        font_pill = ImageFont.truetype("arialbd.ttf", 16)
        font_caption = ImageFont.truetype("arialbd.ttf", 24)
        font_bullet = ImageFont.truetype("arial.ttf", 20)
        font_mono = ImageFont.truetype("consola.ttf", 17)
    except Exception:
        font_name = ImageFont.load_default()
        font_role = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_pill = ImageFont.load_default()
        font_caption = ImageFont.load_default()
        font_bullet = ImageFont.load_default()
        font_mono = ImageFont.load_default()

    # 1. Presenter Profile Header (Avatar + Pulse + Equalizer)
    av_data = get_avatar_image()
    cx, cy = 95, 75
    pulse = 1.0 + 0.08 * np.sin(2 * np.pi * 3.0 * t)
    ring_radius = int(46 * pulse)
    
    # Glowing animated ring around avatar
    draw.ellipse([(cx - ring_radius, cy - ring_radius), (cx + ring_radius, cy + ring_radius)], outline="#38BDF8", width=3)
    draw.ellipse([(cx - ring_radius - 3, cy - ring_radius - 3), (cx + ring_radius + 3, cy + ring_radius + 3)], outline=(56, 189, 248), width=1)
    
    if av_data:
        av_img, av_mask = av_data
        frame.paste(av_img, (cx - 42, cy - 42), av_mask)

    draw.text((155, 52), "MUHAMMAD HAROON", fill="#F8FAFC", font=font_name)
    draw.text((155, 82), "Full-Stack & AI Systems Architect", fill="#38BDF8", font=font_role)

    # Category Pill
    draw.rounded_rectangle([(width - 340, 48), (width - 60, 88)], radius=12, fill="#1E293B", outline="#F59E0B", width=2)
    cat_text = f"// {category.upper()[:22]}"
    draw.text((width - 325, 58), cat_text, fill="#F59E0B", font=font_pill)

    # Audio Equalizer Bars (Top Right)
    eq_x = width - 485
    for i in range(5):
        h_bar = int(10 + 16 * abs(np.sin(2 * np.pi * (1.8 + i*0.7) * t)))
        draw.rounded_rectangle([(eq_x + i*14, 88 - h_bar), (eq_x + i*14 + 8, 88)], radius=3, fill="#10B981")
    draw.text((eq_x - 120, 68), "LIVE VOICE", fill="#10B981", font=font_mono)

    # 2. Main Glassmorphic Terminal Card
    card_x1, card_y1 = 60, 130
    card_x2, card_y2 = width - 60, 640
    draw.rounded_rectangle([(card_x1, card_y1), (card_x2, card_y2)], radius=18, fill=(15, 23, 42, 240), outline="#334155", width=2)

    # Terminal Window Controls
    draw.ellipse([(85, 155), (97, 167)], fill="#EF4444")
    draw.ellipse([(105, 155), (117, 167)], fill="#F59E0B")
    draw.ellipse([(125, 155), (137, 167)], fill="#10B981")
    code_filename = get_file_name_for_topic(category)
    draw.text((155, 152), code_filename, fill="#94A3B8", font=font_mono)

    # Title
    draw.text((85, 188), title[:65], fill="#FFFFFF", font=font_title)
    draw.line([(85, 238), (card_x2 - 25, 238)], fill="#1E293B", width=2)

    # "What I Build & My Engineering Approach"
    draw.text((85, 252), "WHAT I DO & HOW I ARCHITECT FOR ENTERPRISES:", fill="#F59E0B", font=font_pill)

    bullets = get_topic_bullets(category, title)
    by = 282
    for b in bullets:
        draw.text((85, by), b, fill="#CBD5E1", font=font_bullet)
        by += 32

    # Dynamic Spoken Captions Box (Center-Bottom of Card)
    sub_y1 = card_y2 - 135
    sub_y2 = card_y2 - 25
    draw.rounded_rectangle([(85, sub_y1), (card_x2 - 25, sub_y2)], radius=12, fill=(30, 41, 59, 245), outline="#38BDF8", width=2)

    draw.text((105, sub_y1 + 12), "[ NARRATION & ARCHITECTURAL INSIGHT ]", fill="#38BDF8", font=font_mono)

    # Dynamic typewriter highlight for spoken text
    # Calculate visible text based on progress
    full_quote = f'"{spoken_text}"'
    visible_chars = int(len(full_quote) * min(1.0, progress * 1.6))
    typed_quote = full_quote[:visible_chars]
    cursor = " █" if (int(t * 4) % 2 == 0 and visible_chars < len(full_quote)) else ""

    # Wrap quote lines
    words = (typed_quote + cursor).split()
    quote_lines = []
    curr = []
    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > 72:
            quote_lines.append(" ".join(curr))
            curr = []
    if curr:
        quote_lines.append(" ".join(curr))

    qy = sub_y1 + 42
    for ql in quote_lines[:2]:
        draw.text((105, qy), ql, fill="#FEF08A", font=font_caption)
        qy += 32

    # 3. Bottom Progress Bar
    bar_w = int(width * progress)
    draw.rectangle([(0, height - 10), (width, height)], fill="#0F172A")
    draw.rectangle([(0, height - 10), (bar_w, height)], fill="#38BDF8")

    return np.array(frame.convert("RGB"))

def render_animated_video(bg_path: str, audio_path: str, output_path: str, category: str, title: str, hook: str, lesson: str, spoken_text: str) -> str:
    """Renders 720p HD animated MP4 video with synced neural voiceover and ambient music ducking."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    duration = get_audio_duration(audio_path) + 1.2
    fps = 25
    total_frames = int(duration * fps)

    bg_img = Image.open(bg_path).convert("RGB")
    temp_video = output_path.replace(".mp4", "_temp.mp4")

    cmd_video = [
        FFMPEG_EXE,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1280x720",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "22",
        temp_video
    ]

    p = subprocess.Popen(cmd_video, stdin=subprocess.PIPE)

    for i in range(total_frames):
        t = i / fps
        frame = create_video_frame(bg_img, t, duration, category, title, hook, lesson, spoken_text)
        p.stdin.write(frame.tobytes())

    p.stdin.close()
    p.wait()

    # Mux video + voiceover + ambient background music ducking
    if os.path.exists(BG_MUSIC_PATH):
        cmd_mux = [
            FFMPEG_EXE,
            "-y",
            "-i", temp_video,
            "-i", audio_path,
            "-stream_loop", "-1", "-i", BG_MUSIC_PATH,
            "-filter_complex", "[1:a]volume=1.0[voice];[2:a]volume=0.14[bg];[voice][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
    else:
        cmd_mux = [
            FFMPEG_EXE,
            "-y",
            "-i", temp_video,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]

    subprocess.run(cmd_mux, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(temp_video):
        os.remove(temp_video)
    return output_path

async def create_post_video(bg_path: str, output_video_path: str, category: str, title: str, hook: str, lesson: str) -> str:
    """End-to-end async video generation for a given post with Haroon speaking what he does."""
    # Craft authoritative spoken script highlighting who Haroon is and what he builds
    clean_hook = hook.strip().rstrip(".")
    clean_lesson = lesson.strip().rstrip(".")
    
    script_text = (
        f"Hi, I'm Muhammad Haroon, Full-Stack and AI Systems Architect. "
        f"{clean_hook}. "
        f"In production architectures, {clean_lesson}. "
        f"Here is how I build and scale these systems."
    )
    
    audio_path = output_video_path.replace(".mp4", "_audio.mp3")
    await generate_voice(script_text, audio_path)
    
    # Render with spoken text in captions
    render_animated_video(bg_path, audio_path, output_video_path, category, title, hook, lesson, script_text)
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
    return output_video_path
