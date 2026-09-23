import os
import sys
import smtplib
from email.message import EmailMessage
from google import genai
from google.genai import errors as genai_errors
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Initialize Gemini client (automatically uses GEMINI_API_KEY from environment)
client = genai.Client()

# Retry logic: Waits 4s, 8s, 16s, etc., up to 5 times for 503 Server Errors
@retry(
    wait=wait_exponential(multiplier=2, min=4, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(genai_errors.ServerError)
)
def fetch_astrology_reading(prompt):
    chat = client.chats.create(model="gemini-3.6-flash")
    response = chat.send_message(prompt)
    return response.text

def generate_and_send():
    # 1. Retrieve Personal Information
    user_name = os.environ.get("USER_NAME", "Seeker")
    zodiac_info = os.environ.get("ZODIAC_INFO", "general astrological transits")
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set. Please configure GitHub Secrets.")
        sys.exit(1)

    # 2. Construct the personalized prompt
    prompt = (
        f"Generate a daily astrological transit report for {user_name}. "
        f"Their specific chart details are: {zodiac_info}. "
        "Focus on the major planetary transits today and how they affect these specific placements. "
        "Format the output clearly as an email draft."
    )

    print(f"Fetching reading for {user_name}...")
    try:
        reading = fetch_astrology_reading(prompt)
        print("Reading successfully generated.")
    except Exception as e:
        print(f"Workflow failed to generate reading after maximum retries: {e}")
        sys.exit(1)

    # 3. Email Sending Logic
    sender_email = os.environ.get("SENDER_EMAIL")
    email_password = os.environ.get("EMAIL_APP_PASSWORD")
    recipient_email = os.environ.get("RECIPIENT_EMAIL")

    if sender_email and email_password and recipient_email:
        print("Preparing to send email...")
        msg = EmailMessage()
        msg.set_content(reading)
        msg['Subject'] = f"Daily Astrological Transit Report for {user_name}"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        try:
            # Connects securely to Gmail's SMTP server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, email_password)
                server.send_message(msg)
            print("Email successfully delivered!")
        except Exception as e:
            print(f"Failed to send email: {e}")
    else:
        print("Email credentials missing from secrets. Printed to console instead:\n")
        print("--- DAILY REPORT ---")
        print(reading)

if __name__ == "__main__":
    generate_and_send()
