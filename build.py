#!/usr/bin/env python3
"""Build helper for The Sunday Ledger v2 (news-image-20261122, R2 revision).

Regenerates entry.png with draw.py when it is missing. The poster is drawn
offline with Pillow (deterministic: fixed compile time, no clock reads, no
network), so a committed entry.png is normally reused as-is.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "entry.png")
DRAW = os.path.join(HERE, "draw.py")


def main():
    """Draw entry.png only when it is missing; never overwrite a good render."""
    if os.path.exists(PNG):
        print("entry.png already exists; nothing to do.")
        return 0
    print("entry.png missing; drawing it with draw.py ...")
    subprocess.run([sys.executable, DRAW], check=True, cwd=HERE)
    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
