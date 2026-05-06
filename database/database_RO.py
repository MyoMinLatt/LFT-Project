import pandas as pd
import sqlite3
import os
import glob

# ===============================
# USER SETTINGS
# ===============================
CSV_FOLDER = r"H:\SejongRain\LATT_Work\2026_Data\LET_Project\wastewater_dashboard - Copy\database\CSV_data_RO"
DB_FILE = r"H:\SejongRain\LATT_Work\2026_Data\LET_Project\wastewater_dashboard - Copy\database\LFT_DB.db"

# ===============================
# COLUMN → TABLE MAPPING RULES
# ===============================
TABLE_RULES = {

   "RO_Pressure": ["압력"],
    "RO_ORP": ["원전위"],
    "RO_FlowRate": ["유량"],
    "RO_Temperature": ["온도"],
    "RO_Conductivity": ["전도도"],
    "RO_pH": ["UFpH", "pH"],
    "RO_Pumps": ["펌프"],
    "RO_Valves": ['XV'],
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
def ensure_columns(cursor, table_name, columns):
    cursor.execute(f"PRAGMA table_info({table_name});")
    existing_cols = [row[1] for row in cursor.fetchall()]

    for col in columns:
        if col not in existing_cols:
            print(f"➕ Adding column '{col}' to {table_name}")
            cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN "{col}" REAL;')

# ===============================
# INSERT DATA
# ===============================
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
    csv_files = glob.glob(os.path.join(CSV_FOLDER, "*.csv"))

    if not csv_files:
        print("❌ No CSV files found in folder.")
        return

    # ✅ Select only the latest file
    latest_csv = max(csv_files, key=os.path.getmtime)
    print(f"✅ Latest CSV file detected: {os.path.basename(latest_csv)}")

    try:
        df = pd.read_csv(latest_csv, encoding="utf-8")

        # 🔧 Fix Time format: from "2025/1022 11:04:48" → "2025/10/22 11:04:48"
        df["Time"] = pd.to_datetime(
            df["Time"],
            errors="coerce"
        )

        # Show bad rows (if any)
        bad = df["Time"].isna()
        if bad.any():
            print("⚠ Invalid Time rows found:")
            print(df.loc[bad, "Time"].head())

        # Standardize format for DB
        df["Time"] = df["Time"].dt.strftime("%Y/%m/%d %H:%M:%S")

    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return

    if "Time" not in df.columns:
        print("⚠ CSV skipped: No 'Time' column found.")
        return

    print("🗄 Connecting to SQLite database...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Classify columns
    table_columns = classify_columns(df.columns)

    # Create tables + ensure schema
    for table, columns in table_columns.items():
        if len(columns) > 1:
            create_table(cursor, table, columns)
            ensure_columns(cursor, table, columns)

    # Insert data
    for table, columns in table_columns.items():
        if len(columns) > 1:
            print(f"📤 Inserting into {table}")
            insert_data(conn, cursor, df, table, columns)

    conn.close()
    print("\n✅ Latest CSV file imported successfully.")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    main()
