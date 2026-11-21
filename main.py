#!/usr/bin/env python3
"""Entry point for the-poster-for-a-place-that-i-2-20261121-0539.

Copies the pre-rendered poster (entry.png, "AURELIA — the floating
city of glass sails") byte for byte into MAKEFUN_OUTPUT_DIR as
entry.png. Standard library only, no network, no randomness, no
clock: two runs write identical bytes.

The copy is written atomically (temporary file in the output
directory, then os.replace) so a crash or interruption can never
leave a half-written entry.png behind, and the source is validated
as a real PNG (8-byte magic signature) before anything is written.

Edge cases handled:
- MAKEFUN_OUTPUT_DIR unset -> falls back to ./output (local runs).
- Output directory missing -> created.
- Source poster missing -> clear error, non-zero exit (never writes
  a partial or empty file).
- Source poster not a PNG (wrong magic bytes) -> clear error,
  non-zero exit, nothing written.
- Source poster over the 1 MiB cap -> clear error, non-zero exit,
  nothing written.
- The copy is byte-exact, so the 1024x1024 PNG stays under the
  1 MiB cap exactly as verified at build time.
"""

import os
import sys
import tempfile

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
# Bounty cap: the poster must stay under 1 MiB.
MAX_SIZE = 1048576

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    if not os.path.isfile(src):
        print("error: poster file entry.png is missing next to main.py; "
              "nothing was written", file=sys.stderr)
        return 1
    size = os.path.getsize(src)
    if size > MAX_SIZE:
        print(f"error: entry.png is {size} bytes, over the 1 MiB "
              f"({MAX_SIZE} byte) limit; nothing was written",
              file=sys.stderr)
        return 1
    with open(src, "rb") as f:
        header = f.read(len(PNG_MAGIC))
    if header != PNG_MAGIC:
        print("error: entry.png is not a valid PNG (bad magic bytes); "
              "nothing was written", file=sys.stderr)
        return 1
    dst = os.path.join(out_dir, "entry.png")
    # Atomic write: stream to a temp file in the same directory, then
    # rename over the destination in one step.
    fd, tmp_path = tempfile.mkstemp(prefix=".entry-", suffix=".png",
                                    dir=out_dir)
    try:
        os.chmod(tmp_path, 0o644)
        with os.fdopen(fd, "wb") as tmp:
            with open(src, "rb") as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    tmp.write(chunk)
        os.replace(tmp_path, dst)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
