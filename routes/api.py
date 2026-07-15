from flask import make_response
from flask import Blueprint, jsonify, request
from database.system_map import get_dashboard_table
from database.system_map_pumps import get_pumps_table
from database.system_map_valves import get_valves_table
from database.uf_data import get_uf_device_data
from database.ro_data import get_ro_device_data
from database.device_popup import get_device_popup_data
from utils.notifier import send_email, send_sms
from database.user_utils import get_all_users

api_bp = Blueprint("api", __name__, url_prefix="/api")

# =========================
# Dashboard
# =========================
@api_bp.route("/dashboard")
def dashboard():
    data = get_dashboard_table()
    return jsonify(data)


# =========================
# Pumps
# =========================
@api_bp.route("/pumps")
def pumps():
    return jsonify(get_pumps_table())


# =========================
# Valves API
# ========================

@api_bp.route("/valves")
def valves():
    data = get_valves_table()
    return jsonify(data)


# =========================
# UF Data
# =========================
@api_bp.route("/uf-data")
def uf_data():
    return jsonify(get_uf_device_data(
        request.args.get("parameter"),
        request.args.get("device"),
        request.args.get("interval"),
        request.args.get("start"),
        request.args.get("end")
    ))

# =========================
# RO Data
# =========================
@api_bp.route("/ro-data")
def ro_data():
    return jsonify(get_ro_device_data(
        request.args.get("parameter"),
        request.args.get("device"),
        request.args.get("interval"),
        request.args.get("start"),
        request.args.get("end")
    ))

# =========================
# RO Valve (ONLY XV013)
# =========================
#@api_bp.route("/ro-valves")
#def ro_valves():
#    valves = get_valves_table()
#    filtered = [v for v in valves if v.get("uf_device") == "XV013"]
#    return jsonify(filtered)


# =========================
# Device Popup (Flow Diagram)
# =========================
@api_bp.route("/device-popup")
def device_popup():

    device = request.args.get("device")
    date = request.args.get("date")
    datetime_param = request.args.get("datetime")  # 🔥 ADD THIS

    return jsonify(get_device_popup_data(device, date, datetime_param))


# =========================
# Pump Popup (statistics like devices)
# =========================
@api_bp.route("/pump-popup")
def pump_popup():

    pump = request.args.get("pump")
    system = request.args.get("system")
    date = request.args.get("date")

    if not pump:
        return jsonify({"error": "pump parameter required"}), 400

    from database.pump_popup import get_device_popup_data

    datetime_param = request.args.get("datetime")

    data = get_device_popup_data(system, pump, date, datetime_param)

    return jsonify(data)


@api_bp.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

#======================================
# Alarm message
#======================================

from threading import Thread
import time

last_alert_time = 0


def send_alert_worker(users, msg):

    for user in users:

        email = str(user.get("email", "")).strip()
        phone = str(user.get("phone", "")).strip()

        # EMAIL
        if email:

            print(f"EMAIL -> {email}")

            try:
                email_ok = send_email(
                    email,
                    "System Alert",
                    msg
                )

                if email_ok:
                    print(f"✅ EMAIL OK -> {email}")
                else:
                    print(f"❌ EMAIL FAILED -> {email}")

            except Exception as e:
                print(f"❌ EMAIL ERROR -> {email}: {e}")

        # SMS
        if phone:

            print(f"SMS -> {phone}")

            try:
                sms_ok = send_sms(
                    phone,
                    msg
                )

                if sms_ok:
                    print(f"✅ SMS OK -> {phone}")
                else:
                    print(f"❌ SMS FAILED -> {phone}")

            except Exception as e:
                print(f"❌ SMS ERROR -> {phone}: {e}")


@api_bp.route("/send-alert", methods=["POST"])
def send_alert():

    global last_alert_time

    now = time.time()

    if now - last_alert_time < 60:
        return jsonify({"status": "cooldown"})

    last_alert_time = now

    data = request.get_json() or {}

    print("===== ALERT API HIT =====")
    print(data)

    msg = f"""
⚠️ ALERT: Threshold Exceeded

🔴 Above Maximum ({data.get('high_count',0)})
{data.get('high_list','')}

🟡 Below Minimum ({data.get('low_count',0)})
{data.get('low_list','')}
"""

    users = get_all_users()

    t = Thread(
        target=send_alert_worker,
        args=(users, msg)
    )

    t.daemon = True
    t.start()

    return jsonify({"status": "processing"})





