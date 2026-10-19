import os
import sys
import smtplib
from email.message import EmailMessage
from datetime import datetime
import google.generativeai as genai

BIRTH_DATE = "1980-03-15"

def reduce_number(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n

def calculate_life_path(birth_date_str):
    parts = birth_date_str.split('-')
    total = sum(reduce_number(int(p)) for p in parts)
    return reduce_number(total)

def calculate_numerology(birth_date_str, target_date):
    b_year, b_month, b_day = map(int, birth_date_str.split('-'))
    life_path = calculate_life_path(birth_date_str)

    t_year = target_date.year
    t_month = target_date.month
    t_day = target_date.day

    u_year = reduce_number(t_year)
    u_day = reduce_number(t_year + t_month + t_day)
    p_year = reduce_number(u_year + reduce_number(b_month) + reduce_number(b_day))
    p_month = reduce_number(p_year + t_month)
    p_day = reduce_number(p_month + t_day)

    return {
        "Life Path": life_path,
        "Universal Day": u_day,
        "Personal Year": p_year,
        "Personal Month": p_month,
        "Personal Day": p_day
    }

def generate_report():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable not set.")
        sys.exit(1)

    user_name = os.environ.get("USER_NAME", "Darrel")
    zodiac_info = os.environ.get("ZODIAC_INFO", "Pisces Sun, Leo Ascendant, Taurus Midheaven")

    genai.configure(api_key=api_key)

    today = datetime.now()
    today_str = today.strftime("%B %d, %Y")
    num_data = calculate_numerology(BIRTH_DATE, today)

    prompt = f"""
Generate a daily astrological horoscope and numerology report for {user_name} for today ({today_str}).
The target person was born on March 15, 1980 ({zodiac_info}).

Numerology values for today:
* Life Path: {num_data['Life Path']}
* Universal Day: {num_data['Universal Day']}
* Personal Year: {num_data['Personal Year']}
* Personal Month: {num_data['Personal Month']}
* Personal Day: {num_data['Personal Day']}

Please structure the report clearly with:
1. Astrological Horoscope & Transits for {zodiac_info} for today ({today_str}).
2. Daily Numerology Report detailing each of the calculated numbers (Life Path, Universal Day, Personal Year, Personal Month, Personal Day) and how they interact today.
3. Three practical, actionable focus points combining today's transits and numbers.
"""

    for model_name in ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-2.0-flash"]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Model {model_name} unavailable, trying next: {e}")

    sys.exit(1)

def send_email(subject, body):
    sender_email = os.environ.get("SENDER_EMAIL") or os.environ.get("GMAIL_USER") or os.environ.get("EMAIL_USER")
    app_password = os.environ.get("EMAIL_APP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD") or os.environ.get("EMAIL_PASS")
    recipient_email = os.environ.get("RECIPIENT_EMAIL") or os.environ.get("EMAIL_RECIPIENT") or sender_email

    if not sender_email or not app_password:
        print("Email credentials not set in environment variables.")
        sys.exit(1)

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)
    print("Email sent successfully!")

if __name__ == "__main__":
    today_str = datetime.now().strftime("%B %d, %Y")
    report = generate_report()
    send_email(f"Daily Astrology & Numerology Report ({today_str})", report)
