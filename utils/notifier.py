
# =========================
# EMAIL FUNCTION (GMAIL API)
# =========================

import os
from email.mime.text import MIMEText
from twilio.rest import Client
import smtplib
import socket


def send_email(to_email, subject, message):

    sender_email = "minlatt.myo@gmail.com"
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_password:
        print("❌ EMAIL_APP_PASSWORD not set")
        return False

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print(f"✅ EMAIL SUCCESS -> {to_email}")
        return True

    except (socket.gaierror, socket.timeout, OSError, Exception) as e:
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