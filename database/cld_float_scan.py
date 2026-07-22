from pathlib import Path
import struct

file = Path(r"G:\20260713 - 복사본.cld")

with open(file, "rb") as f:
    data = f.read()

count = 0

for i in range(0, len(data) - 4, 4):
    value = struct.unpack("<f", data[i:i+4])[0]

    # Show only reasonable finite values
    if -1000 < value < 1000 and value not in (0.0, 1.875):
        print(f"Offset {i:10d}: {value}")
        count += 1

        if count >= 200:
            break