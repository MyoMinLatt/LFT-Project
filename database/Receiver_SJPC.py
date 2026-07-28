import socket
import threading
import pandas as pd
import sqlite3
import os
import glob
from datetime import datetime
import struct

# ==========================
# CSV source folder (PC2)
# ==========================

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 6000



# ==========================
# Database
# ==========================

# -------- OPTION 1 --------------------
# Local folder ( PC1)

CSV_FOLDER = r"C:\LET_Project\LFT_New_DATA"

# SQLite database (PC2)

DB_FILE = (
    r"H:\SejongRain\LATT_Work\2026_Data\LET_Project"
    r"\wastewater_dashboard - Copy"
    r"\database\LFT_DB_2.db"
)

# ==========================================================
# COLUMN MAP
# ==========================================================

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

# ==========================================================
# COLUMN → TABLE RULES
# ==========================================================

TABLE_RULES = {
    "Pressure": ["UF_PT", "RO_PT", "UF_TMP", "RO_TMP"],
    "Conductivity": ["UF_EC", "RO_EC"],
    "FlowRate": ["UF_FIT", "RO_FT"],
    "Temperature": ["UF_TIT", "UF_TT", "RO_TT"],
    "pH": ["UF_pH", "RO_pH"],
    "ORP": ["RO_ORP"],
    "Turbidity": ["UF_TUB"],
    "Agitator": ["UF_AG"],
    "Pumps": ["UF_P", "RO_P"],
    "RO_Concentrate": ["RO_FCV"],
    "Active_Power": ["Active_Power", "Energy_Wh", "Cycle_Count"],
    "Process_Steps": ["Step"],
    "Valves": ["XV"]
}

# ==========================================================
# IMPORT HISTORY TABLE
# ==========================================================

def create_import_history(cursor):

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ImportHistory
    (
        FileName TEXT PRIMARY KEY,
        ImportDate TEXT,
        TotalRows INTEGER
    )
    """)


def get_imported_files(cursor):

    cursor.execute("SELECT FileName FROM ImportHistory")

    return set(row[0] for row in cursor.fetchall())


def save_import_history(cursor,
                        conn,
                        filename,
                        total_rows):

    cursor.execute(
        """
        INSERT INTO ImportHistory
        (
            FileName,
            ImportDate,
            TotalRows
        )
        VALUES
        (
            ?,
            ?,
            ?
        )
        """,
        (
            filename,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_rows
        )
    )

    conn.commit()


def print_header():

    print("=" * 65)
    print(" Wastewater CSV Importer Version 2 ")
    print("=" * 65)

# ==========================================================
# CLASSIFY COLUMNS
# ==========================================================

def classify_columns(columns):

    table_columns = {}

    for table in TABLE_RULES:
        table_columns[table] = ["Time"]

    for col in columns:

        if col == "Time":
            continue

        found = False

        for table, keywords in TABLE_RULES.items():

            for keyword in keywords:

                if keyword in col:
                    table_columns[table].append(col)

                    found = True
                    break

            if found:
                break

        if not found:
            print(f"⚠ Unclassified column : {col}")

    return table_columns

# ==========================================================
# CREATE TABLE
# ==========================================================

def create_table(cursor, table_name, columns):

    definitions = ["Time TEXT UNIQUE"]

    for col in columns:

        if col == "Time":
            continue

        definitions.append(f'"{col}" REAL')

    sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name}
        (
            {", ".join(definitions)}
        );
    """

    cursor.execute(sql)

    cursor.execute(f"""
    CREATE INDEX IF NOT EXISTS idx_{table_name}_time
    ON {table_name}(Time)
    """)

# ==========================================================
# ENSURE NEW COLUMNS EXIST
# ==========================================================

def ensure_columns(cursor, table_name, columns):

    cursor.execute(f"PRAGMA table_info({table_name})")

    existing_columns = [row[1] for row in cursor.fetchall()]

    for col in columns:

        if col not in existing_columns:
            print(f"➕ Adding new column : {table_name}.{col}")

            cursor.execute(
                f'ALTER TABLE {table_name} '
                f'ADD COLUMN "{col}" REAL'
            )

# ==========================================================
# INSERT DATA
# ==========================================================

def insert_data(
    conn,
    cursor,
    dataframe,
    table_name,
    columns
):

    subset = dataframe[columns]

    placeholders = ",".join(["?"] * len(columns))

    names = ",".join(
        [f'"{c}"' for c in columns]
    )

    sql = f"""
    INSERT OR IGNORE INTO
    {table_name}
    ({names})

    VALUES

    ({placeholders})
    """
    cursor.execute(f"""
    CREATE INDEX IF NOT EXISTS idx_{table_name}_time
    ON {table_name}(Time)
    """)

    for row in subset.values.tolist():

        cursor.execute(
            f"SELECT 1 FROM {table_name} WHERE Time=?",
            (row[0],)
        )

        if cursor.fetchone() is None:
            cursor.execute(sql, row)



