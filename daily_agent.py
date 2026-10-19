import os
import sys
import smtplib
from datetime import datetime
from email.message import EmailMessage
from google import genai
from google.genai import errors as genai_errors
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

def reduce_number(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(digit) for digit in str(n))
    return n

def calculate_life_path(year, month, day):
    r_year = reduce_number(year)
    r_month = reduce_number(month)
    r_day = reduce_number(day)
    return reduce_number(r_year + r_month + r_day)

def calculate_universal_day(date_obj):
    year_sum = reduce_number(date_obj.year)
    month_sum = reduce_number(date_obj.month)
    day_sum = reduce_number(date_obj.day)
    return reduce_number(year_sum + month_sum + day_sum)

def calculate_personal_year(birth_month, birth_day, current_year):
    r_month = reduce_number(birth_month)
    r_day = reduce_number(birth_day)
    r_year = reduce_number(current_year)
    return reduce_number(r_month + r_day + r_year)

def calculate_personal_month(personal_year, current_month):
    r_month = reduce_number(current_month)
    return reduce_number(personal_year + r_month)

def calculate_personal_day(personal_month, current_day):
    r_day = reduce_number(current_day)
    return reduce_number(personal_month + r_day)

def get_numerology_report(birth_date_str="1980-03-15"):
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    today = datetime.now()
    
    lp = calculate_life_path(birth_date.year, birth_date.month, birth_date.day)
    ud = calculate_universal_day(today)
    py = calculate_personal_year(birth_date.month, birth_date.day, today.year)
    pm = calculate_personal_month(py, today.month)
    pd = calculate_personal_day(pm, today.day)
    
    return f"""
Daily Numerology Report ({today.strftime('%Y-%m-%d')}):
- Birth Date: {birth_date_str}
- Life Path Number: {lp}
- Universal Day Number: {ud}
- Personal Year Number: {py}
- Personal Month Number: {pm}
- Personal Day Number: {pd}
"""

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def generate_horoscope(api_key, user_name, zodiac_info):
    client = genai.Client(api_key=api_key)
    numerology_summary = get_numerology_report("1980-03-15")
    prompt = f"""
    You are an expert astrologer and numerologist creating a highly personalized daily reading for {user_name}.
    
    User Profile & Astrological Transits:
    {zodiac_info}
    
    {numerology_summary}
    
    Please structure the daily report with the following sections:
    1. Daily Astrological Transits & Horoscope
    2. Daily Numerology Insights (synthesizing the Life Path, Universal Day, Personal Year, Personal Month, and Personal Day)
    3. Actionable Advice for Today
    
    Keep the tone insightful, empowering, and practical.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def send_email(subject, body, to_email, from_email, app_password):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(body)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    user_name = os.environ.get("USER_NAME", "User")
    zodiac_info = os.environ.get("ZODIAC_INFO", "")
    to_email = os.environ.get("RECIPIENT_EMAIL")
    from_email = os.environ.get("SENDER_EMAIL")
    app_password = os.environ.get("EMAIL_APP_PASSWORD")
    
    if not all([api_key, to_email, from_email, app_password]):
        print("Missing required environment variables.")
        sys.exit(1)
        
    try:
        horoscope_text = generate_horoscope(api_key, user_name, zodiac_info)
        today_str = datetime.now().strftime("%Y-%m-%d")
        subject = f"Your Daily Horoscope & Numerology Reading - {today_str}"
        send_email(subject, horoscope_text, to_email, from_email, app_password)
        print("Horoscope email sent successfully.")
    except Exception as e:
        print(f"Failed to process or send horoscope: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
