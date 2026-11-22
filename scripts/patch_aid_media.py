#!/usr/bin/env python3
"""Patch OrangeFox/TWRP sources for Android 16+ where AID_MEDIA_RW was
removed from bionic (it is still 1023). Adds a fallback define to every
file under bootable/recovery that uses AID_MEDIA_RW without defining it."""
import os
import re
import sys

AID = "AID_MEDIA_RW"
FALLBACK = "#ifndef AID_MEDIA_RW\n#define AID_MEDIA_RW 1023\n#endif\n"


def patch_file(path: str) -> bool:
    with open(path, "r", errors="replace") as fh:
        src = fh.read()
    if AID not in src:
        return False
    if re.search(r"^\s*#\s*define\s+" + AID + r"\b", src, re.M):
        return False
    # insert after the last #include line (or at top otherwise)
    includes = list(re.finditer(r"^#include\b.*$", src, re.M))
    if includes:
        pos = includes[-1].end()
    else:
        pos = 0
    src = src[:pos] + "\n" + FALLBACK + src[pos:]
    with open(path, "w") as fh:
        fh.write(src)
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: patch_aid_media.py <recovery_dir>")
        return 2
    root = sys.argv[1]
    patched = 0
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if fn.endswith((".cpp", ".cc", ".c", ".h")):
                p = os.path.join(dirpath, fn)
                if patch_file(p):
                    print(f"[patched] {os.path.relpath(p, root)}")
                    patched += 1
    print(f"patched files: {patched}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
