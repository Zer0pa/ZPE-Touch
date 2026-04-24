# Reproducibility

## Canonical Inputs

This repo uses code-defined bounded fixtures rather than separate checked-in corpora.
The canonical verification inputs live in:

- `tests/test_touch_pack_regression.py` for the frozen contact fixtures
- `tests/test_touch_native_optional.py` for native-versus-reference parity fixtures
- `tests/test_touch_fiber_branches.py` for thermal, vibrotactile, and proprioceptive fixtures
- `scripts/generate_public_touch_artifacts.py` for regenerating the committed proof outputs

## Golden-Bundle Hash

Will be populated by the `receipt-bundle.yml` workflow in Wave 3.

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

- CPython 3.11+
- Rust toolchain required for the native extension build via `maturin` and `pyo3`
- Verification outputs are written to `proofs/artifacts/*.json` and `validation/results/fresh_clone_verification.json`
