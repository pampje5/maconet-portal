# app/services/mail/mail_sender.py

import os
import requests
from fastapi import HTTPException
from contextlib import ExitStack

MAIL_ENABLED = os.getenv("MAIL_ENABLED", "false").lower() == "true"


def send_mail(
    to: str,
    subject: str,
    body_html: str,
    attachment_path: str | None = None,
):
    """
    Generic mail sender.
    Respects MAIL_ENABLED flag.
    """

    if not MAIL_ENABLED:
        print(f"[MAIL] disabled → to={to}, subject={subject}")
        return {"status": "disabled"}

    provider = os.getenv("MAIL_PROVIDER")

    if provider == "mailgun":
        return send_via_mailgun(
            to=to,
            subject=subject,
            body_html=body_html,
            attachment_path=attachment_path,
        )

    raise HTTPException(500, "Mail provider not configured")


def send_via_mailgun(
    to: str,
    subject: str,
    body_html: str,
    attachment_path: str | None,
):
    api_key = os.getenv("MAILGUN_API_KEY")
    domain = os.getenv("MAILGUN_DOMAIN")

    if not api_key or not domain:
        raise HTTPException(500, "Mailgun not configured")

    from_name = os.getenv("MAIL_FROM_NAME", "Maconet")
    from_addr = os.getenv("MAIL_FROM_ADDRESS", f"noreply@{domain}")

    data = {
        "from": f"{from_name} <{from_addr}>",
        "to": to,
        "subject": subject,
        "html": body_html,
    }

    print(f"[MAIL] sending via Mailgun → to={to}, subject={subject}")

    with ExitStack() as stack:
        files = None

        if attachment_path:
            file_handle = stack.enter_context(open(attachment_path, "rb"))
            files = [("attachment", file_handle)]

        resp = requests.post(
            f"https://api.eu.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data=data,
            files=files,
            timeout=10,
        )

    if resp.status_code >= 300:
        print(f"[MAIL][ERROR] Mailgun response: {resp.status_code} {resp.text}")
        raise HTTPException(
            status_code=500,
            detail="Mail sending failed",
        )

    print(f"[MAIL] sent successfully → to={to}")
    return {"status": "sent"}
