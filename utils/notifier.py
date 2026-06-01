import smtplib
import os
from email.mime.text import MIMEText
from twilio.rest import Client


# =========================
# EMAIL FUNCTION
# =========================
def send_email(to_email, subject, message):

    sender_email = "minlatt.myo@gmail.com"
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_password:
        print("❌ EMAIL_APP_PASSWORD missing")
        return False

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        print(f"Connecting Gmail SMTP -> {to_email}")

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=15
        )

        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(
            sender_email,
            sender_password
        )

        server.sendmail(
            sender_email,
            to_email,
            msg.as_string()
        )

        server.quit()

        print(f"✅ EMAIL SUCCESS -> {to_email}")
        return True

    except Exception as e:
        print(f"❌ EMAIL ERROR -> {to_email}: {e}")
        return False


# =========================
# SMS FUNCTION
# =========================
def send_sms(phone, message):

    try:
        sid = os.getenv("TWILIO_SID")
        token = os.getenv("TWILIO_TOKEN")
        from_number = os.getenv("TWILIO_PHONE")

        if not sid or not token or not from_number:
            print("❌ Twilio env missing")
            return False

        phone = str(phone).strip()
        from_number = str(from_number).strip()

        if phone == from_number:
            print(f"⚠️ Skipping SMS same number -> {phone}")
            return False

        client = Client(sid, token)

        sms = client.messages.create(
            body=message,
            from_=from_number,
            to=phone
        )

        print(f"✅ SMS SID -> {sms.sid}")
        return True

    except Exception as e:
        print(f"❌ SMS ERROR -> {phone}: {e}")
        return False