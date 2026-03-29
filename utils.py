import calendar
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from config import CALENDAR_IMAGE_PATH, BARTENDERS
from database import get_all_shifts, get_user_by_username, delete_all_shifts, add_shift

def generate_schedule():
    today = datetime.now()
    year = today.year
    month = today.month
    
    cal = calendar.monthcalendar(year, month)
    delete_all_shifts()
    
    index = 0
    
    for week in cal:
        for day in week:
            if day == 0:
                continue
            
            date = f"{day:02d}.{month:02d}"
            weekday = datetime(year, month, day).weekday()
            
            main = BARTENDERS[index % 2]
            second = BARTENDERS[(index + 1) % 2]
            
            if weekday in [6, 0, 1, 2]:
                add_shift(date, "15:00", main)
            elif weekday == 3:
                add_shift(date, "17:00", main)
            elif weekday in [4, 5]:
                add_shift(date, "17:00", main)
                add_shift(date, "20:00", second)
            
            index += 1
    
    print(f"✅ Расписание сгенерировано на {month:02d}.{year}")

def create_calendar_image(username=None):
    user_name = None
    if username:
        user = get_user_by_username(username)
        if user:
            user_name = user['name']
    
    img = Image.new("RGB", (1100, 1500), "white")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        header_font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
        header_font = font
    
    col_x = [40, 150, 250, 600]
    y = 140
    days_map = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    
    draw.text(
        (40, 50),
        f"📅 Расписание смен — {datetime.now().strftime('%B %Y')}",
        fill="black",
        font=header_font
    )
    
    shifts_data = get_all_shifts()
    schedule = {}
    
    for shift in shifts_
        date = shift['date']
        if date not in schedule:
            schedule[date] = []
        schedule[date].append(f"{shift['time']} {shift['bartender']}")
    
    for date in sorted(schedule.keys()):
        try:
            day, month = map(int, date.split("."))
            weekday = datetime(datetime.now().year, month, day).weekday()
        except:
            continue
        
        shifts = schedule.get(date, [])
        bg_color = "white"
        
        if weekday in [4, 5]:
            bg_color = "#e6f2ff"
        
        if user_name and any(user_name in s for s in shifts):
            bg_color = "#eaffea"
        
        draw.rectangle((30, y-5, 1050, y+35), fill=bg_color)
        
        row = [
            date,
            days_map[weekday] if weekday < len(days_map) else "",
            shifts[0] if len(shifts) > 0 else "-",
            shifts[1] if len(shifts) > 1 else "-"
        ]
        
        for i, cell in enumerate(row):
            draw.text((col_x[i], y), cell, fill="black", font=font)
        
        y += 45
    
    img.save(CALENDAR_IMAGE_PATH)
    return CALENDAR_IMAGE_PATH

