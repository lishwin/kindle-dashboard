# -*- coding: utf-8 -*-
import os
import io
import time
import datetime
import urllib.request
import json
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from PIL import Image, ImageDraw, ImageFont

app = FastAPI(title="Kindle Voyage Dashboard")

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

    # Convert to Beijing time (UTC+8)
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    beijing_now = utc_now + datetime.timedelta(hours=8)
    
    weather = fetch_weather()
    quote_text, quote_author = fetch_quote()

    # 1. Header
    time_str = beijing_now.strftime("%H:%M")
    date_str = f"{beijing_now.year}年{beijing_now.month}月{beijing_now.day}日 {WEEKDAYS_CN[beijing_now.weekday()]}"
    
    draw.text((60, 45), time_str, font=get_font(120), fill=0)
    draw.text((430, 75), date_str, font=get_font(36), fill=30)
    draw.text((430, 130), f"{CITY_NAME} · 实时云端看板", font=get_font(26), fill=90)
    draw.line([(60, 200), (WIDTH - 60, 200)], fill=200, width=2)

    # 2. Current Weather Card
    draw_rounded_card(draw, [60, 230, WIDTH - 60, 680], radius=20, outline=160, fill=255, width=3)
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
        
        draw.text((95, 270), f"{temp}°", font=get_font(110), fill=0)
        draw.text((340, 290), f"{w_desc}", font=get_font(42), fill=20)
        draw.text((340, 360), f"体感 {feels_like}°C  |  {min_today}° ~ {max_today}°C", font=get_font(28), fill=80)
        
        draw.line([(95, 460), (WIDTH - 95, 460)], fill=220, width=2)
        
        draw.text((100, 490), "空气湿度", font=get_font(24), fill=110)
        draw.text((100, 530), f"{humidity}%", font=get_font(32), fill=0)
        
        draw.text((340, 490), "风速风力", font=get_font(24), fill=110)
        draw.text((340, 530), f"{wind_speed} km/h", font=get_font(32), fill=0)
        
        draw.text((580, 490), "紫外线指数", font=get_font(24), fill=110)
        uv_desc = "弱" if uv_today <= 2 else ("中等" if uv_today <= 5 else "较强")
        draw.text((580, 530), f"{uv_today} ({uv_desc})", font=get_font(32), fill=0)
        
        draw.text((820, 490), "今日温差", font=get_font(24), fill=110)
        draw.text((820, 530), f"{max_today - min_today}°C", font=get_font(32), fill=0)

    # 3. 5-Day Forecast Card
    draw_rounded_card(draw, [60, 710, WIDTH - 60, 1080], radius=20, outline=160, fill=255, width=3)
    draw.text((95, 735), "未来天气预报 (5-Day Forecast)", font=get_font(28), fill=40)
    draw.line([(95, 785), (WIDTH - 95, 785)], fill=230, width=1)
    
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
            draw.text((x_center - (bbox[2]-bbox[0])//2, 810), day_name, font=get_font(26), fill=0)
            
            d_str = d_date.strftime("%m/%d")
            bbox = draw.textbbox((0, 0), d_str, font=get_font(22))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 850), d_str, font=get_font(22), fill=100)
            
            bbox = draw.textbbox((0, 0), desc, font=get_font(24))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 910), desc, font=get_font(24), fill=30)
            
            t_str = f"{t_min}°~{t_max}°"
            bbox = draw.textbbox((0, 0), t_str, font=get_font(26))
            draw.text((x_center - (bbox[2]-bbox[0])//2, 980), t_str, font=get_font(26), fill=0)

    # 4. Daily Quote Card
    draw_rounded_card(draw, [60, 1110, WIDTH - 60, 1370], radius=20, outline=160, fill=255, width=3)
    draw.text((95, 1130), "今日寄语 (Daily Inspiration)", font=get_font(28), fill=40)
    draw.line([(95, 1175), (WIDTH - 95, 1175)], fill=230, width=1)
    
    words = quote_text
    lines = []
    line = ""
    for char in words:
        if len(line) >= 25:
            lines.append(line)
            line = char
        else:
            line += char
    if line:
        lines.append(line)
        
    y_text = 1200
    for l in lines[:3]:
        draw.text((100, y_text), l, font=get_font(30), fill=20)
        y_text += 45
        
    if quote_author:
        author_str = f"—— {quote_author}"
        bbox = draw.textbbox((0, 0), author_str, font=get_font(24))
        draw.text((WIDTH - 100 - (bbox[2] - bbox[0]), 1315), author_str, font=get_font(24), fill=90)

    # 5. Footer
    footer_text = f"云端生成时间: {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}  |  Kindle Voyage Cloud Dashboard"
    bbox = draw.textbbox((0, 0), footer_text, font=get_font(22))
    draw.text((WIDTH // 2 - (bbox[2]-bbox[0])//2, 1400), footer_text, font=get_font(22), fill=130)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

@app.get("/dashboard.png")
@app.get("/screen.png")
def get_dashboard():
    img_bytes = generate_image_bytes()
    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@app.get("/", response_class=HTMLResponse)
def index():
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Kindle Voyage 云端看板</title>
    <style>
        body {{ background: #121212; color: #fff; font-family: sans-serif; text-align: center; padding: 20px; }}
        .card {{ display: inline-block; background: #1e1e1e; padding: 15px; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.7); }}
        img {{ border: 2px solid #ddd; border-radius: 8px; max-width: 480px; height: auto; display: block; }}
        .btn {{ display: inline-block; background: #0078d4; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; margin-top: 15px; font-weight: bold; }}
    </style>
</head>
<body>
    <h2>Kindle Voyage 云端看板服务 (24h 在线)</h2>
    <div class="card">
        <img src="/dashboard.png?t={int(time.time())}" alt="Dashboard Preview">
        <a class="btn" href="javascript:location.reload()">🔄 刷新预览</a>
    </div>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)