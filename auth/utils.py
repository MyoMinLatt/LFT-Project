# auth/utils.py
import random
import time


def generate_otp():
    return str(random.randint(100000, 999999))


def otp_expiry(minutes=5):
    return time.time() + (minutes * 60)


def send_otp(destination, otp):
    # Replace later with Email/SMS/Kakao API
    print(f"[OTP SENT] To {destination}: {otp}")