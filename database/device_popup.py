import sqlite3
from datetime import datetime, timedelta
from config import LFT_DB
from database.system_map import get_table_column

DB_PATH = LFT_DB

def parse_time(t):
    formats = [
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %H:%M:%S"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(t, fmt)
        except:
            pass
    return None


def fetch_values(device):
    table, column = get_table_column(device)
    if table is None:
        return []

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f'SELECT Time, "{column}" FROM "{table}"')
    rows = cur.fetchall()
    conn.close()

    values = []
    for t, v in rows:
        if v is None:
            continue
        dt = parse_time(t)
        if dt is None:
            continue
        try:
            values.append((dt, float(v)))
        except:
            continue

    values.sort(key=lambda x: x[0])
    return values


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
        "latest": "-",
        "recent": "-",
        "avg30m": "-",
        "avg1hr": "-",
        "avg1d": "-",
        "max": "-",
        "min": "-"
    }


def get_device_popup_data(device, date=None, datetime_param=None):

    all_values = fetch_values(device)

    if not all_values:
        return {"today": empty_summary(), "selected": None, "custom": None}

    latest_time = all_values[-1][0]

    # -------- TODAY --------
    today_vals = [(t, v) for t, v in all_values if t.date() == latest_time.date()]
    today_summary = calculate_summary(today_vals, latest_time)

    # -------- SELECTED --------
    selected_summary = None
    if date:
        dt = datetime.strptime(date, "%Y-%m-%d")
        sel_vals = [(t, v) for t, v in all_values if t.date() == dt.date()]

        if sel_vals:
            # Target time (same clock time as Today)
            target_time = latest_time.replace(
                year=dt.year,
                month=dt.month,
                day=dt.day
            )

            # Find closest timestamp
            closest_record = min(sel_vals, key=lambda x: abs(x[0] - target_time))
            closest_time = closest_record[0]

            # Threshold check (IMPORTANT)
            MAX_DIFF = timedelta(minutes=10)

            if abs(closest_time - target_time) > MAX_DIFF:
                # ❌ Too far → fallback (ONLY daily stats)
                vals = [v for t, v in sel_vals]
                selected_summary = {
                    "latest": "-",
                    "recent": "-",
                    "avg30m": "-",
                    "avg1hr": "-",
                    "avg1d": round(sum(vals) / len(vals), 9),
                    "max": round(max(vals), 9),
                    "min": round(min(vals), 9)
                }
            else:
                # ✅ Good match → full logic
                selected_summary = calculate_summary(sel_vals, closest_time)

        else:
            # No data at all
            selected_summary = empty_summary()

    # -------- CUSTOM (2nd LOGIC) --------
    custom = None
    if datetime_param:
        try:
            dt_sel = datetime.strptime(datetime_param, "%Y-%m-%d %H:%M")
            day_vals = [(t, v) for t, v in all_values if t.date() == dt_sel.date()]

            if day_vals:
                exact = [v for t, v in day_vals if t.hour == dt_sel.hour and t.minute == dt_sel.minute]
                vals = [v for t, v in day_vals]

                custom = {
                    "date": dt_sel.strftime("%Y/%m/%d"),
                    "time": dt_sel.strftime("%H:%M"),
                    "value": round(exact[0], 9) if exact else None,
                    "avg": round(sum(vals)/len(vals), 9),
                    "max": round(max(vals), 9),
                    "min": round(min(vals), 9)
                }
        except:
            custom = None

    return {
        "today": today_summary,
        "selected": selected_summary,
        "custom": custom
    }