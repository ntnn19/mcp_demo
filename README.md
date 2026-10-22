# MAPKAPK3 Findings Summary App

A minimal Python app that turns gene research findings (collected from Open
Targets, STRING and RCSB PDB) into three summary figures.

## Purpose

Given a `data/findings.json` file with disease associations, interaction
partners and structure metadata for a gene, this app renders:

- `diseases.png` – horizontal bar chart of top disease association scores.
- `interactions.png` – star network of the gene and its interaction partners.
- `structures.png` – two panels: entries per experimental method and a
  resolution histogram.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m app.summarize --input data/findings.json --out figures/
```

This writes the three PNG files into `figures/`.

## Test

```bash
pytest -q
```

The smoke test runs the CLI on `data/findings.json` into a temporary directory
and asserts the three PNGs exist and are non-empty.
