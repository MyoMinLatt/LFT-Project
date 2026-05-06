from config import LFT_DB
import sqlite3
import statistics

# =============================================
# RO DEVICE MAP (MUST MATCH HTML EXACTLY)
# =============================================
RO_DEVICE_MAP = {
    "Pressure (bar)": {
        "PT008": ("RO_Pressure", "RO_PT008"),
        "PT009": ("RO_Pressure", "RO_PT009"),
        "PT010": ("RO_Pressure", "RO_PT010"),
        "PT011": ("RO_Pressure", "RO_PT011"),
    },
    "TMP (bar)": {
        "RO TMP": ("RO_Pressure", "RO_TMP"),
    },
    "Temperature (°C)": {
        "TT004": ("RO_Temperature", "RO_TT004"),
    },
    "pH": {
        "pH002": ("RO_pH", "RO_pH002"),
        "pH003": ("RO_pH", "RO_pH003"),
    },
    "Flow (m3/h)": {
        "FT001": ("RO_FlowRate", "RO_FT001"),
        "FT002": ("RO_FlowRate", "RO_FT002"),
        "FI001": ("RO_FlowRate", "RO_FI001"),
        "FI002": ("RO_FlowRate", "RO_FI002"),
    },
    "Conductivity (mS/cm)": {
        "EC002": ("RO_Conductivity", "RO_EC002"),
        "EC003": ("RO_Conductivity", "RO_EC003"),
    },
    "ORP (mV)": {
        "ORP001": ("RO_ORP", "RO_ORP001"),
    },
    "Pumps": {
        "P006": ("RO_Pumps", "RO_P001"),
        "P007": ("RO_Pumps", "RO_P002"),
    }
}

# =============================================
# AUTO DETECT TIME COLUMN
# =============================================
def get_time_column(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        if "time" in col[1].lower() or "date" in col[1].lower():
            return col[1]
    return None


# =============================================
# MAIN FUNCTION
# =============================================
def get_ro_device_data(parameter, device, interval, start=None, end=None):

    if parameter not in RO_DEVICE_MAP:
        print("DEBUG PARAM NOT FOUND:", parameter)
        return {}

    if device not in RO_DEVICE_MAP[parameter]:
        print("DEBUG DEVICE NOT FOUND:", device)
        return {}

    table, column = RO_DEVICE_MAP[parameter][device]

    conn = sqlite3.connect(LFT_DB)
    cursor = conn.cursor()

    time_column = get_time_column(cursor, table)
    if not time_column:
        print("DEBUG NO TIME COLUMN")
        conn.close()
        return {}

    query = f'SELECT {time_column}, "{column}" FROM {table} ORDER BY {time_column} ASC'
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "timestamps": [],
            "values": [],
            "latest": 0,
            "mean": 0,
            "min": 0,
            "max": 0,
            "data_time": "-"
        }

    timestamps = [r[0] for r in rows]
    values = [float(r[1] or 0) for r in rows]

    return {
        "timestamps": timestamps,
        "values": values,
        "latest": values[-1],
        "mean": round(statistics.mean(values), 3),
        "min": min(values),
        "max": max(values),
        "data_time": timestamps[-1]
    }