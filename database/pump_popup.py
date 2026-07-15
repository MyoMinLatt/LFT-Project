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
            return datetime.strptime(ts, fmt)
        except ValueError:
            pass

    return None


# ✅ SAME AS DEVICE
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
        "latest": "-","recent": "-","avg30m": "-",
        "avg1hr": "-","avg1d": "-","max": "-","min": "-"
    }


def get_device_popup_data(device, date=None, datetime_param=None):

    table, column = find_device(device)
    if not table:
        return {"today": empty_summary(), "selected": None, "custom": None}

    conn = sqlite3.connect(LFT_DB)
    cur = conn.cursor()

    cur.execute(f'''
        SELECT Time, "{column}"
        FROM "{table}"
        ORDER BY Time DESC
        LIMIT 10000
    ''')

    rows = cur.fetchall()
    rows.reverse()

    conn.close()

    dt_vals = []

    for ts, v in rows:

        t = parse_time(ts)

        if t is None:
            continue

        # Keep only every 5 seconds
        if t.second % 5 != 0:
            continue

        try:
            val = float(v)
        except:
            continue

        dt_vals.append((t, val))

    if not dt_vals:
        return {"today": empty_summary(), "selected": None, "custom": None}

    dt_vals.sort()

    print("\nFirst 10 timestamps:")
    for t, v in dt_vals[:10]:
        print(t)
    latest_time = dt_vals[-1][0]

    # -------- TODAY --------
    today_vals = [

        (t, v)

        for t, v in dt_vals

        if t.date() == latest_time.date()
           and t.second % 5 == 0

    ]

    latest_time = latest_time.replace(
        second=(latest_time.second // 5) * 5,
        microsecond=0
    )

    today_data = calculate_summary(today_vals, latest_time)

    # -------- SELECTED (FIXED LOGIC 1) --------
    selected_data = None

    if date:
        dt = datetime.strptime(date, "%Y-%m-%d")
        sel_vals = [

    (t, v)

    for t, v in dt_vals

    if t.date() == dt.date()
       and t.second % 5 == 0

]

        if sel_vals:
            target_time = latest_time.replace(

                year=dt.year,
                month=dt.month,
                day=dt.day,

                microsecond=0

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
                    "avg1d": round(sum(vals)/len(vals), 3),
                    "max": round(max(vals), 3),
                    "min": round(min(vals), 3)
                }
            else:
                selected_data = calculate_summary(sel_vals, closest_time)

        else:
            selected_data = empty_summary()

    # -------- CUSTOM (UNCHANGED) --------
    custom = None
    if datetime_param:
        try:
            print("datetime_param =", repr(datetime_param))
            dt_sel = datetime.strptime(datetime_param, "%Y-%m-%d %H:%M:%S")
            day_vals = [(t, v) for t, v in dt_vals if t.date() == dt_sel.date()]

            if day_vals:
                exact = [

                    v

                    for t, v in day_vals

                    if t.hour == dt_sel.hour
                       and t.minute == dt_sel.minute
                       and t.second == dt_sel.second

                ]
                vals = [v for t, v in day_vals]

                custom = {
                    "date": dt_sel.strftime("%Y/%m/%d"),
                    "time": dt_sel.strftime("%H:%M:%S"),
                    "value": round(exact[0], 3) if exact else None,
                    "avg": round(sum(vals) / len(vals), 3),
                    "max": round(max(vals), 3),
                    "min": round(min(vals), 3)
                }
        except Exception as e:
                print("CUSTOM ERROR:", e)
                custom = None

    return {
        "today": today_data,
        "selected": selected_data,
        "custom": custom
    }