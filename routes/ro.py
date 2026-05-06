from flask import Blueprint, render_template, jsonify, request
from database.ro_data import get_ro_device_data

ro_bp = Blueprint("ro", __name__)

@ro_bp.route("/ro")
def ro_page():
    return render_template("ro_system.html")


@ro_bp.route("/api/ro-data")
def ro_data_api():

    parameter = request.args.get("parameter")
    device = request.args.get("device")
    interval = request.args.get("interval")
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

    data = get_ro_device_data(parameter, device, interval, start, end)
    return jsonify(data)


@ro_bp.route("/api/ro-valves")
def ro_valves():

    from database.system_map_valves import get_valves_table
    data = get_valves_table()

    # Only XV013
    filtered = [v for v in data if v.get("ro_device") == "XV013"]

    return jsonify(filtered)