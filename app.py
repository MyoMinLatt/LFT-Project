from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from flask import Flask, render_template, request, jsonify


# ==============================
# DATABASE FUNCTIONS
# ==============================
from database.system_map import get_dashboard_table
from database.system_map_pumps import get_pumps_table
from database.system_map_valves import get_valves_table
from database.device_popup import get_device_popup_data as get_device_data
from database.pump_popup import get_device_popup_data as get_pump_data

from database.user_utils import get_all_users

# ==============================
# ROUTES BLUEPRINTS
# ==============================
from routes import uf_bp, ro_bp

app = Flask(__name__)

import os
app.secret_key = os.environ.get("SECRET_KEY")


# ==============================
# REGISTER BLUEPRINTS
# ==============================
app.register_blueprint(uf_bp)
app.register_blueprint(ro_bp)


# ==============================
# MAIN PAGES (PUBLIC ACCESS)
# ==============================
@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/monitoring')
def monitoring():
    return render_template('dashboard.html')

@app.route('/flow_diagram')
def flow_diagram():
    return render_template('flow_diag.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/uf')
def uf():
    return render_template('uf_system.html')

@app.route('/ro')
def ro():
    return render_template('ro_system.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route("/health")
def health():
    return "OK", 200


# ==============================
# API ROUTES (Dashboard)
# ==============================
@app.route('/api/dashboard')
def api_dashboard():
    return jsonify(get_dashboard_table())

@app.route('/api/pumps')
def api_pumps():
    return jsonify(get_pumps_table())

@app.route('/api/valves')
def api_valves():
    return jsonify(get_valves_table())


# ==============================
# DEVICE POPUP (Dynamic)
# ==============================
@app.route("/device_popup")
def device_popup():
    device = request.args.get("device")
    date = request.args.get("date")
    datetime_param = request.args.get("datetime")

    from database.system_map_pumps import SYSTEM_MAP as PUMP_MAP

    is_pump = any(
        device in PUMP_MAP[category][system]
        for category in PUMP_MAP
        for system in PUMP_MAP[category]
    )

    if is_pump:
        from database.pump_popup import get_device_popup_data as get_pump_data
        data = get_pump_data(device, date, datetime_param)
    else:
        from database.device_popup import get_device_popup_data as get_device_data
        data = get_device_data(device, date, datetime_param)

    return jsonify(data)


# ==============================
# SEND EMAIL / SMS ALERTS
# ==============================
from utils.notifier import send_email, send_sms
import time

last_alert_time = 0

@app.route("/api/send-alert", methods=["POST"])
def send_alert():

    global last_alert_time

    now = time.time()

    if now - last_alert_time < 60:
        return jsonify({"status": "cooldown"})

    last_alert_time = now

    data = request.get_json() or {}

    print("===== ALERT API HIT =====")
    print(data)

    message = f"""
⚠️ ALERT: Threshold Exceeded

🔴 Above Maximum ({data.get('high_count',0)})
{data.get('high_list','')}

🟡 Below Minimum ({data.get('low_count',0)})
{data.get('low_list','')}
"""

    users = get_all_users()

    for user in users:

        # EMAIL
        if user.get("receive_email", 1) and user.get("email"):
            try:
                send_email(
                    user["email"],
                    "System Alert",
                    message
                )


            except Exception as e:
                print(f"❌ Email failed {user['email']}: {e}")

        # SMS
        if user.get("receive_sms", 1) and user.get("phone"):
            try:
                send_sms(
                    user["phone"],
                    message
                )
                print(f"✅ SMS sent to {user['phone']}")

            except Exception as e:
                print(f"❌ SMS failed {user['phone']}: {e}")

    print("===== ALERT COMPLETE =====")
    return jsonify({"status": "sent"})


# ===========================
# LOAD MANUAL HTML FILE
# ===========================
@app.route("/manuals/<name>")
def manuals(name):

    lang = request.args.get(
        "lang",
        "en"
    )

    folder_map = {

        "en": "manuals",
        "ko": "manuals/manual_ko",
        "my": "manuals/manual_my",
        "vi": "manuals/manual_vi",
        "mn": "manuals/manual_mn"

    }

    folder = folder_map.get(
        lang,
        "manuals"
    )

    return render_template(
        f"{folder}/{name}.html"
    )
# ==============================
# RUN FLASK APP
# ==============================

if __name__ == '__main__':
 #   init_user_table()
  #  app.run(debug=True)
    # For network access,
    app.run(host="0.0.0.0", port=5000, debug=True)

 #port = int(os.environ.get("PORT", 5000))
 #app.run(host="0.0.0.0", port=port)
