from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import List, Tuple


DEFAULT_CHECKSUM_FILES = [
    "traffic_signs/checksums/traffic_signs_sha256.txt",
    "cityscapes_pedestrian/checksums/cityscapes_pedestrian_public_sha256.txt",
    "coco_pottedplant/checksums/coco_pottedplant_public_sha256.txt",
]


CHECKSUM_LINE_RE = re.compile(r"^([a-fA-F0-9]{64})\s+(.+)$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def parse_checksum_file(path: Path) -> List[Tuple[str, str]]:
    entries: List[Tuple[str, str]] = []

    with path.open("r", encoding="utf-8-sig") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            match = CHECKSUM_LINE_RE.match(line)
            if match is None:
                raise ValueError(
                    f"Invalid checksum line in {path} at line {line_number}: {raw_line!r}"
                )

            expected_hash = match.group(1).lower()
            relative_path = match.group(2).strip()
            entries.append((expected_hash, relative_path))

    return entries


def verify_checksum_file(repo_root: Path, checksum_file: Path) -> Tuple[int, int, int]:
    checksum_path = repo_root / checksum_file

    if not checksum_path.exists():
        print(f"[MISSING CHECKSUM FILE] {checksum_file}")
        return 0, 0, 1

    print(f"\nVerifying {checksum_file}")

    entries = parse_checksum_file(checksum_path)

    ok_count = 0
    missing_count = 0
    mismatch_count = 0

    for expected_hash, relative_path in entries:
        target_path = repo_root / relative_path

        if not target_path.exists():
            print(f"  [MISSING] {relative_path}")
            missing_count += 1
            continue

        actual_hash = sha256_file(target_path)

        if actual_hash != expected_hash:
            print(f"  [MISMATCH] {relative_path}")
            print(f"    expected: {expected_hash}")
            print(f"    actual:   {actual_hash}")
            mismatch_count += 1
            continue

        ok_count += 1

    print(
        f"  OK: {ok_count} | missing: {missing_count} | mismatched: {mismatch_count}"
    )

    return ok_count, missing_count, mismatch_count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify SHA256 checksum files for the public release artifacts."
    )

    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root. Defaults to the parent directory of this script.",
    )

    parser.add_argument(
        "--checksum-files",
        nargs="*",
        default=DEFAULT_CHECKSUM_FILES,
        help="Checksum files to verify, relative to the repository root.",
    )

    args = parser.parse_args()

    if args.repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]
    else:
        repo_root = Path(args.repo_root).resolve()

    if not repo_root.exists():
        print(f"Repository root does not exist: {repo_root}")
        return 2

    total_ok = 0
    total_missing = 0
    total_mismatch = 0

    for checksum_file in args.checksum_files:
        ok_count, missing_count, mismatch_count = verify_checksum_file(
            repo_root=repo_root,
            checksum_file=Path(checksum_file),
        )

        total_ok += ok_count
        total_missing += missing_count
        total_mismatch += mismatch_count

    print("\nSummary")
    print("=======")
    print(f"OK files:          {total_ok}")
    print(f"Missing files:     {total_missing}")
    print(f"Mismatched files:  {total_mismatch}")

    if total_missing > 0 or total_mismatch > 0:
        print("\nChecksum verification FAILED.")
        return 1

    print("\nChecksum verification PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
