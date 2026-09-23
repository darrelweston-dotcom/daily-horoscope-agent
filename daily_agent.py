import os
import sys
from google import genai
from google.genai import errors as genai_errors
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# The client automatically picks up the GEMINI_API_KEY environment variable.
client = genai.Client()

# Retry logic: Waits 4s, 8s, 16s, etc., up to 5 times if Google's servers are overloaded (503)
@retry(
    wait=wait_exponential(multiplier=2, min=4, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(genai_errors.ServerError)
)
def fetch_astrology_reading(prompt):
    # Using the Chat API instead of generate_content resolves the AFC warning from your logs
    chat = client.chats.create(model="gemini-3.6-flash")
    response = chat.send_message(prompt)
    return response.text

def generate_and_send():
    # 1. Pull personal information securely from GitHub Secrets/Environment Variables
    # This keeps your info private and allows public users to plug in their own data.
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
        
        # 3. Email Sending Logic
        # (Insert your SMTP or email API code here, making sure to use os.environ.get("RECIPIENT_EMAIL"))
        print("\n--- DAILY REPORT ---")
        print(reading)

    except Exception as e:
        print(f"Workflow failed after maximum retries: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_and_send()
