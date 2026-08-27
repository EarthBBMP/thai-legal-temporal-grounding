"""Reduce the collection timestamps in raw/*.json to a UTC date.

collect.py stamps each response with local wall-clock time and a UTC offset,
e.g. "2026-08-27T02:51:17+0700". Published as-is that pins the collector to a
timezone and to the hour they were working. The date is all the reproduction
record needs, so this converts to UTC and keeps the date.

Only the `timestamp` field changes. Every other field, `raw_response` included,
is checked for equality before the file is written back.

    python src/anonymise_timestamps.py --dry-run
    python src/anonymise_timestamps.py
"""

import argparse
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"

FULL = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4}$")
DATE_ONLY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def to_utc_date(stamp):
    """'2026-08-27T02:51:17+0700' -> '2026-08-26'. None if already reduced."""
    if DATE_ONLY.match(stamp):
        return None
    if not FULL.match(stamp):
        raise ValueError(f"unrecognised timestamp: {stamp!r}")
    dt = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S%z")
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    changed = skipped = 0
    for f in sorted(RAW.glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        new = to_utc_date(rec["timestamp"])
        if new is None:
            skipped += 1
            continue

        before = {k: v for k, v in rec.items() if k != "timestamp"}
        rec["timestamp"] = new
        if before != {k: v for k, v in rec.items() if k != "timestamp"}:
            sys.exit(f"aborted: {f.name} changed outside the timestamp field")

        if not args.dry_run:
            f.write_text(json.dumps(rec, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        changed += 1

    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"{verb} {changed} files, {skipped} already reduced")


if __name__ == "__main__":
    main()
