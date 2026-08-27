import datetime
import math
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ephem
from google import genai

# Baseline Profile Context
BIRTH_MONTH = 3
BIRTH_DAY = 15
BIRTH_YEAR = 1980

NATAL_PROFILE = """
USER PROFILE:
* Name: Darrel Keith Weston
* Date of Birth: March 15, 1980
* Sun Sign: Pisces

NUMEROLOGY BASELINE:
* Life Path Number: 9
* Destiny (Expression) Number: 9
* Soul Urge Number: 22/4
* Personality Number: 5
* Birthday Number: 6
"""

# Configuration (Uses environment variables for security)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_gmail@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your_16_char_app_password")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "your_gmail@gmail.com")

def reduce_number(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(digit) for digit in str(n))
    return n

def calculate_numerology_transits(today):
    universal_year = sum(int(d) for d in str(today.year))
    personal_year = reduce_number(BIRTH_MONTH + BIRTH_DAY + universal_year)
    personal_month = reduce_number(personal_year + today.month)
    personal_day = reduce_number(personal_month + today.day)
    return personal_year, personal_month, personal_day

def get_zodiac_sign(lon_rad):
    degrees = math.degrees(float(lon_rad)) % 360
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return signs[int(degrees // 30)]

def calculate_astrological_transits(today):
    date_str = today.strftime("%Y/%m/%d 12:00:00")
    bodies = {
        "Sun": ephem.Sun(date_str), "Moon": ephem.Moon(date_str),
        "Mercury": ephem.Mercury(date_str), "Venus": ephem.Venus(date_str),
        "Mars": ephem.Mars(date_str), "Jupiter": ephem.Jupiter(date_str),
        "Saturn": ephem.Saturn(date_str)
    }
    return {name: get_zodiac_sign(ephem.Ecliptic(body).lon) for name, body in bodies.items()}

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def generate_and_send():
    today = datetime.date.today()
    py, pm, pd = calculate_numerology_transits(today)
    transits = calculate_astrological_transits(today)
    transit_summary = ", ".join([f"{planet} in {sign}" for planet, sign in transits.items()])

    prompt = f"""
{NATAL_PROFILE}

DYNAMIC TRANSITS FOR TODAY ({today.strftime('%B %d, %Y')}):
* Current Planetary Positions: {transit_summary}
* Personal Year: {py}
* Personal Month: {pm}
* Personal Day: {pd}

INSTRUCTIONS:
Generate a personalized daily report.
1. Daily Horoscope: Interpret today's transits relative to a Pisces Sun.
2. Daily Numerology: Interpret the energy of Personal Day {pd}.
3. Daily Focus: Provide one clear action item.

Keep response focused, clear, and grounded.
"""

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    subject = f"Your Daily Astrological & Numerology Report - {today.strftime('%b %d, %Y')}"
    send_email(subject, response.text)
    print("Report emailed successfully!")

if __name__ == "__main__":
    generate_and_send()
