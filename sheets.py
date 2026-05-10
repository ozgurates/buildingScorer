"""Google Sheets persistence layer for the survey app.

Provides session ID generation, progressive saving, and session resume.
All save operations run in a background thread so the UI never blocks.
Failures are swallowed silently — the survey must keep working even if
Sheets is unreachable.

Schema: project_name is its own column; all question answers are stored
as JSON in a single `answers` column. Final headers:
    session_id, timestamp, last_page, status, project_name, answers
"""

import json
import os
import secrets
import string
import threading
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "survey_responses")
WORKSHEET_NAME = "responses"

HEADERS = ["session_id", "timestamp", "last_page", "status", "project_name", "answers"]

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

ANSWER_KEY_PREFIXES = ("A_", "B_", "C_", "D_", "E_")

_last_error: str | None = None


def last_error() -> str | None:
    return _last_error


def _set_error(exc: BaseException | None) -> None:
    global _last_error
    if exc is None:
        _last_error = None
    else:
        _last_error = f"{type(exc).__name__}: {exc}"


def generate_session_id() -> str:
    """Return an 8-character session code in the form ABC-1234."""
    left = "".join(secrets.choice(string.ascii_uppercase) for _ in range(3))
    right = "".join(secrets.choice(string.digits) for _ in range(4))
    return f"{left}-{right}"


def collect_answers(session_state) -> dict:
    """Pull all answer-shaped keys out of st.session_state into a plain dict."""
    out = {}
    for k, v in session_state.items():
        if k.startswith(ANSWER_KEY_PREFIXES) or k == "project_name":
            out[k] = v
    return out


def _build_credentials():
    """Load service-account credentials.

    Resolution order:
      1. GOOGLE_CREDENTIALS_JSON env var (full JSON as a string)
      2. Streamlit secrets section [gcp_service_account]
      3. Local credentials file at GOOGLE_CREDENTIALS_PATH
    """
    from google.oauth2.service_account import Credentials

    inline = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if inline:
        info = json.loads(inline)
        return Credentials.from_service_account_info(info, scopes=_SCOPES)

    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
            return Credentials.from_service_account_info(info, scopes=_SCOPES)
    except Exception:
        pass

    return Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_PATH, scopes=_SCOPES
    )


def _open_worksheet():
    """Open the worksheet, creating it (and headers) if needed."""
    import gspread

    creds = _build_credentials()
    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)

    try:
        ws = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME, rows=1000, cols=max(26, len(HEADERS))
        )
        ws.update("A1", [HEADERS])
        return ws

    if ws.col_count < len(HEADERS):
        ws.add_cols(len(HEADERS) - ws.col_count)
    first_row = ws.row_values(1)
    if first_row != HEADERS:
        ws.update("A1", [HEADERS])
    return ws


def _save_blocking(session_id: str, last_page: str, answers: dict, status: str) -> bool:
    try:
        ws = _open_worksheet()
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        project_name = answers.get("project_name", "") or ""
        question_answers = {k: v for k, v in answers.items() if k != "project_name"}
        answers_json = json.dumps(question_answers, default=str)
        row = [session_id, timestamp, last_page, status, project_name, answers_json]

        ids = ws.col_values(1)
        if session_id in ids:
            row_idx = ids.index(session_id) + 1
            ws.update(f"A{row_idx}", [row])
        else:
            ws.append_row(row)
        _set_error(None)
        return True
    except Exception as exc:
        _set_error(exc)
        return False


def save_session_async(
    session_id: str,
    last_page: str,
    answers: dict,
    status: str = "in_progress",
) -> None:
    """Fire-and-forget save. Does nothing if session_id is empty."""
    if not session_id:
        return
    thread = threading.Thread(
        target=_save_blocking,
        args=(session_id, last_page, dict(answers), status),
        daemon=True,
    )
    thread.start()


def test_connection() -> tuple[bool, str | None]:
    """Synchronously try to open the worksheet. Returns (ok, error_string)."""
    try:
        _open_worksheet()
        _set_error(None)
        return True, None
    except Exception as exc:
        _set_error(exc)
        return False, f"{type(exc).__name__}: {exc}"


def load_session(session_id: str):
    """Return {answers, last_page, status} for the given code, or None."""
    if not session_id:
        return None
    try:
        ws = _open_worksheet()
        records = ws.get_all_records()
    except Exception as exc:
        _set_error(exc)
        return None

    for row in records:
        if str(row.get("session_id", "")).strip() == session_id:
            raw = row.get("answers") or "{}"
            try:
                answers = json.loads(raw) if isinstance(raw, str) else dict(raw)
            except (ValueError, TypeError):
                answers = {}
            project_name = row.get("project_name")
            if project_name:
                answers["project_name"] = project_name
            return {
                "answers": answers,
                "last_page": row.get("last_page") or "",
                "status": row.get("status") or "in_progress",
            }
    return None


def mark_completed(session_id: str, last_page: str, answers: dict) -> None:
    """Mark a session as completed (async)."""
    save_session_async(session_id, last_page, answers, status="completed")
