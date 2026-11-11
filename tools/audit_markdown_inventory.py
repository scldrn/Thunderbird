#!/usr/bin/env python3
"""Inventory source Markdown bytes and compare corresponding checkout files.

This checks content availability and hashes, not human or model comprehension.
It never changes source files and prints JSON to stdout.
"""

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def digest(path):
    # A macOS iCloud placeholder can block indefinitely while being opened.
    if getattr(path.stat(), "st_flags", 0) & 0x40000000:
        raise OSError("iCloud content is not available locally")
    data = path.read_bytes()
    data.decode("utf-8")
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original research tree")
    parser.add_argument("checkout", type=Path, help="Current research tree")
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    checkout = args.checkout.resolve(strict=True)
    records = []
    groups = Counter()
    for path in sorted(source.rglob("*.md")):
        relative = path.relative_to(source)
        groups[relative.parts[0] if len(relative.parts) > 1 else "(root)"] += 1
        record = {"path": relative.as_posix()}
        try:
            record["source"] = digest(path)
        except (OSError, UnicodeError) as error:
            record["source_error"] = str(error)
        peer = checkout / relative
        if not peer.is_file():
            record["comparison"] = "missing"
        else:
            try:
                record["checkout"] = digest(peer)
                if "source" not in record:
                    record["comparison"] = "source_unreadable"
                elif record["source"]["sha256"] == record["checkout"]["sha256"]:
                    record["comparison"] = "identical"
                else:
                    record["comparison"] = "different"
            except (OSError, UnicodeError) as error:
                record["comparison"] = "checkout_unreadable"
                record["checkout_error"] = str(error)
        records.append(record)
    output = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "checkout": str(checkout),
        "scope": "Source *.md files; byte reading, UTF-8 decoding and SHA-256 only",
        "groups": dict(sorted(groups.items())),
        "comparison": dict(sorted(Counter(r["comparison"] for r in records).items())),
        "source_read_errors": sum("source_error" in r for r in records),
        "files": records,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 1 if output["source_read_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
