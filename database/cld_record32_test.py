from pathlib import Path

file = Path(r"G:\20260713 - 복사본.cld")

with open(file, "rb") as f:

    for i in range(10):

        record = f.read(32)

        print(f"\nRecord {i}")
        print(record.hex(" "))
