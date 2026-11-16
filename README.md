# API Pagination 24-Case Fixture

Supporting files for the article **API Pagination: 24 Cases for Cursor Loops, Empty Pages, and Duplicate Results**.

## Reproduce

Requires Python 3 and only the standard library:

```bash
python3 experiment.py
```

The script regenerates `cases.json`, `results.csv`, and `summary.json`. The two SVG files visualize the policy totals and the continuation decision flow.

## Results

| Policy | Cases | Action errors | Duplicate rows |
|---|---:|---:|---:|
| Stop on empty page | 24 | 4 | 4 |
| Blind follow | 24 | 8 | 8 |
| Cursor cycle guard | 24 | 0 | 4 |
| Cycle guard + stable-ID dedupe | 24 | 0 | 0 |

## Scope and limitations

All response sequences and IDs are constructed and deterministic. This is not a live API, provider, SDK, production, or customer-data test. The results describe only the cases encoded in this repository. The cited provider documentation is used to illustrate different pagination contracts; no provider response was requested.

**License:** Code and data in this repository are released under the MIT License. See `LICENSE`. The accompanying article is separately licensed CC BY 4.0.
