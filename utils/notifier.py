import os
import base64
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build


# =========================
# EMAIL FUNCTION (GMAIL API)
# =========================
def send_email(to_email, subject, message):

    sender_email = "minlatt.myo@gmail.com"

    try:

        credentials = service_account.Credentials.from_service_account_file(
            "gmail_service_account.json",
            scopes=[
                "https://www.googleapis.com/auth/gmail.send"
            ]
        )

        delegated = credentials.with_subject(
            sender_email
        )

        service = build(
            "gmail",
            "v1",
            credentials=delegated
        )

        msg = MIMEText(
            message,
            "plain",
            "utf-8"
        )

        msg["to"] = to_email
        msg["from"] = sender_email
        msg["subject"] = subject

        raw = base64.urlsafe_b64encode(
            msg.as_bytes()
        ).decode()

        body = {
            "raw": raw
        }

        service.users().messages().send(
            userId="me",
            body=body
        ).execute()

        print(f"✅ EMAIL SUCCESS -> {to_email}")
        return True

    except Exception as e:
        print(f"❌ EMAIL ERROR -> {to_email}: {e}")
        return False


# =========================
# SMS FUNCTION
# =========================
def send_sms(phone, message):

    sid = os.getenv("TWILIO_SID")
    token = os.getenv("TWILIO_TOKEN")
    from_number = os.getenv("TWILIO_PHONE")

    if not sid or not token or not from_number:
        print("⚠️ Twilio not configured")
        return False

    # prevent same To and From
    if phone == from_number:
        print(f"⚠️ Skipping SMS: same number {phone}")
        return False

    try:
        client = Client(
            sid,
            token,
            timeout=15   # 🔥 ADD
        )

        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=phone
        )

        print(f"✅ SMS sent to {phone}")
        return True

    except Exception as e:
        print("❌ SMS error:", e)
        return False