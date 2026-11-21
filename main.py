#!/usr/bin/env python3
"""Entry point for the-poster-for-a-place-that-i-2-20261121-0539.

Copies the pre-rendered poster (entry.png, "AURELIA — the floating
city of glass sails") byte for byte into MAKEFUN_OUTPUT_DIR as
entry.png. Standard library only, no network, no randomness, no
clock: two runs write identical bytes.

Edge cases handled:
- MAKEFUN_OUTPUT_DIR unset -> falls back to ./output (local runs).
- Output directory missing -> created.
- Source poster missing -> clear error, non-zero exit (never writes
  a partial or empty file).
- The copy is byte-exact (shutil.copyfile), so the 1024x1024 PNG
  stays under the 1 MiB cap exactly as verified at build time.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    if not os.path.isfile(src):
        print("error: entry.png missing next to main.py", file=sys.stderr)
        return 1
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
