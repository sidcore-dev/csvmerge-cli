# csvmerge-cli

A small, dependency-free command-line tool that concatenates multiple CSV
files sharing the same columns into a single output CSV.

## Why

Splitting data into per-day, per-region, or per-export CSV files is
common, but stitching them back together safely — checking that every
file actually has the same columns before you concatenate — is easy to
get wrong by hand. `csvmerge-cli` validates headers first and refuses to
silently mash together files that don't match.

## Install

```bash
pip install .
```

This installs a `csvmerge-cli` command on your PATH.

## Usage

```bash
csvmerge-cli jan.csv feb.csv mar.csv --out q1.csv
```

Given `jan.csv`:

```
id,name,amount
1,Alice,10
```

and `feb.csv`:

```
id,name,amount
2,Bob,20
```

`q1.csv` becomes:

```
id,name,amount
1,Alice,10
2,Bob,20
```

Without `--out`, the merged CSV is written to stdout, so it can be piped:

```bash
csvmerge-cli jan.csv feb.csv | wc -l
```

If a file's columns are the same set but in a different order, merging
fails by default with a clear error:

```
csvmerge-cli: error: feb.csv: header does not match jan.csv (column order
differs (use --allow-reorder to permit this)): expected ['id', 'name',
'amount'], got ['name', 'id', 'amount']
```

Pass `--allow-reorder` to permit this — rows from reordered files are
rewritten to match the first file's column order:

```bash
csvmerge-cli jan.csv feb.csv --allow-reorder --out q1.csv
```

If a file's columns are genuinely different (missing or extra columns),
merging fails regardless of `--allow-reorder`.

### Options

| Flag               | Description                                                    |
|---------------------|------------------------------------------------------------------|
| `--allow-reorder`   | Allow files whose columns are the same set but in a different order |
| `--out PATH`        | Output file path (default: stdout)                              |

### Exit codes

- `0` — merge succeeded
- `1` — a file's header didn't match
- `2` — a file couldn't be read or the output couldn't be written

## Development

```bash
pip install -e .
python -m unittest discover -s tests -v
```

## License

All rights reserved. This code is public for viewing and reference only —
no license is granted to use, copy, modify, or redistribute it. See
[LICENSE](LICENSE) for details.
