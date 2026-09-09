from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math
import os

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSET_DIR, exist_ok=True)

CYAN = (0, 229, 255)
CYAN_SOFT = (0, 229, 255, 120)
DARK = (10, 13, 18)
DARK_CARD = (18, 24, 32)
WHITE = (255, 255, 255)


def save(img, name):
    img.save(os.path.join(ASSET_DIR, name))


def new_image(size, color=(0, 0, 0, 0)):
    return Image.new("RGBA", size, color)


def draw_rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


# ── 7-segment digit ──
def segment_poly(seg, w, h, pad):
    pw = w - pad * 2
    ph = (h - pad * 2) // 2 - 4
    sw = 10  # segment thickness
    mid_y = h // 2
    if seg == 0:
        return [(pad + sw, pad), (pad + pw - sw, pad), (pad + pw - sw * 2, pad + sw), (pad + sw * 2, pad + sw)]
    if seg == 3:
        return [(pad + sw, h - pad - sw), (pad + pw - sw, h - pad - sw), (pad + pw - sw * 2, h - pad), (pad + sw * 2, h - pad)]
    if seg == 6:
        return [(pad + sw, mid_y - sw // 2), (pad + pw - sw, mid_y - sw // 2), (pad + pw - sw * 2, mid_y + sw // 2), (pad + sw * 2, mid_y + sw // 2)]
    if seg == 1:
        return [(pad + pw - sw, pad + sw), (pad + pw, pad + sw), (pad + pw, mid_y - sw), (pad + pw - sw, mid_y - sw * 2)]
    if seg == 2:
        return [(pad + pw - sw, mid_y + sw), (pad + pw, mid_y + sw), (pad + pw, h - pad - sw), (pad + pw - sw, h - pad - sw * 2)]
    if seg == 5:
        return [(pad, pad + sw), (pad + sw, pad + sw), (pad + sw, mid_y - sw * 2), (pad, mid_y - sw)]
    if seg == 4:
        return [(pad, mid_y + sw), (pad + sw, mid_y + sw), (pad + sw, h - pad - sw * 2), (pad, h - pad - sw)]
    return []


DIGIT_SEGS = {
    0: [0, 1, 2, 3, 4, 5],
    1: [1, 2],
    2: [0, 1, 3, 4, 6],
    3: [0, 1, 2, 3, 6],
    4: [1, 2, 5, 6],
    5: [0, 2, 3, 5, 6],
    6: [0, 2, 3, 4, 5, 6],
    7: [0, 1, 2],
    8: [0, 1, 2, 3, 4, 5, 6],
    9: [0, 1, 2, 3, 5, 6],
}


def gen_digit(digit, size=(60, 90)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    for seg in DIGIT_SEGS[digit]:
        poly = segment_poly(seg, w, h, 4)
        # glow layer
        glow = [(x + (0 if i % 2 == 0 else 0), y + (0 if i % 2 == 1 else 0)) for i, (x, y) in enumerate(poly)]
        draw.polygon(poly, fill=(*CYAN, 80))
        # inner bright
        inner = [(x + (1 if i % 2 == 0 else -1), y + (1 if i % 2 == 1 else -1)) for i, (x, y) in enumerate(poly)]
        draw.polygon(inner, fill=(*CYAN, 255))
    # apply slight blur for neon glow
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    # redraw crisp segments on top after blur to keep readability
    draw2 = ImageDraw.Draw(img)
    for seg in DIGIT_SEGS[digit]:
        poly = segment_poly(seg, w, h, 4)
        draw2.polygon(poly, fill=(*CYAN, 220))
    return img


def gen_colon(size=(30, 90)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    r = 5
    cy1, cy2 = h // 2 - 18, h // 2 + 18
    draw.ellipse((w // 2 - r, cy1 - r, w // 2 + r, cy1 + r), fill=(*CYAN, 200))
    draw.ellipse((w // 2 - r, cy2 - r, w // 2 + r, cy2 + r), fill=(*CYAN, 200))
    return img


# ── Glowing ring ──
def gen_ring(size=(640, 640)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    outer_r = min(cx, cy) - 10
    inner_r = outer_r - 36

    # outer glow
    for i in range(8, 0, -1):
        r_out = outer_r + i * 4
        r_in = inner_r - i * 4
        alpha = max(0, 30 - i * 3)
        draw.ellipse((cx - r_out, cy - r_out, cx + r_out, cy + r_out),
                     fill=(*CYAN, alpha), outline=None)
        draw.ellipse((cx - r_in, cy - r_in, cx + r_in, cy + r_in),
                     fill=(0, 0, 0, 0), outline=None)

    # main ring body
    draw.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r),
                 fill=(*CYAN, 255), outline=None)
    draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
                 fill=(0, 0, 0, 0), outline=None)

    # highlight
    draw.ellipse((cx - outer_r + 4, cy - outer_r + 4, cx + outer_r - 4, cy + outer_r - 4),
                 outline=(*CYAN, 180), width=2)

    # design tick marks at 9 and 3 o'clock
    tick_w, tick_h = 28, 14
    for side in (-1, 1):
        tx = cx + side * outer_r
        for i in range(5, 0, -1):
            draw.rounded_rectangle(
                (tx - tick_w // 2 - i, cy - tick_h // 2 - i,
                 tx + tick_w // 2 + i, cy + tick_h // 2 + i),
                radius=tick_h // 2,
                fill=(*CYAN, max(0, 80 - i * 14)))
        draw.rounded_rectangle(
            (tx - tick_w // 2, cy - tick_h // 2,
             tx + tick_w // 2, cy + tick_h // 2),
            radius=tick_h // 2,
            fill=WHITE)

    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    return img


# ── Circular +/- button ──
def gen_circle_symbol(symbol, size=(90, 90)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    r = w // 2 - 4

    # outer glow
    for i in range(6, 0, -1):
        draw.ellipse((cx - r - i, cy - r - i, cx + r + i, cy + r + i),
                     outline=(*CYAN, max(0, 50 - i * 8)), width=2)

    # circle border
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=CYAN, width=3)

    # symbol
    if symbol == "minus":
        draw.line([(cx - 18, cy), (cx + 18, cy)], fill=WHITE, width=4)
    elif symbol == "plus":
        draw.line([(cx - 18, cy), (cx + 18, cy)], fill=WHITE, width=4)
        draw.line([(cx, cy - 18), (cx, cy + 18)], fill=WHITE, width=4)

    return img


# ── Power button ──
def gen_power_btn(size=(60, 60)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    r = w // 2 - 4

    # glow
    for i in range(5, 0, -1):
        draw.ellipse((cx - r - i, cy - r - i, cx + r + i, cy + r + i),
                     outline=(*CYAN, max(0, 60 - i * 10)), width=2)

    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=CYAN, width=3)
    # power symbol: vertical line through top gap + 300° arc (gap at top)
    draw.line([(cx, cy - 15), (cx, cy + 3)], fill=WHITE, width=4)
    draw.arc((cx - 11, cy - 11, cx + 11, cy + 11), start=300, end=240, fill=WHITE, width=4)
    return img


# ── Light ball ──
def gen_light_ball(color, size=(120, 120)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    r = w // 2 - 10

    # outer glow
    for i in range(18, 0, -1):
        draw.ellipse((cx - r - i * 2, cy - r - i * 2, cx + r + i * 2, cy + r + i * 2),
                     fill=(*color, max(0, 55 - i * 3)))

    # ball body
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    # bright specular
    draw.ellipse((cx - r // 3, cy - r // 2, cx + r // 5, cy - r // 6), fill=(255, 255, 255, 160))

    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    return img


# ── Neon title ──
def gen_title(size=(280, 56)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    text = "AQUA CORE"

    try:
        font = ImageFont.truetype("arialbd.ttf", 42)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (w - tw) // 2 - bbox[0]
    ty = (h - th) // 2 - bbox[1]

    # strong glow layers
    for i in range(14, 0, -1):
        alpha = max(0, 90 - i * 6)
        draw.text((tx, ty - i), text, font=font, fill=(*CYAN, alpha))
        draw.text((tx, ty + i), text, font=font, fill=(*CYAN, alpha))
        draw.text((tx - i, ty), text, font=font, fill=(*CYAN, alpha))
        draw.text((tx + i, ty), text, font=font, fill=(*CYAN, alpha))
        draw.text((tx - i, ty - i), text, font=font, fill=(*CYAN, alpha // 2))
        draw.text((tx + i, ty - i), text, font=font, fill=(*CYAN, alpha // 2))
        draw.text((tx - i, ty + i), text, font=font, fill=(*CYAN, alpha // 2))
        draw.text((tx + i, ty + i), text, font=font, fill=(*CYAN, alpha // 2))

    # crisp top
    draw.text((tx, ty), text, font=font, fill=CYAN)
    draw.text((tx + 1, ty), text, font=font, fill=WHITE)
    draw.text((tx, ty - 1), text, font=font, fill=(200, 255, 255))
    return img


# ── Color dots ──
def gen_color_dot(color, size=(48, 48)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, h // 2
    r = w // 2 - 4
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    draw.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), fill=(*color, 200))
    return img


# ── Chevron (wheel picker arrows) ──
def gen_chevron(direction, size=(60, 60)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    cx = w // 2
    if direction == "up":
        pts = [(cx - 16, h // 2 + 10), (cx, h // 2 - 10), (cx + 16, h // 2 + 10)]
    else:
        pts = [(cx - 16, h // 2 - 10), (cx, h // 2 + 10), (cx + 16, h // 2 - 10)]
    # glow
    for i in range(5, 0, -1):
        draw.line(pts, fill=(*CYAN, max(0, 70 - i * 12)), width=6 + i * 2, joint="curve")
    # crisp line
    draw.line(pts, fill=CYAN, width=5, joint="curve")
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return img


def gen_preset_btn_active(size=(200, 70)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    r = 20
    # glow
    for i in range(4, 0, -1):
        draw.rounded_rectangle((i, i, w - i, h - i), radius=r, outline=(*CYAN, max(0, 80 - i * 15)), width=2)
    draw.rounded_rectangle((0, 0, w, h), radius=r, fill=CYAN)
    return img


def gen_preset_btn_inactive(size=(200, 70)):
    img = new_image(size)
    draw = ImageDraw.Draw(img)
    w, h = size
    r = 20
    draw.rounded_rectangle((0, 0, w, h), radius=r, fill=DARK_CARD)
    draw.rounded_rectangle((2, 2, w - 2, h - 2), radius=r - 2, outline=CYAN, width=2)
    return img


def _gradient_btn(size, top, bot):
    """Rounded gradient button with glow and shine (proper alpha blending)."""
    w, h = size
    r = 24

    # glow behind
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gwd = ImageDraw.Draw(glow)
    gwd.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=(*top, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=8))

    # vertical gradient body
    grad = Image.new("RGB", size)
    gd = ImageDraw.Draw(grad)
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        gd.line([(0, yy), (w, yy)], fill=col)

    mask = Image.new("L", size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)

    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    body = Image.new("RGBA", size, (0, 0, 0, 0))
    body.paste(grad, (0, 0), mask)
    out.alpha_composite(body)

    # shine on separate layer so alpha blends instead of replacing pixels
    shine = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    sd.rounded_rectangle((6, 5, w - 6, h // 2), radius=r - 4, fill=(255, 255, 255, 46))
    out.alpha_composite(shine)
    return out


def gen_start_btn(size=(720, 100)):
    return _gradient_btn(size, (34, 211, 238), (8, 145, 178))


def gen_stop_btn(size=(720, 100)):
    """Active-state button: pink -> purple vertical gradient with glow."""
    return _gradient_btn(size, (236, 72, 153), (168, 85, 247))


if __name__ == "__main__":
    # Digits
    for d in range(10):
        save(gen_digit(d, (60, 90)), f"digit_{d}.png")
    save(gen_colon((30, 90)), "digit_colon.png")

    # Ring
    save(gen_ring((560, 560)), "ring_bg.png")

    # Title neon image (Lua default label can't render glow)
    save(gen_title((280, 56)), "title_aqua_core.png")

    # Buttons
    save(gen_circle_symbol("minus", (90, 90)), "btn_minus.png")
    save(gen_circle_symbol("plus", (90, 90)), "btn_plus.png")
    save(gen_power_btn((60, 60)), "power_btn.png")

    # Light balls per color
    save(gen_light_ball((0, 229, 255), (120, 120)), "light_ball_cyan.png")
    save(gen_light_ball((236, 72, 153), (120, 120)), "light_ball_pink.png")
    save(gen_light_ball((168, 85, 247), (120, 120)), "light_ball_purple.png")
    save(gen_light_ball((59, 130, 246), (120, 120)), "light_ball_blue.png")

    # Color dots
    save(gen_color_dot((0, 229, 255)), "color_dot_cyan.png")
    save(gen_color_dot((236, 72, 153)), "color_dot_pink.png")
    save(gen_color_dot((168, 85, 247)), "color_dot_purple.png")
    save(gen_color_dot((59, 130, 246)), "color_dot_blue.png")

    # Preset backgrounds
    save(gen_preset_btn_active((200, 70)), "preset_active.png")
    save(gen_preset_btn_inactive((200, 70)), "preset_inactive.png")

    # Wheel picker chevrons
    save(gen_chevron("up", (60, 60)), "chevron_up.png")
    save(gen_chevron("down", (60, 60)), "chevron_down.png")

    # Start button background
    save(gen_start_btn((720, 100)), "start_btn.png")
    save(gen_stop_btn((720, 100)), "stop_btn.png")

    print("assets generated")
