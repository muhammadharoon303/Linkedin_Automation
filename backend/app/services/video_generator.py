import os
import sys
import math
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

def get_font(size: int, bold: bool = False, mono: bool = False):
    try:
        if mono:
            return ImageFont.truetype("consola.ttf", size)
        elif bold:
            return ImageFont.truetype("arialbd.ttf", size)
        else:
            return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

async def generate_voice(text: str, audio_path: str, voice: str = "en-US-ChristopherNeural") -> str:
    """Generates natural neural voiceover using Edge TTS with automatic fallback to gTTS."""
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+4%")
        await communicate.save(audio_path)
    except Exception as e:
        print(f"Edge TTS fallback triggered ({e}). Using gTTS...")
        from gtts import gTTS
        loop = asyncio.get_event_loop()
        def _run_gtts():
            tts = gTTS(text, lang='en', tld='us')
            tts.save(audio_path)
        await loop.run_in_executor(None, _run_gtts)
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

# Cache avatar image and circular mask
_cached_avatar = None
def get_avatar_image():
    global _cached_avatar
    if _cached_avatar is not None:
        return _cached_avatar
    if os.path.exists(AVATAR_PATH):
        try:
            av_w, av_h = 72, 72
            av = Image.open(AVATAR_PATH).convert("RGBA").resize((av_w, av_h), Image.Resampling.LANCZOS)
            mask = Image.new("L", (av_w, av_h), 0)
            m_draw = ImageDraw.Draw(mask)
            m_draw.ellipse([(0, 0), (av_w, av_h)], fill=255)
            _cached_avatar = (av, mask)
            return _cached_avatar
        except Exception:
            pass
    return None

def draw_header(draw, width, t, category_name: str, canvas):
    cx, cy = 95, 65
    pulse = 1.0 + 0.08 * math.sin(2 * math.pi * 3.0 * t)
    ring_r = int(40 * pulse)
    
    # Glowing animated ring around avatar
    draw.ellipse([(cx - ring_r, cy - ring_r), (cx + ring_r, cy + ring_r)], outline="#38BDF8", width=3)
    draw.ellipse([(cx - ring_r - 2, cy - ring_r - 2), (cx + ring_r + 2, cy + ring_r + 2)], outline=(56, 189, 248), width=1)
    
    av_data = get_avatar_image()
    if av_data:
        av_img, av_mask = av_data
        canvas.paste(av_img, (cx - 36, cy - 36), av_mask)

    draw.text((155, 45), "MUHAMMAD HAROON", fill="#F8FAFC", font=get_font(22, bold=True))
    draw.text((155, 72), "Full-Stack & AI Systems Architect", fill="#38BDF8", font=get_font(15))

    # Category Badge (Top Right)
    draw.rounded_rectangle([(width - 320, 42), (width - 50, 80)], radius=10, fill="#1E293B", outline="#F59E0B", width=2)
    draw.text((width - 305, 52), f"// {category_name.upper()[:22]}", fill="#F59E0B", font=get_font(15, bold=True))

    # Live Audio Equalizer
    eq_x = width - 460
    for i in range(5):
        h = int(8 + 14 * abs(math.sin(2 * math.pi * (1.8 + i*0.7) * t)))
        draw.rounded_rectangle([(eq_x + i*13, 80 - h), (eq_x + i*13 + 7, 80)], radius=2, fill="#10B981")
    draw.text((eq_x - 110, 60), "LIVE VOICE", fill="#10B981", font=get_font(15, mono=True))

# ----------------- Visual Animation Archetypes ----------------- #

