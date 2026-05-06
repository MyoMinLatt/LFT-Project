import socket
import os

HOST = '192.168.10.1'   # ✅ PC2 IP
PORT = 5000

FOLDER_PATH = r'D:\Data'


def send_all_files():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        for file_name in os.listdir(FOLDER_PATH):
            if file_name.endswith('.csv'):
                full_path = os.path.join(FOLDER_PATH, file_name)

                print(f"Sending: {file_name}")

                with open(full_path, 'r') as f:
                    for line in f:
                        message = f"{file_name},{line.strip()}\n"
                        s.sendall(message.encode())

        print("All files sent!")


if __name__ == "__main__":
    send_all_files()