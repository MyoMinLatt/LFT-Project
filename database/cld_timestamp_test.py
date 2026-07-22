from pathlib import Path
import struct
from datetime import datetime

file = Path(r"G:\20260713 - 복사본.cld")

offsets = [
    0,
    4096,
    65536,
    1048576,
    5242880,
    10485760,
    20971520,
    41943040,
    62914560,
]

with open(file, "rb") as f:

    for pos in offsets:

        f.seek(pos)

        record = f.read(16)

        sensor, t, zero, value = struct.unpack("<IIIf", record)

        print(f"\nOffset: {pos:,}")
        print("Sensor ID :", sensor)
        print("Raw time  :", t)

        try:
            dt = datetime.utcfromtimestamp(t)
            print("UTC time  :", dt)
        except Exception:
            print("Not a Unix timestamp")

        print("Value     :", value)