from config import LFT_DB
from database.db_utils import get_latest_value

# ===============================
# Pump Mapping
# ===============================

SYSTEM_MAP = {

    "Pumps": {

        "UF": {
            "P001": ("UF_Pumps", "UF_P001"),
            "P002": ("UF_Pumps", "UF_P002"),
            "P003": ("UF_Pumps", "UF_P003"),
            "P004": ("UF_Pumps", "UF_P004"),
            "P005": ("UF_Pumps", "UF_P005"),
        },

        "RO": {
            "P006": ("RO_Pumps", "RO_P001"),
            "P007": ("RO_Pumps", "RO_P002"),
        }
    }
}

# ===============================
# Read Latest Values
# ===============================

def get_all_latest_data():
    result = {}
    for category, systems in SYSTEM_MAP.items():
        result[category] = {}
        for unit, sensors in systems.items():
            result[category][unit] = {}
            for name, (table, column) in sensors.items():
                value = get_latest_value(LFT_DB, table, column)
                result[category][unit][name] = value
    return result

# ===============================
# Format For Dashboard
# ===============================

def get_pumps_table():
    raw_data = get_all_latest_data()
    final_table = []

    pumps = raw_data.get("Pumps", {})
    uf_data = pumps.get("UF", {})
    ro_data = pumps.get("RO", {})

    uf_list = list(uf_data.items())
    ro_list = list(ro_data.items())

    max_len = max(len(uf_list), len(ro_list))

    uf_list += [("", "")] * (max_len - len(uf_list))
    ro_list += [("", "")] * (max_len - len(ro_list))

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
# Device Lookup
# ===============================

def get_table_column(device):
    """
    Find a pump device in the pumps map and return its info.
    """
    for category in SYSTEM_MAP:
        for system in SYSTEM_MAP[category]:
            pumps = SYSTEM_MAP[category][system]
            if device in pumps:
                return pumps[device]
    return None, None

# ===============================
# Test
# ===============================

if __name__ == "__main__":
    import pprint
    pprint.pprint(get_pumps_table())