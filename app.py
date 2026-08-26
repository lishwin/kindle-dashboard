# -*- coding: utf-8 -*-
import os
import io
import time
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
    45: "有雾", 48: "浓雾", 51: "小毛毛雨", 53: "毛毛雨", 55: "密毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨", 71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨", 81: "中阵雨", 82: "强阵雨", 85: "阵雪", 86: "大阵雪",
    95: "雷阵雨", 96: "雷雨伴冰雹", 99: "强雷暴"
}

WEEKDAYS_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

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
        return "博学之，审问之，慎思之，明辨之，笃行之。", "《礼记·中庸》"

def draw_rounded_card(draw, box, radius=16, outline=180, fill=255, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)

def generate_image_bytes():
    img = Image.new("L", (WIDTH, HEIGHT), color=255)
    draw = ImageDraw.Draw(img)

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    beijing_now = utc_now + datetime.timedelta(hours=8)
    
    weather = fetch_weather()
    quote_text, quote_author = fetch_quote()

    # --- 1. HEADER (Big Date Calendar Style) ---
    day_num_str = str(beijing_now.day)
    year_month_str = f"{beijing_now.year}年 {beijing_now.month}月"
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

    # --- 2. CARD 1: DAILY INSPIRATION (今日寄语 - 移至顶部) ---
    draw_rounded_card(draw, [60, 230, WIDTH - 60, 520], radius=20, outline=160, fill=255, width=3)
    draw.text((95, 250), "今日寄语 (Daily Inspiration)", font=get_font(28), fill=40)
    draw.line([(95, 290), (WIDTH - 95, 290)], fill=230, width=1)
    
    words = quote_text
    lines = []
    line = ""
    for char in words:
        if len(line) >= 26:
            lines.append(line)
            line = char
        else:
            line += char
    if line:
        lines.append(line)
        
    y_text = 315
    for l in lines[:3]:
        draw.text((100, y_text), l, font=get_font(30), fill=20)
        y_text += 44
        
    if quote_author:
        author_str = f"—— {quote_author}"
        bbox = draw.textbbox((0, 0), author_str, font=get_font(24))
        draw.text((WIDTH - 100 - (bbox[2] - bbox[0]), 465), author_str, font=get_font(24), fill=90)

    # --- 3. CARD 2: 5-DAY FORECAST (近期预报 - 中间) ---
    draw_rounded_card(draw, [60, 545, WIDTH - 60, 915], radius=20, outline=160, fill=255, width=3)
    draw.text((95, 570), "近期天气预报 (5-Day Forecast)", font=get_font(28), fill=40)
    draw.line([(95, 610), (WIDTH - 95, 610)], fill=230, width=1)
    
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
            draw.text((x_center - (bbox[2]-bbox[0])//2, 635), day_name, font=get_font(26), fill=0)
            
            d_str = d_date.strftime("%m/%d")
            bbox = draw.textbbox((0, 0), d_str, font=get_font(22))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 675), d_str, font=get_font(22), fill=100)
            
            bbox = draw.textbbox((0, 0), desc, font=get_font(24))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 735), desc, font=get_font(24), fill=30)
            
            t_str = f"{t_min}°~{t_max}°"
            bbox = draw.textbbox((0, 0), t_str, font=get_font(26))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 805), t_str, font=get_font(26), fill=0)

    # --- 4. CARD 3: TODAY WEATHER (实时天气 - 移至底部) ---
    draw_rounded_card(draw, [60, 940, WIDTH - 60, 1380], radius=20, outline=160, fill=255, width=3)
    draw.text((95, 965), f"{CITY_NAME} · 实时天气 (Current Weather)", font=get_font(28), fill=40)
    draw.line([(95, 1005), (WIDTH - 95, 1005)], fill=230, width=1)
    
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
        
        # Left side: Big temp & condition
        draw.text((95, 1030), f"{temp}°", font=get_font(95), fill=0)
        draw.text((310, 1040), f"{w_desc}", font=get_font(38), fill=20)
        draw.text((310, 1095), f"今日温幅 {min_today}°C ~ {max_today}°C  |  体感 {feels_like}°C", font=get_font(25), fill=80)
        
        # Divider line
        draw.line([(95, 1165), (WIDTH - 95, 1165)], fill=220, width=2)
        
        # Grid details
        draw.text((100, 1195), "空气湿度", font=get_font(24), fill=110)
        draw.text((100, 1235), f"{humidity}%", font=get_font(32), fill=0)
        
        draw.text((340, 1195), "风速风力", font=get_font(24), fill=110)
        draw.text((340, 1235), f"{wind_speed} km/h", font=get_font(32), fill=0)
        
        draw.text((580, 1195), "紫外线指数", font=get_font(24), fill=110)
        uv_desc = "弱" if uv_today <= 2 else ("中等" if uv_today <= 5 else "较强")
        draw.text((580, 1235), f"{uv_today} ({uv_desc})", font=get_font(32), fill=0)
        
        draw.text((820, 1195), "今日温差", font=get_font(24), fill=110)
        draw.text((820, 1235), f"{max_today - min_today}°C", font=get_font(32), fill=0)

    # --- 5. FOOTER ---
    footer_text = "Kindle Voyage 桌面天气日历"
    bbox = draw.textbbox((0, 0), footer_text, font=get_font(22))
    draw.text((WIDTH // 2 - (bbox[2]-bbox[0])//2, 1405), footer_text, font=get_font(22), fill=130)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

if __name__ == "__main__":
    with open("dashboard.png", "wb") as f:
        f.write(generate_image_bytes())
    print("Swapped cards and generated dashboard.png successfully!")