def draw_mobile_flutter_visuals(draw, x1, y1, x2, y2, t):
    """Animated smartphone device frame running a modern Flutter UI with floating state nodes."""
    px, py = (x1 + x2) // 2 - 160, y1 + 10
    pw, ph = 240, 400
    
    draw.rounded_rectangle([(px, py), (px + pw, py + ph)], radius=28, fill="#0F172A", outline="#475569", width=4)
    sx, sy, sw, sh = px + 10, py + 12, pw - 20, ph - 24
    draw.rounded_rectangle([(sx, sy), (sx + sw, sy + sh)], radius=20, fill="#020617")
    
    # Dynamic Island / Camera Notch
    draw.rounded_rectangle([(px + pw//2 - 28, sy + 6), (px + pw//2 + 28, sy + 18)], radius=6, fill="#000000")
    
    # App Bar
    draw.rounded_rectangle([(sx + 8, sy + 28), (sx + sw - 8, sy + 62)], radius=8, fill="#1E293B")
    draw.text((sx + 18, sy + 38), "Flutter Production App", fill="#F8FAFC", font=get_font(13, bold=True))
    
    # 60 FPS Badge
    draw.rounded_rectangle([(sx + sw - 65, sy + 36), (sx + sw - 12, sy + 54)], radius=4, fill="#10B981")
    draw.text((sx + sw - 60, sy + 38), "60.0 FPS", fill="#FFFFFF", font=get_font(10, bold=True, mono=True))
    
    # Hero Card (Sliding / Pulsing)
    card_pulse = 2 * math.sin(t * 3)
    draw.rounded_rectangle([(sx + 8, sy + 74 + card_pulse), (sx + sw - 8, sy + 175 + card_pulse)], radius=12, fill="#1E1B4B", outline="#6366F1", width=2)
    draw.text((sx + 18, sy + 84 + card_pulse), "State: Active Stream", fill="#A5B4FC", font=get_font(11, bold=True))
    draw.text((sx + 18, sy + 102 + card_pulse), "Bloc State Machine", fill="#FFFFFF", font=get_font(15, bold=True))
    
    for i in range(8):
        bh = int(12 + 18 * abs(math.sin(t*4 + i*0.8)))
        bx = sx + 22 + i*22
        draw.rounded_rectangle([(bx, sy + 160 + card_pulse - bh), (bx + 14, sy + 160 + card_pulse)], radius=3, fill="#38BDF8")
        
    for j in range(2):
        ly = sy + 190 + j * 54
        draw.rounded_rectangle([(sx + 8, ly), (sx + sw - 8, ly + 44)], radius=8, fill="#0F172A", outline="#1E293B", width=1)
        draw.ellipse([(sx + 18, ly + 10), (sx + 42, ly + 34)], fill="#38BDF8")
        draw.text((sx + 52, ly + 10), f"UI Component #{j+1}", fill="#E2E8F0", font=get_font(12, bold=True))
        draw.text((sx + 52, ly + 25), "Zero jank rendering", fill="#64748B", font=get_font(10))

    right_x = px + pw + 35
    draw.rounded_rectangle([(right_x, y1 + 30), (x2 - 10, y1 + 170)], radius=14, fill="#0F172A", outline="#38BDF8", width=2)
    draw.text((right_x + 18, y1 + 45), "CLEAN MOBILE ARCHITECTURE", fill="#38BDF8", font=get_font(15, bold=True))
    
    flutter_points = [
        "✔ Decoupled Presentation, Domain & Data layers",
        "✔ Predictable State Machines (Bloc / Riverpod)",
        "✔ Dio interceptors with offline persistence & cache",
        "✔ Optimized widget rebuild trees for 60fps native speed"
    ]
    for idx, pt in enumerate(flutter_points):
        draw.text((right_x + 18, y1 + 75 + idx * 22), pt, fill="#CBD5E1", font=get_font(12))

    draw.rounded_rectangle([(right_x, y1 + 190), (x2 - 10, y1 + 390)], radius=14, fill="#0F172A", outline="#10B981", width=2)
    draw.text((right_x + 18, y1 + 205), "PRODUCTION BENCHMARKS", fill="#10B981", font=get_font(15, bold=True))
    draw.text((right_x + 18, y1 + 235), "• Memory Leak Detection: ZERO leaks detected", fill="#E2E8F0", font=get_font(13))
    draw.text((right_x + 18, y1 + 265), "• App Startup Cold Launch: < 720ms", fill="#E2E8F0", font=get_font(13))
    draw.text((right_x + 18, y1 + 295), "• Frame Render Budget: 16.6ms per frame strictly met", fill="#E2E8F0", font=get_font(13))
    draw.text((right_x + 18, y1 + 325), "• Cross-Platform Parity: iOS & Android single codebase", fill="#E2E8F0", font=get_font(13))

def draw_backend_api_visuals(draw, x1, y1, x2, y2, t):
    """Animated high-throughput API architecture with moving data packets and live latency graphs."""
    nodes = [
        ("Client App", "Flutter / Web", x1 + 20, y1 + 120, "#38BDF8"),
        ("FastAPI Gateway", "Async Router", x1 + 260, y1 + 120, "#10B981"),
        ("Redis Cache", "In-Memory RAM", x1 + 540, y1 + 50, "#F59E0B"),
        ("PostgreSQL", "Relational Shard", x1 + 540, y1 + 190, "#818CF8"),
        ("Worker Pool", "Celery / Async", x1 + 800, y1 + 120, "#EC4899")
    ]
    
    draw.line([(x1 + 170, y1 + 155), (x1 + 260, y1 + 155)], fill="#334155", width=4)
    draw.line([(x1 + 420, y1 + 155), (x1 + 540, y1 + 85)], fill="#334155", width=4)
    draw.line([(x1 + 420, y1 + 155), (x1 + 540, y1 + 225)], fill="#334155", width=4)
    draw.line([(x1 + 690, y1 + 85), (x1 + 800, y1 + 155)], fill="#334155", width=4)
    draw.line([(x1 + 690, y1 + 225), (x1 + 800, y1 + 155)], fill="#334155", width=4)

    packet_phase = (t * 2.0) % 1.0
    p1x = (x1 + 170) + packet_phase * 90
    draw.ellipse([(p1x - 7, y1 + 148), (p1x + 7, y1 + 162)], fill="#38BDF8")
    
    p2x = (x1 + 420) + packet_phase * 120
    p2y = (y1 + 155) + packet_phase * (-70)
    draw.ellipse([(p2x - 7, p2y - 7), (p2x + 7, p2y + 7)], fill="#F59E0B")

    p3x = (x1 + 690) + packet_phase * 110
    p3y = (y1 + 225) + packet_phase * (-70)
    draw.ellipse([(p3x - 7, p3y - 7), (p3x + 7, p3y + 7)], fill="#10B981")

    for title, subtitle, nx, ny, color in nodes:
        draw.rounded_rectangle([(nx, ny), (nx + 150, ny + 70)], radius=12, fill="#0F172A", outline=color, width=3)
        draw.text((nx + 14, ny + 14), title, fill="#FFFFFF", font=get_font(13, bold=True))
        draw.text((nx + 14, ny + 38), subtitle, fill=color, font=get_font(11, mono=True))

    dash_y = y1 + 270
    draw.rounded_rectangle([(x1 + 20, dash_y), (x2 - 20, y2 - 20)], radius=14, fill="#090D16", outline="#1E293B", width=2)
    
    metrics = [
        ("API LATENCY", "12.4 ms", "P99: 28ms • Non-blocking async", "#10B981"),
        ("THROUGHPUT", "18,450 req/s", "Horizontal Autoscaling active", "#38BDF8"),
        ("ERROR RATE", "0.002%", "Healthcheck: 100% PASS", "#A855F7")
    ]
    col_w = (x2 - x1 - 80) // 3
    for i, (m_title, m_val, m_sub, m_col) in enumerate(metrics):
        mx = x1 + 40 + i * (col_w + 15)
        draw.rounded_rectangle([(mx, dash_y + 12), (mx + col_w, dash_y + 105)], radius=10, fill="#0F172A", outline=m_col, width=1)
        draw.text((mx + 15, dash_y + 22), m_title, fill="#94A3B8", font=get_font(11, bold=True, mono=True))
        draw.text((mx + 15, dash_y + 40), m_val, fill=m_col, font=get_font(26, bold=True))
        draw.text((mx + 15, dash_y + 78), m_sub, fill="#CBD5E1", font=get_font(10))

def draw_cybersecurity_visuals(draw, x1, y1, x2, y2, t):
    """Futuristic Cyber Defense & Threat Mitigation HUD with animated forcefield shield and radar."""
    cx, cy = (x1 + x2) // 2 - 180, (y1 + y2) // 2
    
    radar_r = 140
    draw.ellipse([(cx - radar_r, cy - radar_r), (cx + radar_r, cy + radar_r)], outline="#059669", width=2)
    draw.ellipse([(cx - radar_r//2, cy - radar_r//2), (cx + radar_r//2, cy + radar_r//2)], outline=(5, 150, 105), width=1)
    
    draw.line([(cx - radar_r - 10, cy), (cx + radar_r + 10, cy)], fill="#065F46", width=1)
    draw.line([(cx, cy - radar_r - 10), (cx, cy + radar_r + 10)], fill="#065F46", width=1)
    
    angle = (t * 2.5) % (2 * math.pi)
    beam_x = cx + int(radar_r * math.cos(angle))
    beam_y = cy + int(radar_r * math.sin(angle))
    draw.line([(cx, cy), (beam_x, beam_y)], fill="#10B981", width=3)
    
    shield_pulse = 1.0 + 0.06 * math.sin(t * 5)
    sr = int(65 * shield_pulse)
    hex_pts = []
    for i in range(6):
        a = i * (math.pi / 3) + (math.pi / 6)
        hex_pts.append((cx + int(sr * math.cos(a)), cy + int(sr * math.sin(a))))
    draw.polygon(hex_pts, fill="#064E3B", outline="#10B981")
    draw.text((cx - 36, cy - 10), "SHIELD", fill="#F8FAFC", font=get_font(18, bold=True))
    draw.text((cx - 28, cy + 12), "ACTIVE", fill="#34D399", font=get_font(12, bold=True, mono=True))

    panel_x = cx + radar_r + 35
    draw.rounded_rectangle([(panel_x, y1 + 15), (x2 - 15, y2 - 15)], radius=14, fill="#090D16", outline="#EF4444", width=2)
    draw.text((panel_x + 18, y1 + 30), "DEFENSE-IN-DEPTH SECURITY HUD", fill="#EF4444", font=get_font(15, bold=True, mono=True))
    
    sec_logs = [
        ("✔ Zero-Trust API Authentication: JWT Bearer validated", "#10B981"),
        ("✔ Strict Pydantic Payload Sanitization: Injection blocked", "#10B981"),
        ("✔ Rate Limiter: 100 req/min per IP enforced via Redis", "#38BDF8"),
        ("✔ Least-Privilege Scoping: Database roles strictly partitioned", "#F59E0B"),
        ("✔ Automated Dependency Auditing: CVE scans on every commit", "#10B981")
    ]
    for idx, (log_text, col) in enumerate(sec_logs):
        ly = y1 + 70 + idx * 36
        draw.rounded_rectangle([(panel_x + 15, ly), (x2 - 30, ly + 28)], radius=6, fill="#0F172A")
        draw.text((panel_x + 25, ly + 6), log_text, fill=col, font=get_font(12, mono=True))

    draw.rounded_rectangle([(panel_x + 15, y1 + 265), (x2 - 30, y1 + 370)], radius=10, fill="#1E1B4B", outline="#818CF8", width=1)
    draw.text((panel_x + 25, y1 + 278), "SECURITY MINDSET IN PRACTICE:", fill="#A5B4FC", font=get_font(12, bold=True))
    draw.text((panel_x + 25, y1 + 305), "Security is not an afterthought added before deployment.", fill="#FFFFFF", font=get_font(13, bold=True))
    draw.text((panel_x + 25, y1 + 330), "It is architected into every query, endpoint, and token contract.", fill="#94A3B8", font=get_font(12))

def draw_computer_vision_visuals(draw, x1, y1, x2, y2, t):
    """Futuristic Computer Vision & Spatial AR Tracking HUD."""
    vw, vh = 580, 360
    vx, vy = x1 + 30, y1 + 25
    draw.rounded_rectangle([(vx, vy), (vx + vw, vy + vh)], radius=12, fill="#050811", outline="#38BDF8", width=2)
    
    corner_len = 25
    draw.line([(vx + 10, vy + 10), (vx + 10 + corner_len, vy + 10)], fill="#38BDF8", width=3)
    draw.line([(vx + 10, vy + 10), (vx + 10, vy + 10 + corner_len)], fill="#38BDF8", width=3)
    draw.line([(vx + vw - 10, vy + 10), (vx + vw - 10 - corner_len, vy + 10)], fill="#38BDF8", width=3)
    draw.line([(vx + vw - 10, vy + 10), (vx + vw - 10, vy + 10 + corner_len)], fill="#38BDF8", width=3)
    draw.line([(vx + 10, vy + vh - 10), (vx + 10 + corner_len, vy + vh - 10)], fill="#38BDF8", width=3)
    draw.line([(vx + 10, vy + vh - 10), (vx + 10, vy + vh - 10 - corner_len)], fill="#38BDF8", width=3)
    draw.line([(vx + vw - 10, vy + vh - 10), (vx + vw - 10 - corner_len, vy + vh - 10)], fill="#38BDF8", width=3)
    draw.line([(vx + vw - 10, vy + vh - 10), (vx + vw - 10, vy + vh - 10 - corner_len)], fill="#38BDF8", width=3)

    draw.text((vx + 25, vy + 20), "REC • 4K 60FPS • AI PIPELINE ACTIVE", fill="#EF4444", font=get_font(12, bold=True, mono=True))
    draw.text((vx + vw - 140, vy + 20), "LATENCY: 4.8ms", fill="#10B981", font=get_font(12, bold=True, mono=True))

    box_x = vx + int(180 + 35 * math.sin(t * 1.5))
    box_y = vy + int(90 + 20 * math.cos(t * 2.0))
    bw, bh = 190, 190
    draw.rectangle([(box_x, box_y), (box_x + bw, box_y + bh)], outline="#10B981", width=2)
    
    draw.rectangle([(box_x, box_y - 22), (box_x + bw, box_y)], fill="#10B981")
    draw.text((box_x + 8, box_y - 18), "HAND MESH: 99.4% CONF", fill="#000000", font=get_font(11, bold=True, mono=True))

    pts = [
        (box_x + 95, box_y + 160),
        (box_x + 60, box_y + 110),
        (box_x + 40, box_y + 80),
        (box_x + 80, box_y + 60),
        (box_x + 105, box_y + 50),
        (box_x + 130, box_y + 65),
        (box_x + 155, box_y + 90)
    ]
    for pt in pts:
        draw.ellipse([(pt[0] - 4, pt[1] - 4), (pt[0] + 4, pt[1] + 4)], fill="#38BDF8")
    for k in range(len(pts) - 1):
        draw.line([pts[k], pts[k+1]], fill="#A7F3D0", width=2)

    rx = vx + vw + 30
    draw.rounded_rectangle([(rx, y1 + 25), (x2 - 15, y2 - 25)], radius=12, fill="#0F172A", outline="#818CF8", width=2)
    draw.text((rx + 18, y1 + 45), "COMPUTER VISION & AR PIPELINE", fill="#818CF8", font=get_font(15, bold=True))
    
    cv_points = [
        "• Real-Time Spatial Coordinate Extraction",
        "• MediaPipe 21-Keypoint 3D Landmark Rigging",
        "• Multi-Threaded Video Frame Processing",
        "• Zero-Lag Edge Inference with OpenCV & Python",
        "• Gesture Recognition with Kalman Noise Filtering"
    ]
    for idx, p in enumerate(cv_points):
        draw.text((rx + 18, y1 + 80 + idx * 30), p, fill="#E2E8F0", font=get_font(12))

    draw.rounded_rectangle([(rx + 15, y1 + 250), (x2 - 30, y1 + 360)], radius=8, fill="#1E293B")
    draw.text((rx + 25, y1 + 265), "PERFORMANCE METRICS:", fill="#F59E0B", font=get_font(12, bold=True))
    draw.text((rx + 25, y1 + 295), "Frame Processing Budget: 14.2ms / frame", fill="#FFFFFF", font=get_font(13))
    draw.text((rx + 25, y1 + 325), "Spatial Accuracy Tolerance: < 2.1mm error", fill="#34D399", font=get_font(13))

def draw_iot_hardware_visuals(draw, x1, y1, x2, y2, t):
    """Industrial IoT, ESP32 Telemetry Cockpit with circular gauges and live oscilloscope."""
    gx1, gy1 = x1 + 110, y1 + 130
    gr = 90
    draw.ellipse([(gx1 - gr, gy1 - gr), (gx1 + gr, gy1 + gr)], outline="#475569", width=6)
    draw.text((gx1 - 38, gy1 + 35), "MOTOR RPM", fill="#94A3B8", font=get_font(12, bold=True))
    
    rpm_val = int(3200 + 400 * math.sin(t * 2))
    needle_angle = -math.pi * 0.75 + (rpm_val / 5000.0) * math.pi * 1.5
    nx = gx1 + int(gr * 0.75 * math.cos(needle_angle))
    ny = gy1 + int(gr * 0.75 * math.sin(needle_angle))
    draw.line([(gx1, gy1), (nx, ny)], fill="#EF4444", width=3)
    draw.ellipse([(gx1 - 8, gy1 - 8), (gx1 + 8, gy1 + 8)], fill="#F8FAFC")
    draw.text((gx1 - 36, gy1 - 10), f"{rpm_val}", fill="#FFFFFF", font=get_font(20, bold=True))

    gx2 = x1 + 330
    draw.ellipse([(gx2 - gr, gy1 - gr), (gx2 + gr, gy1 + gr)], outline="#475569", width=6)
    draw.text((gx2 - 28, gy1 + 35), "CORE TEMP", fill="#94A3B8", font=get_font(12, bold=True))
    temp_val = int(48 + 6 * math.sin(t * 1.2))
    temp_angle = -math.pi * 0.75 + (temp_val / 100.0) * math.pi * 1.5
    tx = gx2 + int(gr * 0.75 * math.cos(temp_angle))
    ty = gy1 + int(gr * 0.75 * math.sin(temp_angle))
    draw.line([(gx2, gy1), (tx, ty)], fill="#F59E0B", width=3)
    draw.ellipse([(gx2 - 8, gy1 - 8), (gx2 + 8, gy1 + 8)], fill="#F8FAFC")
    draw.text((gx2 - 26, gy1 - 10), f"{temp_val}°C", fill="#FFFFFF", font=get_font(20, bold=True))

    ow_x1, ow_y1, ow_x2, ow_y2 = x1 + 20, y1 + 250, x1 + 430, y2 - 20
    draw.rounded_rectangle([(ow_x1, ow_y1), (ow_x2, ow_y2)], radius=12, fill="#050811", outline="#10B981", width=2)
    draw.text((ow_x1 + 15, ow_y1 + 10), "TELEMETRY SIGNAL [MQTT / WEBSOCKET]", fill="#10B981", font=get_font(11, bold=True, mono=True))
    
    prev_pt = None
    for px in range(ow_x1 + 15, ow_x2 - 15, 4):
        phase = (px - ow_x1) * 0.05 + t * 6.0
        py = (ow_y1 + ow_y2) // 2 + int(32 * math.sin(phase))
        if prev_pt:
            draw.line([prev_pt, (px, py)], fill="#34D399", width=2)
        prev_pt = (px, py)

    rx = x1 + 465
    draw.rounded_rectangle([(rx, y1 + 25), (x2 - 15, y2 - 20)], radius=14, fill="#0F172A", outline="#38BDF8", width=2)
    draw.text((rx + 20, y1 + 45), "INDUSTRIAL HARDWARE-TO-CLOUD", fill="#38BDF8", font=get_font(15, bold=True))
    
    iot_points = [
        "• ESP32 Dual-Core Microcontroller Telemetry",
        "• Sub-50ms WebSocket Bidirectional Motor Control",
        "• Industrial Safety Protocols & Watchdog Heartbeats",
        "• Real-Time Cloud Sensor Synchronization",
        "• Ergonomic Industrial Web Dashboard Interface"
    ]
    for idx, p in enumerate(iot_points):
        draw.text((rx + 20, y1 + 85 + idx * 34), p, fill="#CBD5E1", font=get_font(13))

    draw.rounded_rectangle([(rx + 15, y1 + 265), (x2 - 30, y1 + 355)], radius=10, fill="#1E293B")
    draw.text((rx + 25, y1 + 280), "LIVE TELEMETRY SPECS:", fill="#F59E0B", font=get_font(12, bold=True))
    draw.text((rx + 25, y1 + 305), "Transmission: Protocol Buffers over WSS", fill="#E2E8F0", font=get_font(12))
    draw.text((rx + 25, y1 + 325), "Latency: 28ms Edge-to-Cloud Round Trip", fill="#34D399", font=get_font(12))

def draw_agentic_ai_visuals(draw, x1, y1, x2, y2, t):
    """Multi-Agent Neural Brain Network with autonomous message passing."""
    cx, cy = (x1 + x2) // 2 - 160, (y1 + y2) // 2
    
    draw.ellipse([(cx - 55, cy - 55), (cx + 55, cy + 55)], fill="#1E1B4B", outline="#818CF8", width=3)
    draw.text((cx - 42, cy - 14), "ORCHESTRATOR", fill="#FFFFFF", font=get_font(11, bold=True, mono=True))
    draw.text((cx - 28, cy + 5), "AI AGENT", fill="#A5B4FC", font=get_font(11, bold=True, mono=True))

    sub_nodes = [
        ("CODE GEN", "Coder Agent", 0),
        ("TOOL EXEC", "API Caller", math.pi / 2),
        ("VALIDATOR", "Output Audit", math.pi),
        ("MEMORY", "Vector RAG", 3 * math.pi / 2)
    ]
    radius = 145
    for name, role, a in sub_nodes:
        sx = cx + int(radius * math.cos(a + t * 0.3))
        sy = cy + int(radius * math.sin(a + t * 0.3))
        
        draw.line([(cx, cy), (sx, sy)], fill="#334155", width=2)
        
        phase = (t * 2.5 + a) % 1.0
        px = cx + int(phase * (sx - cx))
        py = cy + int(phase * (sy - cy))
        draw.ellipse([(px - 5, py - 5), (px + 5, py + 5)], fill="#38BDF8")
        
        draw.ellipse([(sx - 38, sy - 38), (sx + 38, sy + 38)], fill="#0F172A", outline="#38BDF8", width=2)
        draw.text((sx - 26, sy - 10), name, fill="#FFFFFF", font=get_font(10, bold=True, mono=True))
        draw.text((sx - 28, sy + 5), role, fill="#38BDF8", font=get_font(9))

    rx = cx + radius + 60
    draw.rounded_rectangle([(rx, y1 + 25), (x2 - 15, y2 - 20)], radius=14, fill="#0F172A", outline="#EC4899", width=2)
    draw.text((rx + 20, y1 + 45), "AUTONOMOUS AGENT WORKFLOWS", fill="#EC4899", font=get_font(15, bold=True))
    
    agent_pts = [
        "• Multi-Agent Collaboration & Message Passing",
        "• Local Quantized LLM Inference (Ollama)",
        "• Structured JSON Schema Function Calling",
        "• Self-Healing Error Recovery & Prompt Chains",
        "• Long-Term Memory with Local Vector Embeddings"
    ]
    for idx, p in enumerate(agent_pts):
        draw.text((rx + 20, y1 + 85 + idx * 34), p, fill="#CBD5E1", font=get_font(13))

    draw.rounded_rectangle([(rx + 15, y1 + 265), (x2 - 30, y1 + 355)], radius=10, fill="#1E293B")
    draw.text((rx + 25, y1 + 280), "LOCAL INFERENCE SPEED:", fill="#F59E0B", font=get_font(12, bold=True))
    draw.text((rx + 25, y1 + 305), "Model: Llama-3-8B-Instruct (4-bit Q4_K_M)", fill="#E2E8F0", font=get_font(12))
    draw.text((rx + 25, y1 + 325), "Generation Rate: 74.2 tokens/second (Zero API Cost)", fill="#34D399", font=get_font(12))

def draw_devtools_git_visuals(draw, x1, y1, x2, y2, t):
    """Git Branching Graph & Automated CI/CD Deployment Pipeline."""
    # Left Side: Git Branch DAG
    gw = 400
    gx_start, gy_start = x1 + 25, y1 + 30
    draw.rounded_rectangle([(gx_start, gy_start), (gx_start + gw, y2 - 20)], radius=14, fill="#090D16", outline="#38BDF8", width=2)
    draw.text((gx_start + 20, gy_start + 18), "VERSION CONTROL & GIT ARCHITECTURE", fill="#38BDF8", font=get_font(13, bold=True, mono=True))
    
    # 3 Branches: main, feature/scale, release
    branches = [
        ("main", gy_start + 80, "#10B981"),
        ("feature/scale", gy_start + 160, "#F59E0B"),
        ("release/v2", gy_start + 240, "#A855F7")
    ]
    for b_name, by, b_col in branches:
        draw.line([(gx_start + 80, by), (gx_start + gw - 30, by)], fill=b_col, width=3)
        draw.text((gx_start + 15, by - 8), b_name, fill=b_col, font=get_font(10, bold=True, mono=True))
        # Commit nodes
        for c in range(4):
            cx_pos = gx_start + 110 + c * 65
            draw.ellipse([(cx_pos - 7, by - 7), (cx_pos + 7, by + 7)], fill="#0F172A", outline=b_col, width=3)

    # Animated Merge line
    phase = (t * 1.5) % 1.0
    mx = gx_start + 240 + int(phase * 65)
    draw.ellipse([(mx - 6, gy_start + 80 - 6), (mx + 6, gy_start + 80 + 6)], fill="#38BDF8")

    # Right Side: CI/CD Pipeline Stages
    rx = gx_start + gw + 30
    draw.rounded_rectangle([(rx, gy_start), (x2 - 15, y2 - 20)], radius=14, fill="#0F172A", outline="#10B981", width=2)
    draw.text((rx + 20, gy_start + 18), "PRODUCTION CI/CD AUTOMATION PIPELINE", fill="#10B981", font=get_font(14, bold=True))
    
    stages = [
        ("1. Static Code Analysis & Linters", "dart analyze & ruff check: 0 errors", "#10B981"),
        ("2. Automated Unit & Widget Tests", "Test Suite 100% PASS (Coverage: 94.2%)", "#10B981"),
        ("3. Containerized Docker Multi-Stage Build", "Image size reduced from 1.2GB to 85MB", "#38BDF8"),
        ("4. Zero-Downtime Deployment", "Rolling healthcheck deployment active", "#10B981")
    ]
    for idx, (st_name, st_desc, st_col) in enumerate(stages):
        sy = gy_start + 55 + idx * 58
        draw.rounded_rectangle([(rx + 15, sy), (x2 - 30, sy + 48)], radius=8, fill="#1E293B", outline=st_col, width=1)
        draw.text((rx + 25, sy + 8), st_name, fill="#FFFFFF", font=get_font(12, bold=True))
        draw.text((rx + 25, sy + 26), st_desc, fill=st_col, font=get_font(11, mono=True))

    draw.rounded_rectangle([(rx + 15, gy_start + 295), (x2 - 30, y2 - 35)], radius=8, fill="#1E1B4B")
    draw.text((rx + 25, gy_start + 305), "ARCHITECTURAL RULE:", fill="#F59E0B", font=get_font(12, bold=True))
    draw.text((rx + 25, gy_start + 325), "Automate everything that can fail human memory.", fill="#FFFFFF", font=get_font(13))

# Selector function for category archetype
def select_visual_archetype(category: str, title: str):
    sig = f"{category} {title}".upper()
    if "FLUTTER" in sig or "MOBILE" in sig or "DART" in sig:
        return draw_mobile_flutter_visuals, "MOBILE & FLUTTER"
    elif "BACKEND" in sig or "FASTAPI" in sig or "API" in sig or "DATABASE" in sig:
        return draw_backend_api_visuals, "BACKEND & APIS"
    elif "SECURITY" in sig or "CYBER" in sig or "INFOSEC" in sig:
        return draw_cybersecurity_visuals, "CYBERSECURITY & DEVSECOPS"
    elif "VISION" in sig or "MEDIAPIPE" in sig or "OPENCV" in sig or "TRACKING" in sig:
        return draw_computer_vision_visuals, "COMPUTER VISION & AR"
    elif "IOT" in sig or "ESP32" in sig or "HARDWARE" in sig or "MOTOR" in sig or "HCI" in sig:
        return draw_iot_hardware_visuals, "INDUSTRIAL IOT & HARDWARE"
    elif "AGENT" in sig or "OLLAMA" in sig or "LLM" in sig or "AI" in sig:
        return draw_agentic_ai_visuals, "AGENTIC AI & NEURAL SYSTEMS"
    else:
        return draw_devtools_git_visuals, "FULL-STACK & DEV TOOLS"

def create_video_frame(bg_img: Image.Image, t: float, duration: float, category: str, title: str, hook: str, lesson: str, spoken_text: str) -> np.ndarray:
    width, height = 1280, 720
    progress = min(1.0, max(0.0, t / duration))

    canvas = Image.new("RGB", (width, height), (11, 15, 23))
    draw = ImageDraw.Draw(canvas)

    # 1. Background gradient
    for y in range(height):
        ratio = y / height
        r = int(11 * (1 - ratio) + 15 * ratio)
        g = int(15 * (1 - ratio) + 23 * ratio)
        b = int(23 * (1 - ratio) + 42 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Subtle tech grid lines
    for gx in range(0, width, 80):
        draw.line([(gx, 0), (gx, height)], fill=(255, 255, 255, 10), width=1)
    for gy in range(0, height, 80):
        draw.line([(0, gy), (width, gy)], fill=(255, 255, 255, 10), width=1)

    # 2. Top Header (Haroon's Avatar + Equalizer + Category Badge)
    visual_fn, display_cat = select_visual_archetype(category, title)
    draw_header(draw, width, t, display_cat, canvas)

    # 3. Main Center Visual Arena (Unique Animation per Category!)
    x1, y1, x2, y2 = 50, 110, width - 50, 610
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=18, fill=(15, 23, 42, 235), outline="#334155", width=2)
    
    # Render the unique visual motion archetype!
    visual_fn(draw, x1, y1, x2, y2, t)

    # 4. Dynamic Kinetic Spoken Captions Box (Center-Bottom)
    sub_y1, sub_y2 = 625, 705
    draw.rounded_rectangle([(50, sub_y1), (width - 50, sub_y2)], radius=12, fill=(30, 41, 59, 245), outline="#38BDF8", width=2)
    draw.text((70, sub_y1 + 10), "🎙️ WHAT I DO & HOW I ARCHITECT IT:", fill="#38BDF8", font=get_font(12, bold=True, mono=True))

    full_quote = f'"{spoken_text}"'
    visible_chars = int(len(full_quote) * min(1.0, progress * 1.6))
    typed_quote = full_quote[:visible_chars]
    cursor = " █" if (int(t * 4) % 2 == 0 and visible_chars < len(full_quote)) else ""

    words = (typed_quote + cursor).split()
    quote_lines = []
    curr = []
    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > 75:
            quote_lines.append(" ".join(curr))
            curr = []
    if curr:
        quote_lines.append(" ".join(curr))

    qy = sub_y1 + 35
    for ql in quote_lines[:2]:
        draw.text((70, qy), ql, fill="#FEF08A", font=get_font(15, bold=True))
        qy += 22

    # 5. Bottom Duration Progress Bar
    bar_w = int(width * progress)
    draw.rectangle([(0, height - 6), (width, height)], fill="#0F172A")
    draw.rectangle([(0, height - 6), (bar_w, height)], fill="#38BDF8")

    return np.array(canvas)

def render_animated_video(bg_path: str, audio_path: str, output_path: str, category: str, title: str, hook: str, lesson: str, spoken_text: str) -> str:
    """Renders 720p HD animated MP4 video with synced neural voiceover and ambient music ducking."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    duration = get_audio_duration(audio_path) + 1.2
    fps = 25
    total_frames = int(duration * fps)

    bg_img = Image.open(bg_path).convert("RGB") if (bg_path and os.path.exists(bg_path)) else Image.new("RGB", (1280, 720), (11, 15, 23))
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
    
    render_animated_video(bg_path, audio_path, output_video_path, category, title, hook, lesson, script_text)
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
    return output_video_path
