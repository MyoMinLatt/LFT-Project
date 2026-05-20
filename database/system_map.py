from config import LFT_DB
from database.db_utils import get_latest_value


# ===============================
# System Mapping
# ===============================

SYSTEM_MAP = {

    "Pressure (bar)": {
        "UF": {
            "PT001": ("UF_Pressure", "UF_PT001"),
            "PT002": ("UF_Pressure", "UF_PT002"),
            "PT003": ("UF_Pressure", "UF_PT003"),
            "PT004": ("UF_Pressure", "UF_PT004"),
            "PT005": ("UF_Pressure", "UF_PT005"),
            "PT006": ("UF_Pressure", "UF_PT006"),
            "PT007": ("UF_Pressure", "UF_PT007"),
        },

        "RO": {
            "PT008": ("RO_Pressure", "RO_PT008"),
            "PT009": ("RO_Pressure", "RO_PT009"),
            "PT010": ("RO_Pressure", "RO_PT010"),
            "PT011": ("RO_Pressure", "RO_PT011"),
        }
    },


    "TMP (bar)": {
        "UF": {
            "UF TMP": ("UF_Pressure", "UF_TMP"),
        },

        "RO": {
            "RO TMP": ("RO_Pressure", "RO_TMP"),
        }
    },


    "Temperature (°C)": {
        "UF": {
            "TIT001": ("UF_Temperature", "UF_TIT001"),
            "TIT002": ("UF_Temperature", "UF_TIT002"),
            "TIT003": ("UF_Temperature", "UF_TIT003"),
        },

        "RO": {
            "TT004": ("RO_Temperature", "RO_TT004"),
        }
    },


    "pH": {
        "UF": {
            "pH001": ("UF_pH", "UF_pH001"),
        },

        "RO": {
            "pH002": ("RO_pH", "RO_pH002"),
            "pH003": ("RO_pH", "RO_pH003"),
        }
    },


    "Flow (m<sup>3</sup>/h)": {
        "UF": {
            "FIT001": ("UF_FlowRate", "UF_FIT001"),
            "FIT002": ("UF_FlowRate", "UF_FIT002"),
        },

        "RO": {
            "FT001": ("RO_FlowRate", "RO_FT001"),
            "FT002": ("RO_FlowRate", "RO_FT002"),
            "FI001": ("RO_FlowRate", "RO_FI001"),
            "FI002": ("RO_FlowRate", "RO_FI002"),
        }
    },


    "Conductivity (mS/cm)": {
        "UF": {
            "EC001": ("UF_Conductivity", "UF_EC001"),
        },

        "RO": {
            "EC002": ("RO_Conductivity", "RO_EC002"),
            "EC003": ("RO_Conductivity", "RO_EC003"),
        }
    },


    "Turbidity (NTU)": {
        "UF": {
            "TUB001": ("UF_Turbidity", "UF_TUB001"),
        },

        "RO": {}
    },


    "ORP (mV)": {
        "UF": {},

        "RO": {
            "ORP001": ("RO_ORP", "RO_ORP001"),
        }
    }
}


# ===============================
# Color Mapping
# ===============================

COLOR_MAP = {

    "Pressure (bar)": "bg-pressure",
    "TMP (bar)": "bg-tmp",
    "Temperature (°C)": "bg-temp",
    "Flow (m<sup>3</sup>/h)": "bg-flow",
    "pH": "bg-ph",
    "Conductivity (mS/cm)": "bg-cond",
    "Turbidity (NTU)": "bg-turb",
    "ORP (mV)": "bg-orp"

}


# ===============================
# Read Latest Data
# ===============================

def get_all_latest_data():

    result = {}

    for category, systems in SYSTEM_MAP.items():

        result[category] = {}

        for unit, sensors in systems.items():

            result[category][unit] = {}

            for name, (table, column) in sensors.items():

                value = get_latest_value(
                    LFT_DB,
                    table,
                    column
                )

                result[category][unit][name] = value

    return result


# ===============================
# Dashboard Formatter
# ===============================

VARIABLE_ORDER = list(COLOR_MAP.keys())


def get_dashboard_table():

    raw_data = get_all_latest_data()

    final_table = []

    for variable in VARIABLE_ORDER:

        if variable not in raw_data:
            continue

        uf_data = raw_data[variable].get("UF", {})
        ro_data = raw_data[variable].get("RO", {})

        uf_list = list(uf_data.items())
        ro_list = list(ro_data.items())

        # ==========================================
        # GROUP 2 DEVICES PER ROW
        # ==========================================

        uf_grouped = [
            uf_list[i:i+2]
            for i in range(0, len(uf_list), 2)
        ]

        ro_grouped = [
            ro_list[i:i+2]
            for i in range(0, len(ro_list), 2)
        ]

        max_rows = max(len(uf_grouped), len(ro_grouped))

        # fill missing rows
        while len(uf_grouped) < max_rows:
            uf_grouped.append([])

        while len(ro_grouped) < max_rows:
            ro_grouped.append([])

        # ==========================================
        # BUILD ROWS
        # ==========================================

        for i in range(max_rows):

            uf_row = uf_grouped[i]
            ro_row = ro_grouped[i]

            # UF PAIR 1
            uf1_dev = uf_row[0][0] if len(uf_row) > 0 else ""
            uf1_val = uf_row[0][1] if len(uf_row) > 0 else ""

            # UF PAIR 2
            uf2_dev = uf_row[1][0] if len(uf_row) > 1 else ""
            uf2_val = uf_row[1][1] if len(uf_row) > 1 else ""

            # RO PAIR 1
            ro1_dev = ro_row[0][0] if len(ro_row) > 0 else ""
            ro1_val = ro_row[0][1] if len(ro_row) > 0 else ""

            # RO PAIR 2
            ro2_dev = ro_row[1][0] if len(ro_row) > 1 else ""
            ro2_val = ro_row[1][1] if len(ro_row) > 1 else ""

            row = {

                "variable": variable if i == 0 else "",
                "rowspan": max_rows if i == 0 else 0,

                "color_class": COLOR_MAP.get(variable, ""),

                # UF
                "uf1_device": uf1_dev,
                "uf1_value": uf1_val,

                "uf2_device": uf2_dev,
                "uf2_value": uf2_val,

                # RO
                "ro1_device": ro1_dev,
                "ro1_value": ro1_val,

                "ro2_device": ro2_dev,
                "ro2_value": ro2_val
            }

            final_table.append(row)

    return final_table



# ===============================
# Device Lookup
# ===============================

def get_table_column(device):

    """
    Returns (table_name, column_name) for a device ID like PT001.
    """

    for category in SYSTEM_MAP.values():

        for system in category.values():

            if device in system:
                return system[device]

    return None, None

# ===============================
# Test
# ===============================

if __name__ == "__main__":

    import pprint

    pprint.pprint(get_dashboard_table())

