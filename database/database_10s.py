import pandas as pd
import sqlite3
import os
import glob

# ===============================
# USER SETTINGS
# ===============================
CSV_FOLDER = r"H:\SejongRain\LATT_Work\2026_Data\LET_Project\Real_LFT_Data\Daily_LFT_Data"
DB_FILE = r"H:\SejongRain\LATT_Work\2026_Data\LET_Project\wastewater_dashboard - Copy\database\LFT_DB_3.db"


COLUMN_MAP = {

    "WORD.P002": "UF_P002",
    "WORD.P007": "RO_P007",

    "WORD.EC001": "UF_EC001",
    "WORD.EC002": "RO_EC002",
    "WORD.EC003": "RO_EC003",

    "WORD.PH001": "UF_pH001",
    "WORD.PH002": "RO_pH002",
    "WORD.PH003": "RO_pH003",

    "WORD.PT001": "UF_PT001",
    "WORD.PT002": "UF_PT002",
    "WORD.PT003": "UF_PT003",
    "WORD.PT004": "UF_PT004",
    "WORD.PT005": "UF_PT005",
    "WORD.PT006": "UF_PT006",
    "WORD.PT007": "UF_PT007",
    "WORD.PT008": "RO_PT008",
    "WORD.PT009": "RO_PT009",
    "WORD.PT010": "RO_PT010",
    "WORD.PT011": "RO_PT011",

    "WORD.FIT001": "UF_FIT001",
    "WORD.FIT002": "UF_FIT002",
    "WORD.FT001": "RO_FT001",
    "WORD.FT002": "RO_FT002",

    "WORD.TIT001": "UF_TIT001",
    "WORD.TIT002": "UF_TIT002",
    "WORD.TT003": "UF_TT003",
    "WORD.TT004": "RO_TT004",

    "WORD.TUB001": "UF_TUB001",

    "WORD.ORP001": "RO_ORP001",

    "WORD.AG001": "UF_AG001",

    "WORD.FCV001_SET_D": "RO_FCV001",

    "WORD.POWER_W": "Active_Power",
    "WORD.POWER_WH": "Energy_Wh",
    "WORD.CYCLE_C": "Cycle_Count",

    "WORD.STEP1_ET": "Step1",
    "WORD.STEP2_ET": "Step2",
    "WORD.STEP3_ET": "Step3",
    "WORD.STEP4_ET": "Step4",
    "WORD.STEP5_ET": "Step5",
    "WORD.STEP6_ET": "Step6",

    "WORD.STEP11_ET": "Step11",
    "WORD.STEP12_ET": "Step12",
    "WORD.STEP13_ET": "Step13",
    "WORD.STEP14_ET": "Step14",
    "WORD.STEP15_ET": "Step15",
}




# ===============================
# COLUMN → TABLE MAPPING RULES
# ===============================
TABLE_RULES = {"Pressure":["UF_PT", "RO_PT", "UF_TMP", "RO_TMP"],
                "Conductivity":["UF_EC", "RO_EC"],
                "FlowRate":[ "UF_FIT", "RO_FT" ],
                "Temperature":["UF_TIT", "UF_TT", "RO_TT"],
                "pH":["UF_pH", "RO_pH"],
                "ORP":["RO_ORP" ],
                "Turbidity":["UF_TUB"],
                "Agitator":["UF_AG"],
                "Pumps":["UF_P", "RO_P"],
                "RO_Concentrate":["RO_FCV"],
                "Active_Power":["Active_Power","Energy_Wh", "Cycle_Count"],
                "Process_Steps":["Step"],
                "Valves": ["XV"]
}

# ===============================
# CLASSIFY COLUMNS
# ===============================
def classify_columns(columns):
    table_columns = {table: ["Time"] for table in TABLE_RULES.keys()}

    for col in columns:
        if col == "Time":
            continue

        matched = False
        for table, keywords in TABLE_RULES.items():
            for keyword in keywords:
                if keyword in col:
                    table_columns[table].append(col)
                    matched = True
                    break
            if matched:
                break

        if not matched:
            print(f"⚠ Unclassified column: {col}")

    return table_columns

