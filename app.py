import datetime
from google import genai
import streamlit as st

st.set_page_config(page_title="Daily Reading Generator", page_icon="✨")

st.title("✨ Daily Insight Generator")
st.write(
    "Select your birth details below to see today's reading. No information is stored or saved."
)

col1, col2 = st.columns(2)
with col1:
    month = st.selectbox(
        "Birth Month",
        range(1, 13),
        format_func=lambda x: datetime.date(2000, x, 1).strftime("%B"),
    )
with col2:
    day = st.number_input("Birth Day", min_value=1, max_value=31, value=15)

zodiac_signs = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]
sign = st.selectbox("Sun Sign", zodiac_signs)

if st.button("Generate Today's Reading"):
  with st.spinner("Calculating transits..."):
    today = datetime.date.today()

    # Calculate Personal Day Energy
    universal_year = sum(int(d) for d in str(today.year))
    personal_day = (month + day + universal_year + today.month + today.day) % 9
    if personal_day == 0:
      personal_day = 9

    prompt = f"""
        Generate a daily horoscope and numerology reading for today, {today.strftime('%B %d, %Y')}.
        User Sun Sign: {sign}
        Personal Day Energy: {personal_day}
        
        Format clearly:
        1. Cosmic Outlook ({sign} energy today)
        2. Numerology Theme (Personal Day {personal_day})
        3. Today's Core Focus
        
        Keep it inspiring, concise, and grounded.
        """

    try:
      client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
      response = client.models.generate_content(
          model="gemini-2.5-flash", contents=prompt
      )
      st.markdown("---")
      st.markdown(response.text)
    except Exception as e:
      st.error("Please add your GEMINI_API_KEY to Streamlit Secrets.")
