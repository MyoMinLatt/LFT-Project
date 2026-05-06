import smtplib
import os
from email.mime.text import MIMEText

def send_otp(destination, otp):

    sender_email = "minlatt.myo@gmail.com"
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender_password:
        print("❌ EMAIL_APP_PASSWORD NOT FOUND")
        return

    msg = MIMEText(f"Your OTP code is: {otp}")
    msg["Subject"] = "OTP Verification"
    msg["From"] = sender_email
    msg["To"] = destination

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print(f"✅ OTP SENT to {destination}")

    except Exception as e:
        print("❌ OTP ERROR:", e)