# ==========================================================
# CHECK CSV FILE
# ==========================================================

def validate_csv(csv_file):

    if not os.path.exists(csv_file):
        print(f"❌ Missing : {csv_file}")

        return False

    if os.path.getsize(csv_file) == 0:
        print(f"❌ Empty file : {csv_file}")

        return False

    return True

# ==========================================================
# READ CSV
# ==========================================================

def read_csv(csv_file):

    try:

        df = pd.read_csv(
            csv_file,
            encoding="utf-8"
        )

        return df

    except Exception as e:

        print("❌ Cannot read")

        print(csv_file)

        print(e)

        return None

# ============================================================
# Receiving function
# ============================================================
def receive_csv_from_client(conn):

    # Receive filename length

    raw = conn.recv(4)

    if len(raw) < 4:
        return None

    name_length = struct.unpack("I", raw)[0]

    # Receive filename

    filename = b""

    while len(filename) < name_length:

        filename += conn.recv(name_length - len(filename))

    filename = filename.decode("utf-8")

    # Receive file size

    raw = conn.recv(8)

    file_size = struct.unpack("Q", raw)[0]

    csv_path = os.path.join(CSV_FOLDER, filename)

    received = 0

    with open(csv_path, "wb") as f:

        while received < file_size:

            chunk = conn.recv(min(4096, file_size - received))

            if not chunk:
                break

            f.write(chunk)

            received += len(chunk)

    print(f"📥 Received {filename}")

    return csv_path

def start_server():

    os.makedirs(
        CSV_FOLDER,
        exist_ok=True
    )

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )


    server.bind(
        (SERVER_HOST, SERVER_PORT)
    )

    server.listen()


    print("🚀 CSV Database Server Running")
    print(
        f"Listening on port {SERVER_PORT}"
    )


    while True:

        conn, addr = server.accept()

        print(
            f"Connected from {addr}"
        )


        csv_file = receive_csv_from_client(conn)

        conn.close()


        if csv_file:

            print(
                "Starting database import..."
            )

            main()





# ==========================================================
# MAIN
# ==========================================================

def main():

    print_header()

    print("\n📂 Scanning CSV folder...")

    if not os.path.exists(CSV_FOLDER):

        print("❌ CSV folder not found.")

        print(CSV_FOLDER)

        return

    csv_files = sorted(
        glob.glob(
            os.path.join(
                CSV_FOLDER,
                "*.csv"
            )
        )
    )

    if len(csv_files) == 0:

        print("❌ No CSV files found.")

        return

    print(f"Found {len(csv_files)} CSV file(s).")

    print("\n🗄 Connecting to SQLite...")

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    # -----------------------------------
    # Create ImportHistory table
    # -----------------------------------

    create_import_history(cursor)
    conn.commit()


    # -----------------------------------
    # Load imported files
    # -----------------------------------

    imported_files = get_imported_files(cursor)

    print(
        f"Previously imported : "
        f"{len(imported_files)} file(s)"
    )

    # -----------------------------------
    # Process every CSV
    # -----------------------------------

    imported_today = 0

    skipped = 0

    for csv_file in csv_files:

        filename = os.path.basename(csv_file)

        # Already imported?

        if filename in imported_files:

            skipped += 1

            print(f"⏩ Skip : {filename}")

            continue

        print("\n" + "="*60)

        print(f"📄 Importing : {filename}")

        print("="*60)

        if not validate_csv(csv_file):

            continue

        df = read_csv(csv_file)

        if df is None:

            continue

        print(f"Rows : {len(df)}")

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


        # --------------------------------------
        # Save Import History
        # --------------------------------------

        save_import_history(
            cursor,
            conn,
            filename,
            len(df)
        )

        imported_today += 1

        print(f"✅ Finished : {filename}")

    # =====================================================
    # Finished
    # =====================================================

    conn.commit()

    conn.close()

    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)

    print(f"CSV Files Found      : {len(csv_files)}")
    print(f"Already Imported     : {skipped}")
    print(f"Imported This Run    : {imported_today}")
    print(f"Database             : {DB_FILE}")

    print("\n✅ Import completed successfully.")


# ===============================
# RUN
# ===============================

if __name__ == "__main__":

    start_server()