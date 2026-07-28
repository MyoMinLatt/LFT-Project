import socket
import os
import time
import struct
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------
PORT = 6000
FOLDER_PATH = r"C:\LET_Project\LFT_New_DATA"

MAX_RETRIES = 5
RETRY_DELAY = 3
LINE_DELAY = 0.001


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def scan_local_network(port, timeout=0.5):
    """
    Scan the local subnet (192.168.1.0/24) for a server listening on the given port.
    Returns the first IP that responds.
    """
    base_ip = "192.168.0."
    for i in range(2, 255):  # skip .1 (router)
        ip = base_ip + str(i)
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                print(f"[INFO] Found server at {ip}:{port}")
                return ip
        except Exception:
            continue
    return None


def send_file(host, file_path, file_name):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((host, PORT))
                print(f"[CONNECTED] Sending {file_name} (Attempt {attempt})")

                # Send filename

                name_bytes = file_name.encode("utf-8")

                s.sendall(struct.pack("I", len(name_bytes)))
                s.sendall(name_bytes)

                # Send file size

                file_size = os.path.getsize(file_path)

                s.sendall(struct.pack("Q", file_size))

                # Send the complete CSV file

                sent = 0

                with open(file_path, "rb") as f:

                    while True:

                        chunk = f.read(4096)

                        if not chunk:
                            break

                        s.sendall(chunk)

                        sent += len(chunk)

                print(f"[DONE] {file_name} ({sent} bytes)")
                return

        except Exception as e:
            print(f"[ERROR] {file_name} attempt {attempt}: {e}")
            time.sleep(RETRY_DELAY)

    print(f"[FAILED] Could not send {file_name} after {MAX_RETRIES} attempts")


def send_all_files():
    host = scan_local_network(PORT)
    if not host:
        print(f"[ERROR] Server not found on local network. Check if PC2 is running.")
        return

    files = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.csv')]
    if not files:
        print("[INFO] No CSV files found.")
        return

    for file in files:
        path = os.path.join(FOLDER_PATH, file)
        print(f"\n===== START {file} =====")
        send_file(host, path, file)
        print(f"===== END {file} =====\n")
        time.sleep(1)


# =============================
# To Run Automatically (Delete this block when manually run the following block)
# =============================

def wait_until_midnight():

    now = datetime.now()

    target = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    if now >= target:
        target += timedelta(days=1)

    seconds = (target - now).total_seconds()

    print(f"Waiting {seconds:.0f} seconds until midnight...")

    time.sleep(seconds)



# -----------------------------
# MAIN   (To run Manually)
# -----------------------------
#if __name__ == "__main__":
#    print("[INFO] Starting CSV transfer to server...")
#    send_all_files()
#    print("[INFO] All files processed.")


# -----------------------------
# MAIN   (To run Automatically)
# -----------------------------

if __name__ == "__main__":

    while True:

        wait_until_midnight()

        print("[INFO] Starting CSV transfer...")

        send_all_files()

        print("[INFO] Transfer completed.")