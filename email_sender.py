"""SMTP email delivery for the assessment PDF report.

Uses Gmail with an app password. Reads SENDER_EMAIL, SENDER_APP_PASSWORD
and RECIPIENT_EMAIL from environment / .env file. Generate an app
password at: Google Account → Security → 2-Step Verification → App
Passwords → "Mail".
"""

import os
import smtplib
import ssl
from email.message import EmailMessage

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

_last_error: str | None = None


def last_error() -> str | None:
    return _last_error


def send_report(pdf_bytes: bytes, session_id: str) -> bool:
    global _last_error
    if not SENDER_EMAIL or not SENDER_APP_PASSWORD or not RECIPIENT_EMAIL:
        _last_error = (
            "Email config missing — SENDER_EMAIL, SENDER_APP_PASSWORD, or "
            "RECIPIENT_EMAIL is not set in .env / Streamlit secrets."
        )
        return False
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = f"Health-Promoting Spaces Assessment Report — {session_id}"
    msg.set_content(
        "Hello,\n\n"
        f"The Health-Promoting Spaces Assessment Report for session "
        f"{session_id} is attached.\n\n"
        "Regards"
    )
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=f"assessment_report_{session_id}.pdf",
    )

    try:
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            ctx = ssl.create_default_context()
        password = SENDER_APP_PASSWORD.replace(" ", "")
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as server:
            server.login(SENDER_EMAIL, password)
            server.send_message(msg)
        _last_error = None
        return True
    except Exception as exc:
        _last_error = f"{type(exc).__name__}: {exc}"
        return False
