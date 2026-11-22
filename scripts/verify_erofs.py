#!/usr/bin/env python3
"""Check that a file is a plausible EROFS image.

The EROFS superblock magic is 0xE0F5E1E2. On-disk (little-endian)
it is the byte sequence E2 E1 F5 E0 at offset 1024.
"""
import os
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_erofs.py <image>")
        return 2
    p = sys.argv[1]
    if not os.path.exists(p):
        print(f"FAIL: {p} does not exist")
        return 1
    if os.path.getsize(p) < 2_000_000:
        print(f"FAIL: {p} too small ({os.path.getsize(p)} bytes)")
        return 1
    with open(p, "rb") as fh:
        fh.seek(1024)
        magic = fh.read(4)
    # Magic on disk: E2 E1 F5 E0 (little-endian 0xE0F5E1E2)
    if magic != b"\xe2\xe1\xf5\xe0":
        print(f"FAIL: {p} no EROFS magic at 1024 (got {magic.hex()})")
        return 1
    print(f"OK: {p} looks like EROFS (magic E2E1F5E0 at 1024)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
