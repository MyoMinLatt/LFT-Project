from pathlib import Path
import struct
from collections import Counter

file = Path(r"G:\20260713 - 복사본.cld")

counter = Counter()

with open(file, "rb") as f:

    while True:

        record = f.read(16)

        if len(record) < 16:
            break

        value = struct.unpack("<f", record[12:16])[0]

        counter[value] += 1

print(f"Number of unique values: {len(counter)}")
print()

for value, count in counter.most_common(50):
    print(f"{value:12} : {count:,}")