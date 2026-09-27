import os
import sys
import asyncio
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import edge_tts
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

async def generate_voice(text: str, audio_path: str, voice: str = "en-US-ChristopherNeural") -> str:
    """Generates natural neural voiceover using Edge TTS."""
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate="+5%")
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
    return 10.0

def create_video_frame(bg_img: Image.Image, t: float, duration: float, category: str, title: str, hook: str, lesson: str) -> np.ndarray:
    width, height = 1280, 720
    progress = t / duration

    # 1. Subtle cinematic Ken Burns zoom (1.00 to 1.07)
    zoom = 1.0 + 0.07 * progress
    zw, zh = int(width * zoom), int(height * zoom)
    frame_bg = bg_img.resize((zw, zh), Image.Resampling.BILINEAR)
    
    # Center crop
    x1 = (zw - width) // 2
    y1 = (zh - height) // 2
    frame = frame_bg.crop((x1, y1, x1 + width, y1 + height))
    
    # 2. Dark glassmorphic gradient overlay for contrast
    overlay = Image.new("RGBA", (width, height), (15, 23, 42, 175))
    frame.paste(overlay, (0, 0), overlay)
    
    draw = ImageDraw.Draw(frame)

    # Fonts
    try:
        font_pill = ImageFont.truetype("arialbd.ttf", 20)
        font_title = ImageFont.truetype("arialbd.ttf", 38)
        font_hook = ImageFont.truetype("arialbd.ttf", 28)
        font_lesson = ImageFont.truetype("arial.ttf", 24)
        font_footer = ImageFont.truetype("arialbd.ttf", 20)
    except Exception:
        font_pill = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_hook = ImageFont.load_default()
        font_lesson = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Top Category Pill
    pill_text = f"  {category.upper()}  "
    draw.rounded_rectangle([(60, 45), (340, 85)], radius=10, fill="#1E293B", outline="#38BDF8", width=2)
    draw.text((75, 53), pill_text, fill="#38BDF8", font=font_pill)

    # Engineering Video Badge
    draw.text((width - 320, 53), "ANIMATED ARCHITECTURE", fill="#94A3B8", font=font_pill)

    # Title
    draw.text((60, 110), title[:65], fill="#F8FAFC", font=font_title)

    # Glass Terminal Window for Hook and Code
    card_y = 185
    draw.rounded_rectangle([(60, card_y), (width - 60, card_y + 365)], radius=20, fill=(15, 23, 42, 235), outline="#334155", width=2)

    # macOS Terminal Dots
    draw.ellipse([(85, card_y + 25), (99, card_y + 39)], fill="#EF4444")
    draw.ellipse([(108, card_y + 25), (122, card_y + 39)], fill="#F59E0B")
    draw.ellipse([(131, card_y + 25), (145, card_y + 39)], fill="#10B981")
    draw.text((165, card_y + 22), "system_insight.py", fill="#64748B", font=font_pill)

    # Animated typewriter effect for the Hook
    full_hook = f'"{hook}"'
    visible_chars = int(len(full_hook) * min(1.0, (progress * 2.2)))
    typed_hook = full_hook[:visible_chars]
    cursor = " █" if (int(t * 4) % 2 == 0 and visible_chars < len(full_hook)) else ""

    hook_lines = []
    curr_line = []
    for w in (typed_hook + cursor).split():
        curr_line.append(w)
        if len(" ".join(curr_line)) > 55:
            hook_lines.append(" ".join(curr_line))
            curr_line = []
    if curr_line:
        hook_lines.append(" ".join(curr_line))

    hy = card_y + 80
    for hl in hook_lines[:3]:
        draw.text((85, hy), hl, fill="#38BDF8", font=font_hook)
        hy += 42

    # Key Takeaway fade-in at 40% progress
    if progress > 0.38:
        draw.line([(85, hy + 15), (width - 85, hy + 15)], fill="#1E293B", width=2)
        draw.text((85, hy + 35), "💡 KEY ARCHITECTURAL TAKEAWAY:", fill="#F59E0B", font=font_pill)
        draw.text((85, hy + 70), lesson[:115], fill="#E2E8F0", font=font_lesson)

    # Footer Branding
    draw.text((60, height - 70), "MUHAMMAD HAROON | FULL-STACK & AI ARCHITECT", fill="#38BDF8", font=font_footer)
    draw.text((width - 320, height - 70), "FastAPI • Flutter • Ollama", fill="#94A3B8", font=font_pill)

    # Animated Progress Bar at bottom
    bar_width = int(width * progress)
    draw.rectangle([(0, height - 8), (width, height)], fill="#1E293B")
    draw.rectangle([(0, height - 8), (bar_width, height)], fill="#38BDF8")

    return np.array(frame.convert("RGB"))

def render_animated_video(bg_path: str, audio_path: str, output_path: str, category: str, title: str, hook: str, lesson: str) -> str:
    """Renders 720p HD animated MP4 video with synced neural voiceover."""
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
        frame = create_video_frame(bg_img, t, duration, category, title, hook, lesson)
        p.stdin.write(frame.tobytes())

    p.stdin.close()
    p.wait()

    # Mux video + audio
    cmd_mux = [
        FFMPEG_EXE,
        "-y",
        "-i", temp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd_mux, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(temp_video):
        os.remove(temp_video)
    return output_path

async def create_post_video(bg_path: str, output_video_path: str, category: str, title: str, hook: str, lesson: str) -> str:
    """End-to-end async video generation for a given post."""
    script_text = f"{hook}. The core architectural takeaway: {lesson}"
    audio_path = output_video_path.replace(".mp4", "_audio.mp3")
    
    await generate_voice(script_text, audio_path)
    render_animated_video(bg_path, audio_path, output_video_path, category, title, hook, lesson)
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
    return output_video_path
