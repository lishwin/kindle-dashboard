# -*- coding: utf-8 -*-
import os
import io
import time
import math
import datetime
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1072
HEIGHT = 1448
CITY_NAME = "北京"
LATITUDE = 39.9042
LONGITUDE = 116.4074

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(CURRENT_DIR, "fonts")
BUNDLED_FONT = os.path.join(FONT_DIR, "font_main.ttc")

def find_font():
    candidates = [
        BUNDLED_FONT,
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/msyh.ttc"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

FONT_PATH = find_font()

WEATHER_CODES = {
    0: "晴朗", 1: "晴间多云", 2: "多云", 3: "阴天",
    45: "有雾", 48: "浓雾", 51: "小毛毛雨", 53: "毛毛�?, 55: "密毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨", 71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨", 81: "中阵�?, 82: "强阵�?, 85: "阵雪", 86: "大阵�?,
    95: "雷阵�?, 96: "雷雨伴冰�?, 99: "强雷�?
}

WEEKDAYS_CN = ["星期一", "星期�?, "星期�?, "星期�?, "星期�?, "星期�?, "星期�?]

def get_font(size):
    if FONT_PATH:
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except:
            pass
    return ImageFont.load_default()

def fetch_weather():
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LATITUDE}&longitude={LONGITUDE}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,wind_speed_10m&"
            f"daily=weather_code,temperature_2m_max,temperature_2m_min,uv_index_max&"
            f"timezone=Asia%2FShanghai&forecast_days=5"
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'KindleVoyageCloud/1.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print("Weather fetch error:", e)
        return None

