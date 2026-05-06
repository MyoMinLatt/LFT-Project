# auth/routes.py
from flask import Blueprint, request, render_template, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import time

from auth.models import (
    create_user,
    get_user_by_login,
    verify_user,
    update_login_fail,
    reset_fail
)

from auth.utils import generate_otp, otp_expiry, send_otp

auth_bp = Blueprint("auth", __name__)


# =========================
# REGISTER
# =========================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            data = request.form

            # ✅ PASSWORD CONFIRMATION CHECK (HERE)
            if data["password"] != data["confirm_password"]:
                return render_template("register.html", error="Passwords do not match")

            # agreement check
            if data.get("agree") != "yes":
                return render_template("register.html", error="You must agree to Terms")

            otp = generate_otp()
            expiry = otp_expiry()

            create_user(
                data,
                generate_password_hash(data["password"]),
                otp,
                expiry
            )

            send_otp(data["email"], otp)

            session["pending_user"] = data["email"]

            return redirect("/verify")

        except Exception as e:
            return render_template("register.html", error=str(e))

    return render_template("register.html")


# =========================
# VERIFY
# =========================
@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        try:
            code = request.form["code"]
            email = session.get("pending_user")

            user = get_user_by_login(email)

            if not user:
                return "User not found"

            # ✅ FIX: convert OTP expiry to float safely
            otp_expiry = float(user[12])

            if time.time() > otp_expiry:
                return "OTP expired"

            # OTP check
            if code == user[11]:
                verify_user(email)
                return redirect("/login")

            return "Wrong Code"

        except Exception as e:
            return str(e)

    return render_template("verify.html")


# =========================
# LOGIN
# =========================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            value = request.form["email"]
            password = request.form["password"]

            user = get_user_by_login(value)

            if not user:
                return render_template("login.html", error="User not found")

            # indexes (NEW TABLE STRUCTURE)
            # 0 id
            # 1 full_name
            # 2 last_name
            # 3 birthday
            # 4 email
            # 5 phone
            # 6 gender
            # 7 position
            # 8 affiliation
            # 9 password
            # 10 verified
            # 11 otp
            # 12 otp_expiry
            # 13 recovery
            # 14 agreed
            # 15 failed_attempts
            # 16 lock_until
            # 17 created_at
            # 18 password_changed_at
            # 19 role

            # lock check
            if time.time() < user[16]:
                return render_template("login.html", error="Account locked. Try later.")

            # password check
            if not check_password_hash(user[9], password):
                attempts = user[15] + 1

                if attempts >= 5:
                    update_login_fail(user[0], attempts, time.time() + 300)
                else:
                    update_login_fail(user[0], attempts)

                return render_template("login.html", error="Wrong password")

            # verified check
            if user[10] == 0:
                return render_template("login.html", error="Not verified")

            # success login
            # success login
            reset_fail(user["id"])

            session["user"] = user["email"]
            session["email"] = user["email"]
            session["last_name"] = user["last_name"]
            session["role"] = user["role"]

            return redirect("/monitoring")

        except Exception as e:
            return render_template("login.html", error=str(e))

    return render_template("login.html")


# =========================
# FORGOT PASSWORD (STEP 1)
# =========================
@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        try:
            value = request.form["email"]

            user = get_user_by_login(value)

            if not user:
                return render_template("forgot.html", error="User not found")

            otp = generate_otp()
            expiry = otp_expiry()

            from auth.models import set_reset_otp
            set_reset_otp(value, otp, expiry)

            send_otp(value, otp)

            session["reset_user"] = value

            return redirect("/reset_verify")

        except Exception as e:
            return render_template("forgot.html", error=str(e))

    return render_template("forgot.html")


# =========================
# RESET VERIFY (STEP 2)
# =========================
@auth_bp.route("/reset_verify", methods=["GET", "POST"])
def reset_verify():
    if request.method == "POST":
        code = request.form["code"]
        email = session.get("reset_user")

        user = get_user_by_login(email)

        if time.time() > user[11]:
            return "OTP expired"

        if code == user[10]:
            return redirect("/reset_password")

        return "Wrong code"

    return render_template("reset_verify.html")


# =========================
# RESET PASSWORD (STEP 3)
# =========================
@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        try:
            password = request.form["password"]
            email = session.get("reset_user")

            from auth.models import update_password

            update_password(email, generate_password_hash(password))

            return redirect("/login")

        except Exception as e:
            return str(e)

    return render_template("reset_password.html")


# =========================
# LOGOUT
# =========================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")