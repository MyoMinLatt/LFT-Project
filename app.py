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
from auth.routes import auth_bp
from auth.security import login_required, role_required
from auth.models import init_user_table
from routes.api import api_bp


# ==============================
# ROUTES BLUEPRINTS
# ==============================
from routes import uf_bp, ro_bp

app = Flask(__name__)

import os
app.secret_key = os.getenv("SECRET_KEY", "dev_only_secret")


# ==============================
# REGISTER BLUEPRINTS
# ==============================
app.register_blueprint(uf_bp)
app.register_blueprint(ro_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

# ==============================
# MAIN PAGES
# ==============================
@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/monitoring')
@login_required
@role_required(["admin", "engineer", "user"])
def monitoring():
    return render_template('dashboard.html')

@app.route('/flow_diagram')
@login_required
@role_required(["admin", "engineer", "user"])
def flow_diagram():
    return render_template('flow_diag.html')

@app.route('/measurement')
@login_required
@role_required(["admin", "engineer", "user"])
def measurement():
    return render_template('measurements.html')

@app.route('/uf')
@login_required
@role_required(["admin", "engineer", "user"])
def uf():
    return render_template('uf_system.html')

@app.route('/ro')
@login_required
@role_required(["admin", "engineer", "user"])
def ro():
    return render_template('ro_system.html')

@app.route('/analysis')
@login_required
@role_required(["admin", "engineer", "user"])
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
    datetime_param = request.args.get("datetime")  # NEW

    from database.system_map_pumps import SYSTEM_MAP as PUMP_MAP

    # Check if the device is a pump
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
# SEND EMAIL TO ALL USERS
# ==============================

from auth.models import get_all_users
from utils.notifier import send_email, send_sms
import time

last_alert_time = 0

@app.route("/api/send-alert", methods=["POST"])
def send_alert():

    global last_alert_time

    # 🔥 cooldown protection
    now = time.time()
    if now - last_alert_time < 60:
        return jsonify({"status": "cooldown"})

    last_alert_time = now

    data = request.get_json() or {}

    message = f"""
⚠️ ALERT: Threshold Exceeded

🔴 Above Maximum ({data.get('high_count', 0)})
{data.get('high_list', '')}

🟡 Below Minimum ({data.get('low_count', 0)})
{data.get('low_list', '')}
"""

    users = get_all_users()

    for user in users:

        # ✅ only verified users
        if user["verified"] != 1:
            continue


        # 📧 EMAIL ALERT
        if user.get("email"):
            send_email(user["email"], "System Alert", message)

        # 📱 SMS ALERT
        if user.get("phone"):
            send_sms(user["phone"], message)


# ==============================
# RUN FLASK APP
# ==============================
import os
if __name__ == '__main__':
 #   init_user_table()
  #  app.run(debug=True)
    # For network access,
    #app.run(host="0.0.0.0", port=5000, debug=True)

 port = int(os.environ.get("PORT", 5000))
 app.run(host="0.0.0.0", port=port)
