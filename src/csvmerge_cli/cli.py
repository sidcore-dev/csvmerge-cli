"""Command-line entry point for csvmerge-cli."""
from __future__ import annotations

import argparse
import csv
import sys

from .core import HeaderMismatchError, Table, merge_tables


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvmerge-cli",
        description="Concatenate multiple CSV files that share the same columns into one output CSV.",
    )
    parser.add_argument("files", nargs="+", help="CSV files to merge")
    parser.add_argument(
        "--allow-reorder",
        action="store_true",
        help="Allow files whose columns are the same set but in a different order",
    )
    parser.add_argument("--out", default=None, help="Output file path (default: stdout)")
    return parser


def _load_table(path: str) -> Table:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        return Table(name=path, header=[], rows=[])
    return Table(name=path, header=rows[0], rows=rows[1:])


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    tables: list[Table] = []
    for path in args.files:
        try:
            tables.append(_load_table(path))
        except OSError as exc:
            print(f"csvmerge-cli: error: could not read {path}: {exc}", file=sys.stderr)
            return 2

    try:
        header, rows = merge_tables(tables, allow_reorder=args.allow_reorder)
    except HeaderMismatchError as exc:
        print(f"csvmerge-cli: error: {exc}", file=sys.stderr)
        return 1

    if args.out:
        try:
            out_fh = open(args.out, "w", encoding="utf-8", newline="")
        except OSError as exc:
            print(f"csvmerge-cli: error: could not write {args.out}: {exc}", file=sys.stderr)
            return 2
    else:
        out_fh = sys.stdout

    try:
        writer = csv.writer(out_fh)
        if header:
            writer.writerow(header)
        writer.writerows(rows)
    finally:
        if args.out:
            out_fh.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
