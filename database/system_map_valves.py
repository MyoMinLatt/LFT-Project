from config import LFT_DB
from database.db_utils import get_latest_value


# ===============================
# Valves Mapping
# ===============================

SYSTEM_MAP_VALVES = {

    "UF": {
        "XV001": ("UF_Valves", "XV001"),
        "XV002": ("UF_Valves", "XV002"),
        "XV003": ("UF_Valves", "XV003"),
        "XV004": ("UF_Valves", "XV004"),
        "XV005": ("UF_Valves", "XV005"),
        "XV006": ("UF_Valves", "XV006"),
        "XV007": ("UF_Valves", "XV007"),
        "XV008": ("UF_Valves", "XV008"),
        "XV009": ("UF_Valves", "XV009"),
        "XV010": ("UF_Valves", "XV010"),
        "XV011": ("UF_Valves", "XV011"),
        "XV012": ("UF_Valves", "XV012"),
    },

    "RO": {
        "XV013": ("RO_Valves", "XV013"),
    }
}

# ===============================
# Check Table Exists [This block was added when tables of Valves in Sqlit database was not considered.]
# ===============================

def table_exists(db_path, table_name):

    import sqlite3

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name=?
            """,
            (table_name,)
        )

        result = cursor.fetchone()

        conn.close()

        return result is not None

    except Exception:
        return False

# ===============================
# Convert 0 / 1 to Status
# ===============================

def format_binary_status(value):

    if value is None:
        return {
            "text": "ERROR",
            "status": "error"
        }

    try:
        value = int(value)
    except:
        return {
            "text": "ERROR",
            "status": "error"
        }

    if value == 1:
        return {
            "text": "ON",
            "status": "on"
        }

    elif value == 0:
        return {
            "text": "OFF",
            "status": "off"
        }

    else:
        return {
            "text": "ERROR",
            "status": "error"
        }



# ===============================
# Get Latest Valve Data
# ===============================

def get_all_latest_valves():

    result = {
        "UF": {},
        "RO": {}
    }

    # 🔥 FIX: Loop directly through SYSTEM_MAP_VALVES
    for unit, valves in SYSTEM_MAP_VALVES.items():

        for name, (table, column) in valves.items():

            # Skip missing valve tables temporarily
            if not table_exists(LFT_DB, table):
                result[unit][name] = {
                    "text": "N/A",
                    "status": "error"
                }
                continue

            # Use this block when valve tables is added in Sqlit Database
            value = get_latest_value(
                LFT_DB,
                table,
                column
            )

            result[unit][name] = format_binary_status(value)

    return result




# ===============================
# Format For Dashboard Table
# ===============================

def get_valves_table():

    raw_data = get_all_latest_valves()

    final_table = []

    uf_data = raw_data.get("UF", {})
    ro_data = raw_data.get("RO", {})

    uf_list = list(uf_data.items())
    ro_list = list(ro_data.items())

    max_len = max(len(uf_list), len(ro_list))

    # Fill empty rows to align table
    uf_list += [("", {"text": "", "status": ""})] * (max_len - len(uf_list))
    ro_list += [("", {"text": "", "status": ""})] * (max_len - len(ro_list))

    for i in range(max_len):

        uf_dev, uf_val = uf_list[i]
        ro_dev, ro_val = ro_list[i]

        row = {
            "uf_device": uf_dev,
            "uf_value": uf_val,

            "ro_device": ro_dev,
            "ro_value": ro_val
        }

        final_table.append(row)

    return final_table


# ===============================
# Test
# ===============================

if __name__ == "__main__":

    import pprint
    pprint.pprint(get_valves_table())
