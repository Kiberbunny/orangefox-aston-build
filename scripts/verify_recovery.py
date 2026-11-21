#!/usr/bin/env python3
"""Static verification of a (likely NoKernel) Android recovery image."""
import struct
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_recovery.py <recovery.img>")
        return 2
    path = sys.argv[1]
    data = open(path, "rb").read()
    if data[:8] != b"ANDROID!":
        print("FAIL: not an Android boot image (magic missing)")
        return 1
    (kernel_size, kernel_addr, ramdisk_size, ramdisk_addr,
     second_size, second_addr, tags_addr,
     page_size, header_version, os_version,
     name, cmdline) = struct.unpack("<10I16s512s", data[8:8 + 40 + 16 + 512])
    print("magic: ANDROID!")
    print("header_version:", header_version)
    print("page_size:", page_size)
    print("kernel_size:", kernel_size, "(expect 0 for NoKernel recovery)")
    print("ramdisk_size:", ramdisk_size)
    print("cmdline:", cmdline.split(b"\x00")[0].decode(errors="replace")[:80])
    first_page = 8 + 40 + 16 + 512
    ram_start = page_size * ((first_page + page_size - 1) // page_size)
    ram = data[ram_start:ram_start + ramdisk_size]
    print("ramdisk lz4:", ram[:4] == b"\x04\x22\x4d\x18")
    for needle in (b"orangefox", b"twrp", b"recovery", b"init"):
        print(f"contains {needle.decode()!r}:", needle.lower() in data.lower())
    if kernel_size != 0:
        print("WARN: kernel_size != 0; expected for NoKernel recovery tree")
    if ramdisk_size == 0:
        print("FAIL: empty ramdisk")
        return 1
    print("STATIC_VERIFY_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
