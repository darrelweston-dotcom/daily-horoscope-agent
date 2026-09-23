# Daily Astrological Agent

This is an automated Python script that runs on GitHub Actions to generate and email a highly personalized daily astrological transit report using the Google Gemini API.

## How to Use This Template
You do not need to know how to code to use this! Just follow these steps:

1. Click the green **Use this template** button at the top of this page to create your own copy of this repository.
2. In your new repository, go to **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add the following required secrets:
   * `GEMINI_API_KEY`: Your Google Gemini API key.
   * `USER_NAME`: Your name.
   * `ZODIAC_INFO`: Your astrological natal chart details (e.g., Sun, Moon, Ascendant, or full planetary placements). You can generate your free natal chart [here](https://cafeastrology.com/free-natal-chart-report.html).
   * `SENDER_EMAIL`: The Gmail address sending the report.
   * `EMAIL_APP_PASSWORD`: A 16-character Google App Password for the sender email.
   * `RECIPIENT_EMAIL`: The email address where you want to receive the report.
4. Go to the **Actions** tab, select the **Daily Astrological Agent** workflow on the left, and click **Run workflow** to test it!

After your first successful test, the script will automatically run itself every single day.
