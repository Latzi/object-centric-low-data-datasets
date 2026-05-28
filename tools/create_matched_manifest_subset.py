from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text or "dataset"


def parse_input_spec(spec: str) -> Tuple[str, Path]:
    """
    Accepts either:
      dataset_name=path/to/manifest.csv
    or:
      path/to/manifest.csv

    If no dataset name is supplied, the output name is derived from the manifest filename.
    """
    if "=" in spec:
        name, path = spec.split("=", 1)
        return slugify(name), Path(path)

    path = Path(spec)
    stem = path.stem
    stem = stem.replace("_manifest", "")
    return slugify(stem), path


def stable_row_key(row: Dict[str, str]) -> str:
    """
    Gives each row a stable ordering key so sampling is reproducible even if
    Python dictionary ordering or CSV parsing details differ.
    """
    preferred_keys = [
        "sample_id",
        "image_id",
        "image_path",
        "file_name",
        "filename",
        "annotation_path",
        "label_path",
    ]

    for key in preferred_keys:
        value = row.get(key)
        if value is not None and str(value).strip() != "":
            return str(value).strip()

    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def stable_seed(base_seed: int, dataset_name: str, group_name: str = "all") -> int:
    material = f"{base_seed}:{dataset_name}:{group_name}".encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()
    return int(digest[:16], 16)


def read_manifest(path: Path) -> Tuple[List[Dict[str, str]], List[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Manifest has no header row: {path}")
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    if not rows:
        raise ValueError(f"Manifest contains no records: {path}")

    return rows, fieldnames


def allocate_stratified_counts(group_sizes: Dict[str, int], n: int) -> Dict[str, int]:
    total = sum(group_sizes.values())
    if n > total:
        raise ValueError(f"Requested n={n}, but only {total} rows are available.")

    exact = {group: n * size / total for group, size in group_sizes.items()}
    allocated = {group: int(math.floor(value)) for group, value in exact.items()}

    remaining = n - sum(allocated.values())

    # Largest remainder allocation. Tie-break by group name for determinism.
    order = sorted(
        exact.keys(),
        key=lambda group: (exact[group] - allocated[group], group),
        reverse=True,
    )

    for group in order:
        if remaining <= 0:
            break
        if allocated[group] < group_sizes[group]:
            allocated[group] += 1
            remaining -= 1

    if remaining != 0:
        raise RuntimeError("Failed to allocate stratified sample counts.")

    return allocated


def sample_rows(
    rows: List[Dict[str, str]],
    dataset_name: str,
    n: int,
    seed: int,
    split_filter: str | None,
    stratify_by_split: bool,
) -> List[Dict[str, str]]:
    rows = sorted(rows, key=stable_row_key)

    if split_filter is not None:
        rows = [
            row for row in rows
            if str(row.get("split", "")).strip().lower() == split_filter.lower()
        ]

    if not rows:
        raise ValueError(f"No rows available after split filtering: {split_filter}")

    if n > len(rows):
        raise ValueError(
            f"Requested n={n}, but only {len(rows)} rows are available "
            f"for dataset={dataset_name}, split={split_filter or 'all'}."
        )

    has_split = "split" in rows[0]

    if stratify_by_split and split_filter is None and has_split:
        groups: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        for row in rows:
            split = str(row.get("split", "")).strip() or "unspecified"
            groups[split].append(row)

        group_sizes = {split: len(group_rows) for split, group_rows in groups.items()}
        group_counts = allocate_stratified_counts(group_sizes, n)

        sampled: List[Dict[str, str]] = []

        for split in sorted(groups.keys()):
            group_rows = sorted(groups[split], key=stable_row_key)
            rng = random.Random(stable_seed(seed, dataset_name, split))
            selected = rng.sample(group_rows, group_counts[split])
            sampled.extend(selected)

        return sorted(sampled, key=stable_row_key)

    rng = random.Random(stable_seed(seed, dataset_name, split_filter or "all"))
    return sorted(rng.sample(rows, n), key=stable_row_key)


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def split_counts(rows: List[Dict[str, str]]) -> Dict[str, int]:
    if not rows or "split" not in rows[0]:
        return {}

    counts = Counter(str(row.get("split", "")).strip() or "unspecified" for row in rows)
    return dict(sorted(counts.items()))


def write_readme(
    output_dir: Path,
    seed: int,
    n: int,
    split_filter: str | None,
    stratify_by_split: bool,
    summary: List[Dict[str, object]],
) -> None:
    lines = [
        "# Matched Manifest Subsets",
        "",
        "This folder was generated by `tools/create_matched_manifest_subset.py`.",
        "",
        "The files provide deterministic matched-size manifest subsets for fixed-budget experiments.",
        "",
        "## Settings",
        "",
        f"- Seed: `{seed}`",
        f"- Records per output manifest: `{n}`",
        f"- Split filter: `{split_filter or 'all'}`",
        f"- Stratified by split: `{stratify_by_split}`",
        "",
        "## Outputs",
        "",
    ]

    for item in summary:
        lines.extend(
            [
                f"### {item['dataset']}",
                "",
                f"- Input: `{item['input']}`",
                f"- Output: `{item['output']}`",
                f"- Rows written: `{item['rows_written']}`",
                f"- SHA256: `{item['sha256']}`",
                f"- Split counts: `{item['split_counts']}`",
                "",
            ]
        )

    readme_path = output_dir / "README.md"
    readme_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Create deterministic matched-size manifest subsets from one or more "
            "public manifest CSV files."
        )
    )

    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help=(
            "Manifest CSV inputs. Use either path/to/manifest.csv or "
            "dataset_name=path/to/manifest.csv."
        ),
    )
    parser.add_argument(
        "--n",
        type=int,
        required=True,
        help="Number of records to sample per manifest after optional split filtering.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Base random seed used for deterministic sampling.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for sampled manifests.",
    )
    parser.add_argument(
        "--split",
        default=None,
        help="Optional split filter, for example train, val, or test.",
    )
    parser.add_argument(
        "--stratify-by-split",
        action="store_true",
        help=(
            "Preserve approximate split proportions when sampling from all splits. "
            "Ignored when --split is used."
        ),
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: List[Dict[str, object]] = []

    for spec in args.inputs:
        dataset_name, manifest_path = parse_input_spec(spec)
        rows, fieldnames = read_manifest(manifest_path)

        sampled = sample_rows(
            rows=rows,
            dataset_name=dataset_name,
            n=args.n,
            seed=args.seed,
            split_filter=args.split,
            stratify_by_split=args.stratify_by_split,
        )

        split_suffix = f"_{args.split}" if args.split else ""
        out_name = f"{dataset_name}_manifest{split_suffix}_n{args.n}_seed{args.seed}.csv"
        out_path = output_dir / out_name

        write_csv(out_path, sampled, fieldnames)

        item = {
            "dataset": dataset_name,
            "input": str(manifest_path),
            "output": str(out_path),
            "rows_written": len(sampled),
            "split_counts": split_counts(sampled),
            "sha256": sha256_file(out_path),
        }
        summary.append(item)

        print(f"Wrote {out_path} ({len(sampled)} rows)")

    summary_path = output_dir / "matched_manifest_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    write_readme(
        output_dir=output_dir,
        seed=args.seed,
        n=args.n,
        split_filter=args.split,
        stratify_by_split=args.stratify_by_split,
        summary=summary,
    )

    print("")
    print(f"Summary written to {summary_path}")
    print(f"README written to {output_dir / 'README.md'}")


if __name__ == "__main__":
    main()
