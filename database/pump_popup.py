import sqlite3
from datetime import datetime, timedelta
from config import LFT_DB
from database.system_map_pumps import SYSTEM_MAP


def find_device(device):
    for cat in SYSTEM_MAP:
        for sys in SYSTEM_MAP[cat]:
            if device in SYSTEM_MAP[cat][sys]:
                return SYSTEM_MAP[cat][sys][device]
    return None, None


def parse_time(ts):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(ts, fmt)
        except:
            pass
    return None


# ✅ SAME AS DEVICE
def calculate_summary(values, latest_time):

    day_vals = [v for t, v in values if t.date() == latest_time.date()]

    max_val = max(day_vals) if day_vals else "-"
    min_val = min(day_vals) if day_vals else "-"
    avg_day_val = round(sum(day_vals) / len(day_vals), 9) if day_vals else "-"

    interval_vals = [v for t, v in values if t <= latest_time]

    latest_val = interval_vals[-1] if interval_vals else "-"
    recent_val = interval_vals[-2] if len(interval_vals) >= 2 else latest_val

    def avg_minutes(minutes):
        start = latest_time - timedelta(minutes=minutes)
        vals = [v for t, v in values if start <= t <= latest_time]
        return round(sum(vals) / len(vals), 9) if vals else "-"

    def safe_round(val):
        return round(val, 9) if isinstance(val, (int, float)) else "-"

    return {
        "latest": safe_round(latest_val),
        "recent": safe_round(recent_val),
        "avg30m": avg_minutes(30),
        "avg1hr": avg_minutes(60),
        "avg1d": avg_day_val,
        "max": safe_round(max_val),
        "min": safe_round(min_val)
    }


def empty_summary():
    return {
        "latest": "-","recent": "-","avg30m": "-",
        "avg1hr": "-","avg1d": "-","max": "-","min": "-"
    }


def get_device_popup_data(device, date=None, datetime_param=None):

    table, column = find_device(device)
    if not table:
        return {"today": empty_summary(), "selected": None, "custom": None}

    conn = sqlite3.connect(LFT_DB)
    cur = conn.cursor()
    cur.execute(f'SELECT Time, "{column}" FROM "{table}"')
    rows = cur.fetchall()
    conn.close()

    dt_vals = []
    for ts, v in rows:
        t = parse_time(ts)
        try:
            val = float(v)
        except:
            continue
        if t:
            dt_vals.append((t, val))

    if not dt_vals:
        return {"today": empty_summary(), "selected": None, "custom": None}

    dt_vals.sort()

    latest_time = dt_vals[-1][0]

    # -------- TODAY --------
    today_vals = [(t, v) for t, v in dt_vals if t.date() == latest_time.date()]
    today_data = calculate_summary(today_vals, latest_time)

    # -------- SELECTED (FIXED LOGIC 1) --------
    selected_data = None

    if date:
        dt = datetime.strptime(date, "%Y-%m-%d")
        sel_vals = [(t, v) for t, v in dt_vals if t.date() == dt.date()]

        if sel_vals:
            target_time = latest_time.replace(
                year=dt.year,
                month=dt.month,
                day=dt.day
            )

            closest_record = min(sel_vals, key=lambda x: abs(x[0] - target_time))
            closest_time = closest_record[0]

            MAX_DIFF = timedelta(minutes=10)

            if abs(closest_time - target_time) > MAX_DIFF:
                # fallback
                vals = [v for t, v in sel_vals]
                selected_data = {
                    "latest": "-",
                    "recent": "-",
                    "avg30m": "-",
                    "avg1hr": "-",
                    "avg1d": round(sum(vals)/len(vals), 9),
                    "max": round(max(vals), 9),
                    "min": round(min(vals), 9)
                }
            else:
                selected_data = calculate_summary(sel_vals, closest_time)

        else:
            selected_data = empty_summary()

    # -------- CUSTOM (UNCHANGED) --------
    custom = None
    if datetime_param:
        try:
            dt_sel = datetime.strptime(datetime_param, "%Y-%m-%d %H:%M")
            day_vals = [(t, v) for t, v in dt_vals if t.date() == dt_sel.date()]

            if day_vals:
                exact = [v for t, v in day_vals if t.hour == dt_sel.hour and t.minute == dt_sel.minute]
                vals = [v for t, v in day_vals]

                custom = {
                    "date": dt_sel.strftime("%Y/%m/%d"),
                    "time": dt_sel.strftime("%H:%M"),
                    "value": exact[0] if exact else None,
                    "avg": round(sum(vals)/len(vals), 9),
                    "max": round(max(vals), 9),
                    "min": round(min(vals), 9)
                }
        except:
            custom = None

    return {
        "today": today_data,
        "selected": selected_data,
        "custom": custom
    }