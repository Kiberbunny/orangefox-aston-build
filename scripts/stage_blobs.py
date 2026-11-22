#!/usr/bin/env python3
"""Stage proprietary blobs (from extracted vendor/odm images) into the
OrangeFox device tree as configured in config/*.json of the device tree.

Source paths in the configs may start with either "vendor/" or "/vendor/"
(and similarly for "odm/"). The actual partition placement differs between
ROMs (e.g. touch firmware may live in odm on some builds), so we fall back
to a filename search across both extracted roots.
"""
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


def split_partition(src):
    """Return (partition, relative_path) for a source path."""
    for prefix in ("/vendor/", "vendor/"):
        if src.startswith(prefix):
            return "vendor", src[len(prefix):]
    for prefix in ("/odm/", "odm/"):
        if src.startswith(prefix):
            return "odm", src[len(prefix):]
    return None, src


def find_in_roots(rel, roots):
    """Try direct path in the hinted root, then filename search everywhere."""
    hint = roots.get(rel[0])
    if hint:
        direct = os.path.join(hint, rel[1])
        if os.path.exists(direct):
            return direct
    # filename fallback across both roots
    fname = os.path.basename(rel[1])
    for base in roots.values():
        for dirpath, _dirs, files in os.walk(base):
            if fname in files:
                return os.path.join(dirpath, fname)
    return None


def main():
    args = parse_args()
    roots = {"vendor": (args.vendor_dir, True), "odm": (args.odm_dir, True)}
    assets = load_configs(args.tree)
    missing = []
    staged = 0
    for a in assets:
        src = a.get("source", "")
        dst = a.get("destination", "")
        mode = a.get("mode", "0644")
        if not src or not dst:
            continue
        part, rel = split_partition(src)
        # roots dict keyed by partition with (dir, enabled) tuples
        root_dir = roots.get(part, (None, True))[0]
        s = None
        if root_dir:
            direct = os.path.join(root_dir, rel)
            if os.path.exists(direct):
                s = direct
        if s is None:
            # fallback: search both roots by filename
            fname = os.path.basename(rel)
            for base in (args.vendor_dir, args.odm_dir):
                hit = None
                for dirpath, _dirs, files in os.walk(base):
                    if fname in files:
                        hit = os.path.join(dirpath, fname)
                        break
                if hit:
                    s = hit
                    break
        if s is None:
            missing.append(src)
            continue
        d = os.path.join(args.tree, "recovery", "root", dst.lstrip("/"))
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        os.chmod(d, int(mode, 8))
        staged += 1
        print(f"[+] {dst} ({mode}) <- {os.path.relpath(s, args.vendor_dir)}")
    print(f"\nstaged: {staged}, missing: {len(missing)}")
    for m in missing:
        print("  MISSING:", m)
    if missing:
        print("WARN some blobs missing; build may still be attempted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
