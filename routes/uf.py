from flask import Blueprint, render_template, jsonify, request
from database.uf_data import get_uf_device_data

uf_bp = Blueprint("uf", __name__)


# ==============================
# UF PAGE
# ==============================
@uf_bp.route("/uf")
def uf_page():
    return render_template("uf_system.html")


# ==============================
# UF API
# ==============================
@uf_bp.route("/api/uf-data")
def uf_data_api():

    parameter = request.args.get("parameter")
    device = request.args.get("device")
    interval = request.args.get("interval", "30min")

    # 🔥 ADD THESE TWO LINES
    start = request.args.get("start")
    end = request.args.get("end")

    if not parameter or not device:
        return jsonify({
            "timestamps": [],
            "values": [],
            "latest": 0,
            "mean": 0,
            "min": 0,
            "max": 0,
            "data_time": "-"
        })

    try:
        # 🔥 PASS start and end to backend function
        data = get_uf_device_data(parameter, device, interval, start, end)
        return jsonify(data)

    except Exception as e:
        print("UF API ERROR:", e)

        return jsonify({
            "timestamps": [],
            "values": [],
            "latest": 0,
            "mean": 0,
            "min": 0,
            "max": 0,
            "data_time": "-"
        })