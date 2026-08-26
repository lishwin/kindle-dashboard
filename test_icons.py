import math
from PIL import Image, ImageDraw

def draw_weather_icon(draw, icon_type, cx, cy, size=130):
    stroke = 6
    if "晴" in icon_type and "云" not in icon_type and "雨" not in icon_type:
        # 1. SUN ICON
        r_core = int(size * 0.28)
        draw.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=0)
        # Rays
        ray_len = int(size * 0.16)
        ray_start = r_core + 8
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = cx + int(math.cos(rad) * ray_start)
            y1 = cy + int(math.sin(rad) * ray_start)
            x2 = cx + int(math.cos(rad) * (ray_start + ray_len))
            y2 = cy + int(math.sin(rad) * (ray_start + ray_len))
            draw.line([(x1, y1), (x2, y2)], fill=0, width=stroke)
            
    elif "雨" in icon_type or "阵雨" in icon_type or "雷" in icon_type:
        # 2. CLOUD + RAIN
        top_y = cy - int(size * 0.2)
        # Cloud base
        draw.ellipse([cx - 50, top_y - 15, cx - 10, top_y + 25], fill=0)
        draw.ellipse([cx - 20, top_y - 35, cx + 30, top_y + 15], fill=0)
        draw.ellipse([cx + 10, top_y - 15, cx + 50, top_y + 25], fill=0)
        draw.rectangle([cx - 40, top_y + 5, cx + 40, top_y + 25], fill=0)
        # Rain drops
        rain_y = top_y + 38
        for dx in [-30, -10, 10, 30]:
            draw.line([(cx + dx, rain_y), (cx + dx - 6, rain_y + 22)], fill=0, width=5)
            
    elif "雪" in icon_type:
        # 3. CLOUD + SNOW
        top_y = cy - int(size * 0.2)
        draw.ellipse([cx - 50, top_y - 15, cx - 10, top_y + 25], fill=0)
        draw.ellipse([cx - 20, top_y - 35, cx + 30, top_y + 15], fill=0)
        draw.ellipse([cx + 10, top_y - 15, cx + 50, top_y + 25], fill=0)
        draw.rectangle([cx - 40, top_y + 5, cx + 40, top_y + 25], fill=0)
        # Snow dots/asterisks
        for dx in [-25, 0, 25]:
            draw.ellipse([cx + dx - 5, top_y + 42, cx + dx + 5, top_y + 52], fill=0)
            
    elif "雾" in icon_type:
        # 4. FOG BARS
        for idx, (w, dy) in enumerate([(100, -25), (120, 0), (90, 25)]):
            draw.rounded_rectangle([cx - w//2, cy + dy - 5, cx + w//2, cy + dy + 5], radius=5, fill=0)
            
    else:
        # 5. CLOUDY / OVERCAST (Default)
        top_y = cy
        draw.ellipse([cx - 55, top_y - 20, cx - 10, top_y + 25], fill=0)
        draw.ellipse([cx - 25, top_y - 45, cx + 35, top_y + 15], fill=0)
        draw.ellipse([cx + 10, top_y - 20, cx + 55, top_y + 25], fill=0)
        draw.rectangle([cx - 45, top_y + 5, cx + 45, top_y + 25], fill=0)

img = Image.new("L", (800, 200), color=255)
draw = ImageDraw.Draw(img)
for i, cond in enumerate(["晴朗", "多云", "小雨", "小雪", "有雾"]):
    draw_weather_icon(draw, cond, 80 + i * 160, 100, size=120)
img.save("C:/Users/lishw/.gemini/antigravity/brain/5a6f5cc8-65c3-4d3a-a2e3-01dcd9a57c07/scratch/test_icons.png")
print("Icons rendered")