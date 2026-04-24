# Reproducibility

## Canonical Inputs

This repo does not ship an external corpus. The canonical deterministic inputs for the public verification surface live in the committed regression suite and artifact-generation entrypoint:

- `tests/test_touch_pack_regression.py`
- `tests/test_touch_native_optional.py`
- `tests/test_touch_fiber_branches.py`
- `scripts/generate_public_touch_artifacts.py`

## Golden-Bundle Hash

This field will be populated by the `receipt-bundle.yml` workflow in Wave 3.

## Verification Command

```bash
cargo --version
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install . pytest
python -m pytest tests/test_touch_pack_regression.py tests/test_touch_native_optional.py tests/test_touch_fiber_branches.py -q
python scripts/generate_public_touch_artifacts.py
```

## Supported Runtimes

- Python 3.11+ via the root `pyproject.toml`
- Rust toolchain required by the root `Cargo.toml` / `maturin` build backend
- Public verification path: local Python install plus the bounded touch regression commands above
