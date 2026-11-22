#!/usr/bin/env python3
"""Remove Android.bp module blocks that reference the unrecognized
'csuite_test' module type, without touching anything else.

Usage: strip_csuite.py <dir> [<dir> ...]"""
import os
import sys


def split_blocks(lines):
    """Yield (start_idx, end_idx) of each top-level brace block."""
    blocks = []
    depth = 0
    start = None
    for i, line in enumerate(lines):
        opens = line.count("{")
        closes = line.count("}")
        if depth == 0 and opens:
            start = i
        depth += opens - closes
        if depth <= 0 and start is not None:
            blocks.append((start, i + 1))
            start = None
            depth = 0
    return blocks


def strip_file(path: str) -> bool:
    with open(path, "r", errors="replace") as fh:
        lines = fh.readlines()
    blocks = split_blocks(lines)
    remove = set()
    for s, e in blocks:
        body = "".join(lines[s:e])
        if "csuite_test" in body:
            remove.update(range(s, e))
    if not remove:
        return False
    out = [line for i, line in enumerate(lines) if i not in remove]
    with open(path, "w") as fh:
        fh.writelines(out)
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: strip_csuite.py <dir> ...")
        return 2
    total = 0
    for root in sys.argv[1:]:
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if fn.endswith(".bp") or fn == "Android.bp":
                    p = os.path.join(dirpath, fn)
                    if strip_file(p):
                        print(f"[stripped] {os.path.relpath(p, root)}")
                        total += 1
    print(f"stripped files: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