def fetch_quote():
    try:
        req = urllib.request.Request('https://v1.hitokoto.cn/?c=d&c=i&c=k&c=h', headers={'User-Agent': 'KindleVoyageCloud/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get('hitokoto', ''), data.get('from_who') or data.get('from') or ''
    except Exception as e:
        return "博学之，审问之，慎思之，明辨之，笃行之�?, "《礼记·中庸�?

def draw_rounded_card(draw, box, radius=16, outline=180, fill=255, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)

def draw_weather_icon(draw, icon_type, cx, cy, size=130):
    stroke = 6
    if "�? in icon_type and "�? not in icon_type and "�? not in icon_type:
        # SUN
        r_core = int(size * 0.28)
        draw.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=0)
        ray_len = int(size * 0.16)
        ray_start = r_core + 8
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = cx + int(math.cos(rad) * ray_start)
            y1 = cy + int(math.sin(rad) * ray_start)
            x2 = cx + int(math.cos(rad) * (ray_start + ray_len))
            y2 = cy + int(math.sin(rad) * (ray_start + ray_len))
            draw.line([(x1, y1), (x2, y2)], fill=0, width=stroke)
            
    elif "�? in icon_type or "阵雨" in icon_type or "�? in icon_type:
        # CLOUD + RAIN
        top_y = cy - int(size * 0.2)
        draw.ellipse([cx - 50, top_y - 15, cx - 10, top_y + 25], fill=0)
        draw.ellipse([cx - 20, top_y - 35, cx + 30, top_y + 15], fill=0)
        draw.ellipse([cx + 10, top_y - 15, cx + 50, top_y + 25], fill=0)
        draw.rectangle([cx - 40, top_y + 5, cx + 40, top_y + 25], fill=0)
        rain_y = top_y + 38
        for dx in [-30, -10, 10, 30]:
            draw.line([(cx + dx, rain_y), (cx + dx - 6, rain_y + 22)], fill=0, width=5)
            
    elif "�? in icon_type:
        # CLOUD + SNOW
        top_y = cy - int(size * 0.2)
        draw.ellipse([cx - 50, top_y - 15, cx - 10, top_y + 25], fill=0)
        draw.ellipse([cx - 20, top_y - 35, cx + 30, top_y + 15], fill=0)
        draw.ellipse([cx + 10, top_y - 15, cx + 50, top_y + 25], fill=0)
        draw.rectangle([cx - 40, top_y + 5, cx + 40, top_y + 25], fill=0)
        for dx in [-25, 0, 25]:
            draw.ellipse([cx + dx - 5, top_y + 42, cx + dx + 5, top_y + 52], fill=0)
            
    elif "�? in icon_type:
        # FOG
        for idx, (w, dy) in enumerate([(100, -25), (120, 0), (90, 25)]):
            draw.rounded_rectangle([cx - w//2, cy + dy - 5, cx + w//2, cy + dy + 5], radius=5, fill=0)
            
    else:
        # CLOUD (Default)
        top_y = cy
        draw.ellipse([cx - 55, top_y - 20, cx - 10, top_y + 25], fill=0)
        draw.ellipse([cx - 25, top_y - 45, cx + 35, top_y + 15], fill=0)
        draw.ellipse([cx + 10, top_y - 20, cx + 55, top_y + 25], fill=0)
        draw.rectangle([cx - 45, top_y + 5, cx + 45, top_y + 25], fill=0)

def generate_image_bytes():
    img = Image.new("L", (WIDTH, HEIGHT), color=255)
    draw = ImageDraw.Draw(img)

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    beijing_now = utc_now + datetime.timedelta(hours=8)
    
    weather = fetch_weather()
    quote_text, quote_author = fetch_quote()

    # --- 1. HEADER (Big Date Calendar Style) ---
    day_num_str = str(beijing_now.day)
    year_month_str = f"{beijing_now.year}�?{beijing_now.month}�?
    weekday_str = WEEKDAYS_CN[beijing_now.weekday()]
    
    font_huge_day = get_font(130)
    font_ym = get_font(34)
    font_wk = get_font(42)
    font_city = get_font(26)
    
    draw.text((60, 35), day_num_str, font=font_huge_day, fill=0)
    
    bbox_day = draw.textbbox((0, 0), day_num_str, font=font_huge_day)
    offset_x = 60 + (bbox_day[2] - bbox_day[0]) + 30
    
    draw.text((offset_x, 50), year_month_str, font=font_ym, fill=80)
    draw.text((offset_x, 100), weekday_str, font=font_wk, fill=0)
    
    meta_text = f"{CITY_NAME} · 今日天气日历"
    bbox_meta = draw.textbbox((0, 0), meta_text, font=font_city)
    draw.text((WIDTH - 60 - (bbox_meta[2] - bbox_meta[0]), 110), meta_text, font=font_city, fill=100)
    
    draw.line([(60, 200), (WIDTH - 60, 200)], fill=200, width=2)

    # --- 2. CARD 1: DAILY INSPIRATION (今日寄语 - 黑底白字，特大字�? ---
    draw_rounded_card(draw, [60, 230, WIDTH - 60, 530], radius=24, outline=0, fill=0, width=1)
    draw.text((95, 255), "�?今日寄语 �? (Daily Inspiration)", font=get_font(24), fill=180)
    draw.line([(95, 295), (WIDTH - 95, 295)], fill=80, width=1)
    
    words = quote_text
    lines = []
    line = ""
    for char in words:
        if len(line) >= 22:
            lines.append(line)
            line = char
        else:
            line += char
    if line:
        lines.append(line)
        
    y_text = 320
    font_quote_large = get_font(38)
    for l in lines[:3]:
        draw.text((95, y_text), l, font=font_quote_large, fill=255)
        y_text += 54
        
    if quote_author:
        author_str = f"—�?{quote_author}"
        font_author = get_font(26)
        bbox = draw.textbbox((0, 0), author_str, font=font_author)
        draw.text((WIDTH - 95 - (bbox[2] - bbox[0]), 475), author_str, font=font_author, fill=200)

    # --- 3. CARD 2: 5-DAY FORECAST (近期天气预报) ---
    draw_rounded_card(draw, [60, 555, WIDTH - 60, 925], radius=20, outline=160, fill=255, width=3)
    draw.text((95, 580), "近期天气预报 (5-Day Forecast)", font=get_font(28), fill=40)
    draw.line([(95, 620), (WIDTH - 95, 620)], fill=230, width=1)
    
    if weather and 'daily' in weather:
        daily = weather['daily']
        col_width = (WIDTH - 190) // 5
        for i in range(min(5, len(daily['time']))):
            d_date = datetime.datetime.strptime(daily['time'][i], "%Y-%m-%d")
            day_name = "今天" if i == 0 else ("明天" if i == 1 else WEEKDAYS_CN[d_date.weekday()][2:])
            desc = WEATHER_CODES.get(daily['weather_code'][i], "多云")
            t_max = round(daily['temperature_2m_max'][i])
            t_min = round(daily['temperature_2m_min'][i])
            x_center = 95 + i * col_width + col_width // 2
            
            bbox = draw.textbbox((0, 0), day_name, font=get_font(26))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 645), day_name, font=get_font(26), fill=0)
            
            d_str = d_date.strftime("%m/%d")
            bbox = draw.textbbox((0, 0), d_str, font=get_font(22))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 685), d_str, font=get_font(22), fill=100)
            
            bbox = draw.textbbox((0, 0), desc, font=get_font(24))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 745), desc, font=get_font(24), fill=30)
            
            t_str = f"{t_min}°~{t_max}°"
            bbox = draw.textbbox((0, 0), t_str, font=get_font(26))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 815), t_str, font=get_font(26), fill=0)

    # --- 4. CARD 3: TODAY WEATHER WITH LARGE ICON (当日天气 + 超大天气图标) ---
    draw_rounded_card(draw, [60, 950, WIDTH - 60, 1390], radius=20, outline=160, fill=255, width=3)
    draw.text((95, 975), f"{CITY_NAME} · 实时天气 (Current Weather)", font=get_font(28), fill=40)
    draw.line([(95, 1015), (WIDTH - 95, 1015)], fill=230, width=1)
    
    if weather and 'current' in weather:
        curr = weather['current']
        daily = weather['daily']
        temp = round(curr.get('temperature_2m', 0))
        feels_like = round(curr.get('apparent_temperature', temp))
        humidity = curr.get('relative_humidity_2m', 0)
        wind_speed = round(curr.get('wind_speed_10m', 0))
        w_desc = WEATHER_CODES.get(curr.get('weather_code', 0), "多云")
        
        max_today = round(daily['temperature_2m_max'][0])
        min_today = round(daily['temperature_2m_min'][0])
        uv_today = round(daily.get('uv_index_max', [0])[0])
        
        # Left: Huge Temp & Condition
        draw.text((95, 1035), f"{temp}°", font=get_font(105), fill=0)
        draw.text((320, 1045), f"{w_desc}", font=get_font(42), fill=20)
        draw.text((320, 1105), f"今日气温 {min_today}°C ~ {max_today}°C  |  体感 {feels_like}°C", font=get_font(25), fill=80)
        
        # Right: Big Weather Icon matching temperature size!
        draw_weather_icon(draw, w_desc, cx=WIDTH - 180, cy=1090, size=135)
        
        # Divider Line
        draw.line([(95, 1180), (WIDTH - 95, 1180)], fill=220, width=2)
        
        # Grid metrics
        draw.text((100, 1205), "空气湿度", font=get_font(24), fill=110)
        draw.text((100, 1245), f"{humidity}%", font=get_font(32), fill=0)
        
        draw.text((340, 1205), "风速风�?, font=get_font(24), fill=110)
        draw.text((340, 1245), f"{wind_speed} km/h", font=get_font(32), fill=0)
        
        draw.text((580, 1205), "紫外线指�?, font=get_font(24), fill=110)
        uv_desc = "�? if uv_today <= 2 else ("中等" if uv_today <= 5 else "较强")
        draw.text((580, 1245), f"{uv_today} ({uv_desc})", font=get_font(32), fill=0)
        
        draw.text((820, 1205), "今日温差", font=get_font(24), fill=110)
        draw.text((820, 1245), f"{max_today - min_today}°C", font=get_font(32), fill=0)

    # --- 5. FOOTER ---
    footer_text = "Kindle Voyage 桌面天气日历"
    bbox = draw.textbbox((0, 0), footer_text, font=get_font(22))
    draw.text((WIDTH // 2 - (bbox[2]-bbox[0])//2, 1415), footer_text, font=get_font(22), fill=130)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

if __name__ == "__main__":
    with open("dashboard.png", "wb") as f:
        f.write(generate_image_bytes())
    print("New high contrast dashboard.png generated successfully!")
