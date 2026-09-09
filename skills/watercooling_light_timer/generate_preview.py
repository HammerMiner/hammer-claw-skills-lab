from PIL import Image, ImageDraw, ImageFilter
import math

W, H = 128, 128
img = Image.new('RGBA', (W, H), (13, 17, 23, 255))
draw = ImageDraw.Draw(img)

# Background radial gradient
for r in range(W, 0, -1):
    t = r / W
    c = (
        int(22 + (13-22)*t),
        int(33 + (17-33)*t),
        int(62 + (23-62)*t),
        255
    )
    draw.ellipse([W//2-r, H//2-r, W//2+r, H//2+r], fill=c)

ring_r = 42
cx, cy = W//2, H//2

# Outer gradient ring glow
glow = Image.new('RGBA', (W, H), (0,0,0,0))
glowd = ImageDraw.Draw(glow)
steps = 90
for i in range(steps):
    t = i / steps
    r = int(0 + (255-0)*t)
    g = int(240 + (0-240)*t)
    b = int(255 + (170-255)*t)
    color = (r, g, b, 120)
    a1 = -90 + i * 4
    a2 = a1 + 4
    glowd.arc([cx-ring_r-6, cy-ring_r-6, cx+ring_r+6, cy+ring_r+6], a1, a2, fill=color, width=8)
glow = glow.filter(ImageFilter.GaussianBlur(radius=4))
img = Image.alpha_composite(img, glow)
draw = ImageDraw.Draw(img)

# Outer gradient ring
for i in range(steps):
    t = i / steps
    r = int(0 + (255-0)*t)
    g = int(240 + (0-240)*t)
    b = int(255 + (170-255)*t)
    color = (r, g, b, 255)
    a1 = -90 + i * 4
    a2 = a1 + 4
    draw.arc([cx-ring_r-4, cy-ring_r-4, cx+ring_r+4, cy+ring_r+4], a1, a2, fill=color, width=4)

# Inner dark circle
draw.ellipse([cx-ring_r+5, cy-ring_r+5, cx+ring_r-5, cy+ring_r-5], fill=(13,17,23,255))

# Clock arc (cyan-white glow)
clock_glow = Image.new('RGBA', (W, H), (0,0,0,0))
cgd = ImageDraw.Draw(clock_glow)
cgd.arc([cx-ring_r+8, cy-ring_r+8, cx+ring_r-8, cy+ring_r-8], 90, 210, fill=(200,255,255,200), width=3)
clock_glow = clock_glow.filter(ImageFilter.GaussianBlur(radius=2))
img = Image.alpha_composite(img, clock_glow)

# Fan blades with glow
blade_glow = Image.new('RGBA', (W, H), (0,0,0,0))
bgd = ImageDraw.Draw(blade_glow)
for i in range(6):
    angle = i * 60
    x1 = cx + 12 * math.cos(math.radians(angle))
    y1 = cy + 12 * math.sin(math.radians(angle))
    x2 = cx + 28 * math.cos(math.radians(angle))
    y2 = cy + 28 * math.sin(math.radians(angle))
    bgd.line([(x1,y1),(x2,y2)], fill=(0, 240, 255, 180), width=3)
blade_glow = blade_glow.filter(ImageFilter.GaussianBlur(radius=2))
img = Image.alpha_composite(img, blade_glow)

# Center bright dot
draw.ellipse([cx-5, cy-5, cx+5, cy+5], fill=(255,255,255,255))

img.save('preview.png', 'PNG', optimize=True)
print('generated preview.png')
