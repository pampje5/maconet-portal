import os
import requests

from dotenv import load_dotenv

load_dotenv()

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAIL_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")


def send_email(
    to: str,
    subject: str,
    text: str = None,
    html: str = None,
):
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        raise RuntimeError("Mailgun is not configured")

    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"{MAIL_FROM_NAME} <{MAIL_FROM_EMAIL}>",
            "to": [to],
            "subject": subject,
            "text": text,
            "html": html,
        },
        timeout=10,
    )

    response.raise_for_status()