# ===============================
# CREATE TABLE
# ===============================
def create_table(cursor, table_name, columns):
    col_defs = ["Time TEXT"]
    for col in columns:
        if col != "Time":
            col_defs.append(f'"{col}" REAL')

    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {", ".join(col_defs)}
    );
    """
    cursor.execute(sql)

# ===============================
# ADD MISSING COLUMNS
# ===============================
#def ensure_columns(cursor, table_name, columns):
#    cursor.execute(f"PRAGMA table_info({table_name});")
#    existing_cols = [row[1] for row in cursor.fetchall()]

#    for col in columns:
#        if col not in existing_cols:
#            print(f"➕ Adding column '{col}' to {table_name}")
#            cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN "{col}" REAL;')

# ===============================
# INSERT DATA
# ===============================
#def insert_data(conn, cursor, df, table_name, columns):
#    subset = df[columns]

#    placeholders = ", ".join(["?"] * len(columns))
#    col_names = ", ".join([f'"{c}"' for c in columns])

#    sql = f"""
#    INSERT INTO {table_name} ({col_names})
#    VALUES ({placeholders});
#    """

#    cursor.executemany(sql, subset.values.tolist())
#    conn.commit()





# ===============================
# MAIN PROCESS
# ===============================
#def main():
#    print("📂 Scanning CSV folder...")
#    csv_files = glob.glob(os.path.join(CSV_FOLDER, "*.csv"))

#    if not csv_files:
#        print("❌ No CSV files found in folder.")
#        return

    # ✅ Select only the latest file
#    latest_csv = max(csv_files, key=os.path.getmtime)
#    print(f"✅ Latest CSV file detected: {os.path.basename(latest_csv)}")



#    try:
#        df = pd.read_csv(latest_csv, encoding="utf-8")
#        df.rename(columns=COLUMN_MAP, inplace=True)

    # --------------------------------------
    # Calculate TMP (Transmembrane Pressure)
    # --------------------------------------

    # UF TMP = (PT001 + PT005)/2 - PT002
#    required_cols = ["UF_PT001", "UF_PT002", "UF_PT005"]
#    if all(col in df.columns for col in required_cols):
#        df["UF_TMP"] = (
#                (df["UF_PT001"] + df["UF_PT005"]) / 2
#                - df["UF_PT002"]
#        )

    # RO TMP = (PT009 + PT010)/2 - PT011
#    required_cols = ["RO_PT009", "RO_PT010", "RO_PT011"]
#    if all(col in df.columns for col in required_cols):
#        df["RO_TMP"] = (
#                (df["RO_PT009"] + df["RO_PT010"]) / 2
#                - df["RO_PT011"]
#        )

        # 🔧 Fix Time format: from "2025/1022 11:04:48" → "2025/10/22 11:04:48"
#        df["Time"] = pd.to_datetime(
#            df["Time"],
#            errors="coerce"
#        )

        # Show bad rows (if any)
#        bad = df["Time"].isna()
#        if bad.any():
#            print("⚠ Invalid Time rows found:")
#            print(df.loc[bad, "Time"].head())

        # Standardize format for DB
#        df["Time"] = df["Time"].dt.strftime("%Y/%m/%d %H:%M:%S")

#    except Exception as e:
#        print(f"❌ Failed to read file: {e}")
#        return

#    if "Time" not in df.columns:
#        print("⚠ CSV skipped: No 'Time' column found.")
#        return

    #    print("🗄 Connecting to SQLite database...")
    #    conn = sqlite3.connect(DB_FILE)
    #    cursor = conn.cursor()

    # Classify columns
#    table_columns = classify_columns(df.columns)

    # Create tables + ensure schema
#    for table, columns in table_columns.items():
#        if len(columns) > 1:
#            create_table(cursor, table, columns)
#            ensure_columns(cursor, table, columns)

    # Insert data
#    for table, columns in table_columns.items():
#        if len(columns) > 1:
#            print(f"📤 Inserting into {table}")
#            insert_data(conn, cursor, df, table, columns)

