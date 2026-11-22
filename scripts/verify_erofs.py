#!/usr/bin/env python3
"""Check that a file is a plausible EROFS image (magic at offset 1024)."""
import os
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_erofs.py <image>")
        return 2
    p = sys.argv[1]
    if os.path.getsize(p) < 1_000_000:
        print(f"FAIL: {p} too small ({os.path.getsize(p)} bytes)")
        return 1
    with open(p, "rb") as fh:
        fh.seek(1024)
        magic = fh.read(4)
    if magic != b"\xe0\xf5\xe1":
        print(f"FAIL: {p} no EROFS magic at 1024 (got {magic.hex()})")
        return 1
    print(f"OK: {p} looks like EROFS (magic at 1024)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
