from pathlib import Path

file = Path(r"G:\20260713 - 복사본.cld")

positions = [
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

    for pos in positions:

        f.seek(pos)

        print(f"\n===== Offset {pos:,} =====")

        for i in range(4):
            data = f.read(16)
            print(data.hex(" "))
            from pathlib import Path

            file = Path(r"G:\20260713 - 복사본.cld")

            size = file.stat().st_size

            print("Size:", size)

            for record_size in [16, 24, 32, 40, 48, 64, 80, 96, 128]:
                if size % record_size == 0:
                    print(f"{record_size} bytes -> {size // record_size:,} records")