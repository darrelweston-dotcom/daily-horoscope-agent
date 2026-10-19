import os
import sys
import smtplib
from datetime import datetime
from email.message import EmailMessage
import google.generativeai as genai

TARGET_EMAIL = "darrelweston.dotcom@gmail.com"
BIRTH_DATE = "1980-03-15"

def calculate_life_path(date_str):
    digits = [int(c) for c in date_str if c.isdigit()]
    total = sum(digits)
    while total > 9 and total not in (11, 22, 33):
        total = sum(int(c) for c in str(total))
    return total

def reduce_number(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(c) for c in str(n))
    return n

def calculate_numerology(birth_date_str, target_date):
    b_year, b_month, b_day = map(int, birth_date_str.split('-'))
    life_path = calculate_life_path(birth_date_str)
    
    t_year = target_date.year
    t_month = target_date.month
    t_day = target_date.day
    
    u_day = reduce_number(t_year + t_month + t_day)
    p_year = reduce_number(t_year + b_month + b_day)
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
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
    
    today = datetime.now()
    today_str = today.strftime("%B %d, %Y")
    
    num_data = calculate_numerology(BIRTH_DATE, today)
    
    prompt = f"""
Generate a daily astrological horoscope and numerology report for today ({today_str}).
The target person was born on March 15, 1980 (Pisces).

Numerology values for today:
- Life Path: {num_data['Life Path']}
- Universal Day: {num_data['Universal Day']}
- Personal Year: {num_data['Personal Year']}
- Personal Month: {num_data['Personal Month']}
- Personal Day: {num_data['Personal Day']}

Please structure the report clearly with:
1. Astrological Horoscope for Pisces for today ({today_str}).
2. Daily Numerology Report detailing each of the calculated numbers (Life Path, Universal Day, Personal Year, Personal Month, Personal Day) and their meanings/insights for today.
"""
    
    response = model.generate_content(prompt)
    return response.text

def send_email(subject, body):
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    
    if not gmail_user or not gmail_password:
        print("GMAIL_USER or GMAIL_APP_PASSWORD not set.")
        sys.exit(1)
        
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = TARGET_EMAIL
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
    print("Email sent successfully!")

def main():
    report = generate_report()
    today_str = datetime.now().strftime("%Y-%m-%d")
    subject = f"Daily Astrological & Numerology Report - {today_str}"
    send_email(subject, report)

if __name__ == "__main__":
    main()
