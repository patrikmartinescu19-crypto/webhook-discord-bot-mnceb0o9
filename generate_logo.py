"""Generate the Undetected logo - a modern HUD-style shield with crosshair."""
import math
import os

from PIL import Image, ImageDraw, ImageFont


def create_logo(size=512):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    # Colors
    cyan = (0, 255, 242, 255)
    cyan_dim = (0, 255, 242, 80)

    # Background circle with gradient feel
    for r in range(220, 0, -1):
        alpha = int(255 * (1 - (r / 220) * 0.3))
        c = (12, 14, 22, alpha)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    # Outer ring
    for t in range(3):
        r = 200 - t
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=cyan, width=1)

    # Inner ring
    for t in range(2):
        r = 170 - t
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=cyan_dim, width=1)

    # Shield shape
    shield_w = 120
    top_y = cy - 80
    bot_y = cy + 80

    shield_coords = [
        (cx, top_y - 20),           # top center peak
        (cx + shield_w, top_y + 20),  # top right
        (cx + shield_w - 10, bot_y - 30),  # bottom right
        (cx, bot_y + 20),            # bottom center point
        (cx - shield_w + 10, bot_y - 30),  # bottom left
        (cx - shield_w, top_y + 20),  # top left
    ]
    draw.polygon(shield_coords, outline=cyan, fill=(0, 255, 242, 15))
    draw.polygon(shield_coords, outline=cyan)

    # Inner shield line
    inner_shield = [
        (cx, top_y - 5),
        (cx + shield_w - 20, top_y + 30),
        (cx + shield_w - 28, bot_y - 40),
        (cx, bot_y + 5),
        (cx - shield_w + 28, bot_y - 40),
        (cx - shield_w + 20, top_y + 30),
    ]
    draw.polygon(inner_shield, outline=cyan_dim)

    # Crosshair lines
    line_len = 40
    gap = 15
    lw = 2
    # Horizontal
    draw.line([(cx - line_len - gap, cy), (cx - gap, cy)], fill=cyan, width=lw)
    draw.line([(cx + gap, cy), (cx + line_len + gap, cy)], fill=cyan, width=lw)
    # Vertical
    draw.line([(cx, cy - line_len - gap), (cx, cy - gap)], fill=cyan, width=lw)
    draw.line([(cx, cy + gap), (cx, cy + line_len + gap)], fill=cyan, width=lw)

    # Center dot
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=cyan)

    # HUD tick marks around outer ring
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        if angle % 45 == 0:
            r1, r2 = 195, 210
            w = 2
        else:
            r1, r2 = 198, 206
            w = 1
        x1 = cx + r1 * math.cos(rad)
        y1 = cy + r1 * math.sin(rad)
        x2 = cx + r2 * math.cos(rad)
        y2 = cy + r2 * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=cyan, width=w)

    # Corner brackets (HUD style)
    blen = 30
    boff = 215
    bw = 2
    corners = [
        (cx - boff, cy - boff, 1, 1),
        (cx + boff, cy - boff, -1, 1),
        (cx - boff, cy + boff, 1, -1),
        (cx + boff, cy + boff, -1, -1),
    ]
    for (bx, by, dx, dy) in corners:
        draw.line([(bx, by), (bx + blen * dx, by)], fill=cyan, width=bw)
        draw.line([(bx, by), (bx, by + blen * dy)], fill=cyan, width=bw)

    # Text "UNDETECTED" below shield
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    text = "UNDETECTED"
    bbox = draw.textbbox((0, 0), text, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy + 100), text, fill=cyan, font=font_large)

    # Subtitle
    sub = "PC TWEAKS"
    bbox2 = draw.textbbox((0, 0), sub, font=font_small)
    sw = bbox2[2] - bbox2[0]
    draw.text((cx - sw // 2, cy + 140), sub, fill=(0, 255, 242, 180), font=font_small)

    return img


def create_icon(size=64):
    """Create a smaller icon version."""
    logo = create_logo(512)
    icon = logo.resize((size, size), Image.LANCZOS)
    return icon


if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    logo = create_logo(512)
    logo.save(os.path.join(assets_dir, "logo.png"))
    print("Created logo.png (512x512)")

    icon = create_icon(256)
    icon.save(os.path.join(assets_dir, "icon.png"))
    print("Created icon.png (256x256)")

    icon_ico = create_logo(256)
    icon_ico.save(os.path.join(assets_dir, "icon.ico"), format="ICO", sizes=[(256, 256)])
    print("Created icon.ico")
