import os
from PIL import Image, ImageDraw, ImageFont

def generate_technical_card(day_num: int, title: str, category: str, hook: str, output_path: str) -> str:
    """
    Generates an ultra-clean, high-authority dark-mode developer infographic card
    suitable for LinkedIn carousel / single-image posts (1200 x 675 px / 16:9).
    """
    width = 1200
    height = 675
    
    # 1. Background gradient / dark canvas
    img = Image.new("RGB", (width, height), color="#0F172A") # Slate 900
    draw = ImageDraw.Draw(img)
    
    # Header Accent bar
    draw.rectangle([(0, 0), (width, 10)], fill="#38BDF8") # Cyan-400 accent
    
    # Background subtle grid / card frame
    draw.rounded_rectangle([(40, 40), (width - 40, height - 40)], radius=24, outline="#1E293B", width=2, fill="#0F172A")
    
    # Try loading clean system fonts (fallback to default)
    try:
        font_tag = ImageFont.truetype("arialbd.ttf", 20)
        font_day = ImageFont.truetype("arialbd.ttf", 36)
        font_title = ImageFont.truetype("arialbd.ttf", 46)
        font_hook = ImageFont.truetype("arial.ttf", 26)
        font_footer = ImageFont.truetype("arialbd.ttf", 22)
    except Exception:
        font_tag = ImageFont.load_default()
        font_day = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_hook = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Category Pill
    pill_text = f"  {category.upper()}  "
    draw.rounded_rectangle([(70, 70), (320, 110)], radius=10, fill="#1E293B", outline="#38BDF8", width=1)
    draw.text((85, 78), pill_text, fill="#38BDF8", font=font_tag)
    
    # Engineering insight badge
    draw.text((width - 330, 80), "ENGINEERING INSIGHT", fill="#94A3B8", font=font_tag)
    
    # Title (Word wrap)
    words = title.split()
    lines = []
    curr_line = []
    for w in words:
        curr_line.append(w)
        if len(" ".join(curr_line)) > 36:
            lines.append(" ".join(curr_line))
            curr_line = []
    if curr_line:
        lines.append(" ".join(curr_line))
        
    y_text = 160
    for line in lines[:3]:
        draw.text((75, y_text), line, fill="#F8FAFC", font=font_title)
        y_text += 58
        
    # Divider line
    y_text += 10
    draw.line([(75, y_text), (width - 75, y_text)], fill="#334155", width=2)
    y_text += 30
    
    # Hook / Key Takeaway box
    draw.rounded_rectangle([(75, y_text), (width - 75, y_text + 150)], radius=16, fill="#1E293B")
    
    # Terminal-like indicator dots (Mac OS / IDE style)
    draw.ellipse([(95, y_text + 20), (107, y_text + 32)], fill="#EF4444")
    draw.ellipse([(115, y_text + 20), (127, y_text + 32)], fill="#F59E0B")
    draw.ellipse([(135, y_text + 20), (147, y_text + 32)], fill="#10B981")
    
    # Hook Text
    clean_hook = hook.replace('"', '').replace('\n', ' ')
    hook_words = clean_hook.split()
    h_lines = []
    curr_h = []
    for w in hook_words:
        curr_h.append(w)
        if len(" ".join(curr_h)) > 68:
            h_lines.append(" ".join(curr_h))
            curr_h = []
    if curr_h:
        h_lines.append(" ".join(curr_h))
        
    hy = y_text + 55
    for hl in h_lines[:2]:
        draw.text((95, hy), f"> {hl}", fill="#E2E8F0", font=font_hook)
        hy += 36
        
    # Footer branding
    draw.text((75, height - 90), "MUHAMMAD HAROON | FULL-STACK & AI ARCHITECT", fill="#38BDF8", font=font_footer)
    draw.text((width - 340, height - 90), "FastAPI • Ollama • Flutter • CV", fill="#64748B", font=font_tag)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    return output_path
