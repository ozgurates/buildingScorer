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


def _build_ssl_context() -> ssl.SSLContext:
    """Build an SSL context that works behind corporate TLS-intercepting proxies.

    Resolution order:
      1. SSL_CERT_FILE env var (explicit CA bundle path).
      2. `truststore` package — uses the OS trust store (macOS Keychain,
         Windows cert store, Linux system CAs) so corporate root CAs are
         picked up automatically.
      3. `certifi` bundle (works on clean networks).
      4. Python default.
    """
    cert_file = os.getenv("SSL_CERT_FILE")
    if cert_file and os.path.exists(cert_file):
        return ssl.create_default_context(cafile=cert_file)
    try:
        import truststore  # type: ignore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except ImportError:
        pass
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def send_report(pdf_bytes: bytes, session_id: str, overall_score=None, rating=None, meaning=None, action=None) -> bool:
    global _last_error
    if not SENDER_EMAIL or not SENDER_APP_PASSWORD or not RECIPIENT_EMAIL:
        _last_error = (
            "Email config missing — SENDER_EMAIL, SENDER_APP_PASSWORD, or "
            "RECIPIENT_EMAIL is not set in .env / Streamlit secrets."
        )
        return False

    score_line = ""
    if overall_score is not None:
        score_line = f"\nOverall Score: {overall_score:.1f} / 100"
        if rating:
            score_line += f"\nRating: {rating}"
            score_line += f"\nMeaning: {meaning}"
            score_line += f"\nAction: {action}"
        score_line += "\n"
    else:
        score_line = "\nOverall Score: excluded (no valid category scores)\n"

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = f"Health-Promoting Spaces Assessment Report — {session_id}"
    msg.set_content(
        "Hello,\n\n"
        f"The Health-Promoting Spaces Assessment Report for session "
        f"{session_id} is attached.\n"
        f"{score_line}\n"
        "Regards"
    )
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=f"assessment_report_{session_id}.pdf",
    )

    try:
        ctx = _build_ssl_context()
        password = SENDER_APP_PASSWORD.replace(" ", "")
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as server:
            server.login(SENDER_EMAIL, password)
            server.send_message(msg)
        _last_error = None
        return True
    except Exception as exc:
        _last_error = f"{type(exc).__name__}: {exc}"
        return False
