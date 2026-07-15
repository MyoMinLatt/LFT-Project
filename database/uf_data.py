from config import LFT_DB
from datetime import datetime, timedelta
import statistics
import sqlite3


# ==========================================================
# UF DEVICE MAP
# ==========================================================
UF_DEVICE_MAP = {

    "Pressure (bar)": {
        "PT001": ("Pressure", "UF_PT001"),
        "PT002": ("Pressure", "UF_PT002"),
        "PT003": ("Pressure", "UF_PT003"),
        "PT004": ("Pressure", "UF_PT004"),
        "PT005": ("Pressure", "UF_PT005"),
        "PT006": ("Pressure", "UF_PT006"),
        "PT007": ("Pressure", "UF_PT007"),
    },

    "TMP (bar)": {
        "UF_TMP": ("Pressure", "UF_TMP"),
    },

    "Temperature (°C)": {
        "TIT001": ("Temperature", "UF_TIT001"),
        "TIT002": ("Temperature", "UF_TIT002"),
        "TT003": ("Temperature", "UF_TT003"),
    },

    "pH": {
        "pH001": ("pH", "UF_pH001"),
    },

    "Flow (m3/h)": {
        "FIT001": ("FlowRate", "UF_FIT001"),
        "FIT002": ("FlowRate", "UF_FIT002"),
    },

    "Conductivity (mS/cm)": {
        "EC001": ("Conductivity", "UF_EC001"),
    },

    "Turbidity (NTU)": {
        "TUB001": ("Turbidity", "UF_TUB001"),
    },

    "Agitator (Hz)": {
        "AG001": ("Agitator", "UF_AG001"),
    },

"Pumps": {

           "P001": ("Pumps", "UF_P001"),
            "P002": ("Pumps", "UF_P002"),
            "P003": ("Pumps", "UF_P003"),
            "P004": ("Pumps", "UF_P004"),
            "P005": ("Pumps", "UF_P005"),
        }
}


# ==========================================================
# Detect Time Column
# ==========================================================
def get_time_column(cursor, table):

    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()

    for col in columns:
        name = col[1].lower()
        if "time" in name or "date" in name:
            return col[1]

    return None


# ==========================================================
# Flexible Time Parser
# ==========================================================
def parse_time_flexible(time_str):

    for fmt in [
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S"
    ]:
        try:
            return datetime.strptime(time_str, fmt)
        except:
            continue

    return None


# ==========================================================
# SAFE INTERVAL SAMPLING (FIXED)
# ==========================================================
def sample_by_interval(rows, interval):

    parsed = []

    for r in rows:
        if r[1] is None:
            continue

        dt = parse_time_flexible(r[0])
        if dt:
            parsed.append((dt, float(r[1])))

    if not parsed:
        return []

    # Determine step size
    if interval == "5min":
        step = timedelta(minutes=5)

    elif interval == "15min":
        step = timedelta(minutes=15)

    elif interval == "30min":
        step = timedelta(minutes=30)

    elif interval == "1hour":
        step = timedelta(hours=1)

    elif interval == "1day":
        step = timedelta(days=1)

    elif interval == "1week":
        step = timedelta(weeks=1)

    elif interval == "1month":
        step = timedelta(days=30)

    else:
        return rows

    sampled = []
    last_added_time = None

    for dt, value in parsed:

        if not last_added_time:
            sampled.append((dt, value))
            last_added_time = dt
        else:
            if dt - last_added_time >= step:
                sampled.append((dt, value))
                last_added_time = dt

    if not sampled:
        return rows  # fallback safety

    return [(t.strftime("%Y/%m/%d %H:%M:%S"), v) for t, v in sampled]


# ==========================================================
# MAIN UF DATA FUNCTION
# ==========================================================
def get_uf_device_data(parameter, device, interval, start=None, end=None):

    if parameter not in UF_DEVICE_MAP:
        return {}

    if device not in UF_DEVICE_MAP[parameter]:
        return {}

    table, column = UF_DEVICE_MAP[parameter][device]

    conn = sqlite3.connect(LFT_DB)
    cursor = conn.cursor()

    time_column = get_time_column(cursor, table)
    if not time_column:
        conn.close()
        return {}

    column_safe = f'"{column}"'

    # ======================================================
    # ALWAYS GET GLOBAL LATEST
    # ======================================================
    cursor.execute(f"""
        SELECT {time_column}, {column_safe}
        FROM {table}
        ORDER BY {time_column} DESC
        LIMIT 1
    """)
    latest_row = cursor.fetchone()



    if not latest_row:
        conn.close()
        return {}

    real_latest_time = latest_row[0]
    real_latest_value = float(latest_row[1]) if latest_row[1] else 0

    rows = []
    custom_active = False

    # ======================================================
    # CUSTOM RANGE
    # ======================================================
    if start and end:

        try:
            if "T" in start:
                start_time = datetime.strptime(start, "%Y-%m-%dT%H:%M")
                end_time = datetime.strptime(end, "%Y-%m-%dT%H:%M")
            else:
                start_time = datetime.strptime(start, "%Y/%m/%d %H:%M:%S")
                end_time = datetime.strptime(end, "%Y/%m/%d %H:%M:%S")
        except:
            conn.close()
            return {}

        start_str = start_time.strftime("%Y/%m/%d %H:%M:%S")
        end_str = end_time.strftime("%Y/%m/%d %H:%M:%S")

        cursor.execute(f"""
            SELECT {time_column}, {column_safe}
            FROM {table}
            WHERE {time_column} BETWEEN ? AND ?
            ORDER BY {time_column} ASC
        """, (start_str, end_str))

        rows = cursor.fetchall()
        custom_active = True


    else:

        cursor.execute(f"""
            SELECT {time_column}, {column_safe}
            FROM {table}
            ORDER BY {time_column} DESC
            LIMIT 5000
        """)
        rows = cursor.fetchall()

        rows.reverse()  # oldest → newest

    conn.close()

    # ======================================================
    # APPLY INTERVAL SAMPLING
    # ======================================================
    if rows and interval in ["5min", "15min","30min", "1hour", "1day", "1week", "1month"]:
        rows = sample_by_interval(rows, interval)

    # ======================================================
    # NO DATA
    # ======================================================
    if not rows:
        return {
            "timestamps": [],
            "values": [],
            "latest": real_latest_value,
            "mean": 0,
            "min": 0,
            "max": 0,
            "data_time": real_latest_time
        }

    timestamps = [r[0] for r in rows]
    values = [float(r[1]) if r[1] else 0 for r in rows]

    # FIXED latest data time logic
    if custom_active:
        data_time = timestamps[-1]
    else:
        data_time = real_latest_time

    return {
        "timestamps": timestamps,
        "values": values,
        "latest": real_latest_value,
        "mean": round(statistics.mean(values), 5),
        "min": min(values),
        "max": max(values),
        "data_time": data_time
    }