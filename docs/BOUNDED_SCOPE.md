# Touch Bounded Scope

Date: 2026-04-20
Release class: bounded internal technique evidence
Backend: Rust-native authority path with a local Python reference path
Compass-8 posture: `NO` under V2 section 7.2; this is not a product claim.

## Public Scope

This repo publishes four explicit bounded adopters on the touch surface:

- contact
- thermal
- vibrotactile
- proprioceptive

The contact base is frozen. Thermal, vibrotactile, and proprioceptive are carried on their own explicit branches with state and history represented inside the stream.

## Frozen Contact Base

The frozen contact branch preserves:

- contact geometry
- stroke direction
- pressure
- receptor identity
- body region

Contact branch metrics:

- `raw_contact_exact_rate = 1.0`
- `baseline_delta = 0.0`

## Independent Branches

Thermal, vibrotactile, and proprioceptive are evaluated independently. Success on one branch does not imply success on any other branch, and none of the branch results are sold as edits to the contact base.

Per-branch exactness and isolation are recorded in `proofs/artifacts/fiber_release_summary.json`.

## Explicit Non-Claims

This release does not claim:

- affective touch
- full embodied touch
- ambient thermal scene modeling
- non-`RA_II` vibrotactile semantics
- full-body kinematics
- Compass-8 product readiness

## Reproducibility

Minimal reproduction:

```bash
cargo --version
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install . build pytest
python -m pytest tests/test_touch_pack_regression.py tests/test_touch_native_optional.py tests/test_touch_fiber_branches.py -q
python scripts/generate_public_touch_artifacts.py
python -m build
```

Outputs:

- `proofs/artifacts/contact_release_summary.json`
- `proofs/artifacts/fiber_release_summary.json`
- `validation/results/fresh_clone_verification.json`
