#!/usr/bin/env python3
"""Compare a research tree to a checkout without following symbolic links.

Regular files with macOS dataless flags are reported instead of opened. JSON
is printed to stdout; this utility does not change either tree.
"""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

DATALESS = 0x40000000


def sha256(path):
    result = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    checkout = args.checkout.resolve(strict=True)
    paths = []
    for base, directories, files in os.walk(source, followlinks=False):
        for name in directories[:]:
            path = Path(base) / name
            if path.is_symlink():
                directories.remove(name)
                paths.append(path)
        paths.extend(Path(base) / name for name in files)

    def compare(path):
        relative = path.relative_to(source)
        peer = checkout / relative
        record = {"path": relative.as_posix()}
        try:
            if not os.path.lexists(peer):
                record["status"] = "missing"
            elif path.is_symlink():
                record["status"] = (
                    "identical_link" if peer.is_symlink()
                    and os.readlink(path) == os.readlink(peer) else "link_conflict"
                )
            elif peer.is_symlink() or not peer.is_file():
                record["status"] = "type_conflict"
            elif path.stat().st_flags & DATALESS or peer.stat().st_flags & DATALESS:
                record["status"] = "dataless_unchecked"
            else:
                record["source_sha256"] = sha256(path)
                record["checkout_sha256"] = sha256(peer)
                record["status"] = (
                    "identical" if record["source_sha256"] == record["checkout_sha256"]
                    else "different"
                )
        except OSError as error:
            record["status"] = "error"
            record["error"] = str(error)
        return record

    with ThreadPoolExecutor(max_workers=16) as executor:
        records = list(executor.map(compare, sorted(paths)))
    print(json.dumps({
        "source": str(source),
        "checkout": str(checkout),
        "scope": "Source regular files and symbolic links; no directory metadata comparison",
        "counts": dict(sorted(Counter(r["status"] for r in records).items())),
        "files": records,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
