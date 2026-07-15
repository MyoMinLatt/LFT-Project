import sqlite3
from datetime import datetime, timedelta
from config import LFT_DB
from database.system_map import get_table_column

DB_PATH = LFT_DB

def parse_time(t):

    formats = [

        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",

        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",

        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",

        "%Y-%m-%dT%H:%M:%S"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(t, fmt)
        except ValueError:
            pass

    return None


def fetch_values(device):

    print(f"\nRequested device = {device}")

    table, column = get_table_column(device)

    print(f"Mapped table = {table}")
    print(f"Mapped column = {column}")

    if table is None:
        print("Device not found in SYSTEM_MAP")
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
        # --------------------------------------
        # Keep only every 5 seconds
        # # hh:mm:00,05,10,...55
        # --------------------------------------
        if dt.second % 5 != 0:
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
    avg_day_val = round(sum(day_vals) / len(day_vals), 3) if day_vals else "-"

    interval_vals = [v for t, v in values if t <= latest_time]

    latest_val = interval_vals[-1] if interval_vals else "-"
    recent_val = interval_vals[-2] if len(interval_vals) >= 2 else latest_val

    def avg_minutes(minutes):
        start = latest_time - timedelta(minutes=minutes)
        vals = [v for t, v in values if start <= t <= latest_time]
        return round(sum(vals) / len(vals), 3) if vals else "-"

    def safe_round(val):
        return round(val, 3) if isinstance(val, (int, float)) else "-"

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
    today_vals = [
        (t, v)
        for t, v in all_values
        if t.date() == latest_time.date()
           and t.second % 5 == 0
    ]

    latest_time = latest_time.replace(
        second=(latest_time.second // 5) * 5,
        microsecond=0
    )

    today_summary = calculate_summary(today_vals, latest_time)

    # -------- SELECTED --------
    selected_summary = None
    if date:
        dt = datetime.strptime(date, "%Y-%m-%d")
        sel_vals = [
            (t, v)
            for t, v in all_values
            if t.date() == dt.date()
               and t.second % 5 == 0
        ]

        if sel_vals:
            # Target time (same clock time as Today)
            target_time = latest_time.replace(
                year=dt.year,
                month=dt.month,
                day=dt.day,

                microsecond=0
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
                    "avg1d": round(sum(vals) / len(vals), 3),
                    "max": round(max(vals), 3),
                    "min": round(min(vals), 3)
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
            print("datetime_param =", repr(datetime_param))
            dt_sel = datetime.strptime(datetime_param, "%Y-%m-%d %H:%M:%S")
            day_vals = [(t, v) for t, v in all_values if t.date() == dt_sel.date()]

            if day_vals:
                exact = [v for t, v in day_vals if t.hour == dt_sel.hour and t.minute == dt_sel.minute and t.second == dt_sel.second]
                vals = [v for t, v in day_vals]

                custom = {
                    "date": dt_sel.strftime("%Y/%m/%d"),
                    "time": dt_sel.strftime("%H:%M:%S"),
                    "value": round(exact[0], 3) if exact else None,
                    "avg": round(sum(vals)/len(vals), 3),
                    "max": round(max(vals), 3),
                    "min": round(min(vals), 3)
                }
        except Exception as e:
                print("CUSTOM ERROR:", e)
                custom = None

    return {
        "today": today_summary,
        "selected": selected_summary,
        "custom": custom
    }