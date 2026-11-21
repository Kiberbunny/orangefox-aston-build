#!/usr/bin/env python3
"""Stage proprietary blobs (from extracted vendor/odm images) into the
OrangeFox device tree as configured in config/*.json of the device tree."""
import argparse
import json
import os
import shutil
import sys


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--vendor-dir", required=True)
    p.add_argument("--odm-dir", required=True)
    p.add_argument("--tree", required=True, help="path to device tree (device/oneplus/astonc)")
    return p.parse_args()


def load_configs(tree):
    cfg_dir = os.path.join(tree, "config")
    out = []
    for name in ("crypto-recovery-assets.json", "recovery-assets.json"):
        path = os.path.join(cfg_dir, name)
        if not os.path.exists(path):
            print(f"[warn] config {name} not found, skip")
            continue
        with open(path) as fh:
            data = json.load(fh)
        out.extend(data.get("assets", []))
    return out


def main():
    args = parse_args()
    assets = load_configs(args.tree)
    missing = []
    staged = 0
    for a in assets:
        src = a.get("source", "")
        dst = a.get("destination", "")
        mode = a.get("mode", "0644")
        if not src or not dst:
            continue
        # source paths are absolute inside the vendor filesystem (/vendor/...)
        rel = src[len("/vendor/"):] if src.startswith("/vendor/") else src
        base = args.vendor_dir
        s = os.path.join(base, rel)
        if not os.path.exists(s):
            missing.append(src)
            continue
        d = os.path.join(args.tree, "recovery", "root", dst)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        os.chmod(d, int(mode, 8))
        staged += 1
        print(f"[+] {dst} ({mode})")
    print(f"\nstaged: {staged}, missing: {len(missing)}")
    for m in missing:
        print("  MISSING:", m)
    # soft-fail: warn but allow build attempt; set env for reporting
    if missing:
        print("WARN some blobs missing; build may still be attempted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
