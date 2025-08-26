"""
Campaign Delivery Script (Email/SMS/Postcard)

- Example: Sends campaign content via SendGrid (email), Twilio (SMS), and Lob (postcard)
- Loads campaign content from campaign_llm_content.json
- Stubbed API calls for demo
"""
import os
import json
#from sendgrid import SendGridAPIClient
#from twilio.rest import Client
#import lob

CAMPAIGN_PATH = os.path.join(os.path.dirname(__file__), "campaign_llm_content.json")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "demo-key")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "demo-sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "demo-token")
LOB_API_KEY = os.getenv("LOB_API_KEY", "demo-key")


def send_email(to: str, subject: str, body: str):
    print(f"Sending email to {to}: {subject}\n{body}")
    # sg = SendGridAPIClient(SENDGRID_API_KEY)
    # response = sg.send(...)


def send_sms(to: str, body: str):
    print(f"Sending SMS to {to}: {body}")
    # client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    # message = client.messages.create(...)


def send_postcard(to: str, body: str):
    print(f"Sending postcard to {to}: {body}")
    # lob.Client(LOB_API_KEY).postcards.create(...)


def main():
    if not os.path.exists(CAMPAIGN_PATH):
        print("No campaign content found.")
        return
    with open(CAMPAIGN_PATH, "r", encoding="utf-8") as f:
        campaigns = json.load(f)
    for persona in campaigns:
        # Stub: Replace with actual recipient info
        recipient = persona.get("email", "demo@example.com")
        content = persona.get("campaign_content", {})
        if "email" in content:
            send_email(recipient, "Your Travel Offer", content["email"])
        if "social" in content:
            print(f"Social campaign: {content['social']}")
        if "postcard" in content:
            send_postcard(recipient, content["postcard"])
        # Optionally send SMS
        # send_sms(recipient, content.get("sms", ""))
    print("Campaign delivery complete.")

if __name__ == "__main__":
    main()