#    conn.close()
#    print("\n✅ Latest CSV file imported successfully.")


    # To Read all csv files
def ensure_columns(cursor, table_name, columns):
        cursor.execute(f"PRAGMA table_info({table_name});")
        existing_cols = [row[1] for row in cursor.fetchall()]

        for col in columns:
            if col not in existing_cols:
                print(f"➕ Adding column '{col}' to {table_name}")
                cursor.execute(
                    f'ALTER TABLE {table_name} ADD COLUMN "{col}" REAL;'
                )
def insert_data(conn, cursor, df, table_name, columns):

        subset = df[columns]

        placeholders = ", ".join(["?"] * len(columns))
        col_names = ", ".join([f'"{c}"' for c in columns])

        sql = f"""
        INSERT INTO {table_name} ({col_names})
        VALUES ({placeholders});
        """

        cursor.executemany(sql, subset.values.tolist())
        conn.commit()

    # ===============================
    # MAIN PROCESS
    # ===============================

def main():

        print("📂 Scanning CSV folder...")

        csv_files = sorted(glob.glob(os.path.join(CSV_FOLDER, "*.csv")))

        if not csv_files:
            print("❌ No CSV files found.")
            return

        print(f"Found {len(csv_files)} CSV files.")

        print("🗄 Connecting to SQLite database...")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for csv_file in csv_files:

            print(f"\n📄 Processing {os.path.basename(csv_file)}")

            try:
                df = pd.read_csv(csv_file, encoding="utf-8")

            except Exception as e:
                print(f"❌ Cannot read {csv_file}")
                print(e)
                continue

            # --------------------------------------
            # Rename columns
            # --------------------------------------
            df.rename(columns=COLUMN_MAP, inplace=True)

            # --------------------------------------
            # Calculate TMP (Transmembrane Pressure)
            # --------------------------------------

            # UF TMP = (PT001 + PT005)/2 - PT002
            required_cols = ["UF_PT001", "UF_PT002", "UF_PT005"]
            if all(col in df.columns for col in required_cols):
                df["UF_TMP"] = (
                        (df["UF_PT001"] + df["UF_PT005"]) / 2
                        - df["UF_PT002"]
                )

            # RO TMP = (PT009 + PT010)/2 - PT011
            required_cols = ["RO_PT009", "RO_PT010", "RO_PT011"]
            if all(col in df.columns for col in required_cols):
                df["RO_TMP"] = (
                        (df["RO_PT009"] + df["RO_PT010"]) / 2
                        - df["RO_PT011"]
                )

            # --------------------------------------
            # Check Time column
            # --------------------------------------
            if "Time" not in df.columns:
                print("⚠ No Time column.")
                continue

            # --------------------------------------
            # Convert Time
            # --------------------------------------
            df["Time"] = pd.to_datetime(
                df["Time"],
                errors="coerce"
            )

            bad = df["Time"].isna()

            if bad.any():
                print(f"⚠ Skipped {bad.sum()} bad rows.")
                df = df[~bad]
            # --------------------------------------
            # Keep only 10-second interval records
            # --------------------------------------
            df = df[df["Time"].dt.second % 10 == 0].copy()

            print(f"Keeping {len(df)} rows at 10-second intervals.")

            df["Time"] = df["Time"].dt.strftime("%Y/%m/%d %H:%M:%S")

            # --------------------------------------
            # Classify columns
            # --------------------------------------
            table_columns = classify_columns(df.columns)

            # --------------------------------------
            # Create tables / Add new columns
            # --------------------------------------
            for table, columns in table_columns.items():

                if len(columns) <= 1:
                    continue

                create_table(cursor, table, columns)
                ensure_columns(cursor, table, columns)

            # --------------------------------------
            # Insert data
            # --------------------------------------
            for table, columns in table_columns.items():

                if len(columns) <= 1:
                    continue

                print(f"📤 Inserting into {table}")

                insert_data(
                    conn,
                    cursor,
                    df,
                    table,
                    columns
                )

        conn.commit()
        conn.close()

        print("\n✅ All CSV files imported successfully.")



# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    main()