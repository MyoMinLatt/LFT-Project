from pathlib import Path
import struct
from datetime import datetime, UTC

file = Path(r"G:\20260713 - 복사본.cld")

with open(file, "rb") as f:

    for i in range(100):

        record = f.read(16)

        if len(record) < 16:
            break

        sensor, timestamp, zero, value = struct.unpack("<IIIf", record)

        dt = datetime.fromtimestamp(timestamp, UTC)

        print(
            f"{i:3d} | "
            f"Sensor={sensor:2d} | "
            f"{dt} | "
            f"Zero={zero} | "
            f"Value={value}"
        )