"""Core validation and merging logic for csvmerge-cli."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Table:
    """A single parsed CSV file: where it came from, its header, and its rows."""

    name: str
    header: list[str]
    rows: list[list[str]]


class HeaderMismatchError(ValueError):
    """Raised when a table's columns don't match the reference header."""


def reorder_row(row: list[str], from_header: list[str], to_header: list[str]) -> list[str]:
    """Reorder a data row from `from_header` column order to `to_header` order."""
    index = {name: i for i, name in enumerate(from_header)}
    return [row[index[name]] for name in to_header]


def merge_tables(tables: list[Table], allow_reorder: bool = False) -> tuple[list[str], list[list[str]]]:
    """Merge parsed CSV tables into a single header + row list.

    All tables must share the reference header (the first table's header),
    either in the exact same order, or — if `allow_reorder` is set — in
    any order (same set of column names). Rows from reordered tables are
    rewritten to match the reference column order. Raises
    `HeaderMismatchError` with a message naming the offending file if any
    table's columns don't match.
    """
    if not tables:
        return [], []

    reference = tables[0].header
    reference_set = set(reference)
    merged_rows: list[list[str]] = list(tables[0].rows)

    for table in tables[1:]:
        if table.header == reference:
            merged_rows.extend(table.rows)
            continue

        if allow_reorder and set(table.header) == reference_set and len(table.header) == len(reference):
            merged_rows.extend(reorder_row(row, table.header, reference) for row in table.rows)
            continue

        reason = "column order differs (use --allow-reorder to permit this)"
        if set(table.header) != reference_set:
            reason = "columns differ"
        raise HeaderMismatchError(
            f"{table.name}: header does not match {tables[0].name} ({reason}): "
            f"expected {reference}, got {table.header}"
        )

    return reference, merged_rows
