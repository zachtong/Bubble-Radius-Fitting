#!/usr/bin/env python3
"""Generate SHA256 checksums for distribution files."""
import hashlib
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    dist_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("bubbletrack/dist_onefile")
    if not dist_dir.exists():
        print(f"Directory not found: {dist_dir}", file=sys.stderr)
        sys.exit(1)
    for f in sorted(dist_dir.iterdir()):
        if f.is_file():
            print(f"{sha256_file(f)}  {f.name}")


if __name__ == "__main__":
    main()
