import smtplib
import os
from email.mime.text import MIMEText

# =========================
# EMAIL FUNCTION
# =========================
def send_email(to_email, subject, message):
    sender_email = os.getenv(
        "EMAIL_USER",
        "minlatt.myo@gmail.com"
    )
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    # ✅ SAFETY CHECK
    if not sender_password:
        print("❌ EMAIL_APP_PASSWORD not set")
        return

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print(f"✅ Email sent to {to_email}")

    except Exception as e:
        print("❌ Email error:", e)


# =========================
# SMS FUNCTION (Twilio)
# =========================
from twilio.rest import Client

def send_sms(phone, message):
    try:
        sid = os.getenv("TWILIO_SID")
        token = os.getenv("TWILIO_TOKEN")
        from_number = os.getenv("TWILIO_PHONE")

        # ✅ SAFETY CHECK
        if not sid or not token or not from_number:
            print("⚠️ Twilio not configured — skipping SMS")
            return

        client = Client(sid, token)

        message_obj = client.messages.create(
            body=message,
            from_=from_number,
            to=phone
        )

        print(f"📱 SMS sent to {phone} (SID: {message_obj.sid})")

    except Exception as e:
        print("❌ SMS error:", e)