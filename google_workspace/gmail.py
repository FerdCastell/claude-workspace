import base64
import json
import os
import time
import threading
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .auth import get_service

SCHEDULED_FILE = os.path.join(os.path.dirname(__file__), "..", "scheduled_emails.json")


class Gmail:
    def __init__(self, user_id="me"):
        self.service = get_service("gmail", "v1")
        self.user_id = user_id

    def _build_raw(self, to, subject, body, cc=None, bcc=None, html=False):
        if html:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body, "html"))
        else:
            msg = MIMEText(body)
        msg["to"] = to if isinstance(to, str) else ", ".join(to)
        msg["subject"] = subject
        if cc:
            msg["cc"] = cc if isinstance(cc, str) else ", ".join(cc)
        if bcc:
            msg["bcc"] = bcc if isinstance(bcc, str) else ", ".join(bcc)
        return {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}

    def send(self, to, subject, body, cc=None, bcc=None, html=False):
        message = self._build_raw(to, subject, body, cc, bcc, html)
        return self.service.users().messages().send(userId=self.user_id, body=message).execute()

    def create_draft(self, to, subject, body, cc=None, bcc=None, html=False):
        message = self._build_raw(to, subject, body, cc, bcc, html)
        return self.service.users().drafts().create(userId=self.user_id, body={"message": message}).execute()

    def schedule(self, send_at, to, subject, body, cc=None, bcc=None, html=False):
        """
        Schedule an email to be sent at a specific datetime.
        send_at: datetime object (aware) or ISO string like "2026-03-01T10:00:00-05:00"
        Persists the schedule to scheduled_emails.json.
        Call start_scheduler() to process pending emails in the background.
        """
        if isinstance(send_at, datetime):
            send_at = send_at.isoformat()
        entry = {
            "send_at": send_at,
            "to": to,
            "subject": subject,
            "body": body,
            "cc": cc,
            "bcc": bcc,
            "html": html,
        }
        scheduled = self._load_scheduled()
        scheduled.append(entry)
        self._save_scheduled(scheduled)
        return entry

    def list_scheduled(self):
        return self._load_scheduled()

    def send_due(self):
        """Send all emails whose send_at time has passed. Returns list of sent entries."""
        now = datetime.now(timezone.utc)
        scheduled = self._load_scheduled()
        pending = []
        sent = []
        for entry in scheduled:
            send_at = datetime.fromisoformat(entry["send_at"])
            if send_at.tzinfo is None:
                send_at = send_at.replace(tzinfo=timezone.utc)
            if send_at <= now:
                self.send(
                    entry["to"],
                    entry["subject"],
                    entry["body"],
                    entry.get("cc"),
                    entry.get("bcc"),
                    entry.get("html", False),
                )
                sent.append(entry)
            else:
                pending.append(entry)
        self._save_scheduled(pending)
        return sent

    def start_scheduler(self, check_interval=60):
        """
        Start a background thread that checks and sends due emails every check_interval seconds.
        Returns the thread object.
        """
        def loop():
            while True:
                try:
                    self.send_due()
                except Exception as e:
                    print(f"[gmail scheduler] error: {e}")
                time.sleep(check_interval)

        t = threading.Thread(target=loop, daemon=True)
        t.start()
        return t

    def list_messages(self, query="", max_results=10):
        result = self.service.users().messages().list(
            userId=self.user_id, q=query, maxResults=max_results
        ).execute()
        return result.get("messages", [])

    def _load_scheduled(self):
        if not os.path.exists(SCHEDULED_FILE):
            return []
        with open(SCHEDULED_FILE) as f:
            return json.load(f)

    def _save_scheduled(self, data):
        with open(SCHEDULED_FILE, "w") as f:
            json.dump(data, f, indent=2)
