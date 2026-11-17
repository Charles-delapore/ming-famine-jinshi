# Contributing

## Environment

- Python 3.9+; the CI matrix runs 3.12 and 3.13.
- Install the analysis stack with `uv pip install -r requirements-analysis.txt`.
- The test suite needs `numpy pandas scipy scikit-learn statsmodels pytest pyyaml ruff`.

## Before opening a pull request

```bash
python tools/check_public_tree.py   # absolute paths, process language, private data
ruff check .
pytest -q
```

All three must pass. The same checks run in `.github/workflows/checks.yml`.

## Data policy

- Never commit raw CBDB, famine event tables, person-level links or unlicensed
  external data.
- Only aggregate tables belong in `data/derived/`; see
  [`data/derived/README.md`](data/derived/README.md) and
  [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md).
- If a result needs a private input, document the input and the reproduction
  command, and keep the file outside the repository.

## Code style

- Keep scripts runnable from the repository root.
- Use environment variables for private paths (`MING_*`); never hard-code a
  machine path.
- Add a test for new analysis helpers when the logic is non-trivial.
- Update `CHANGELOG.md` for user-visible changes.

## Reporting data errors

Open an issue with the cell, the value, the source and the expected value.
Corrections to published aggregates are versioned in `CHANGELOG.md`.
