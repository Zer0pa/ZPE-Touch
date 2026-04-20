# L6 Touch Bounded Release Scope

Date: 2026-04-20
Lane: `L6`
Release class: bounded adopter
Backend: Rust authoritative path with Python regression fallback

## Honest Claim

This release ships the touch codec only for bounded contact geometry on the live authoritative path.

The release claim is:

- exact preservation of contact-trace geometry
- exact preservation of direction, pressure, and receptor/body-region identity within the frozen contact lane
- explicit non-closure for richer embodied side channels

This is not a full embodied-touch codec release.

## Authoritative Backend

- Rust crate: `v0.0/code/rust/zpe_touch_codec`
- Live wrapper: `v0.0/code/zpe_multimodal/touch/codec.py`
- Source mirror wrapper: `v0.0/code/source/touch/codec.py`

When the native module is installed, the authoritative packing and unpacking path is executed in Rust. The prior Python implementation remains only as a regression reference and operational fallback.

## Bounded Pass Surface

Retained on the authoritative path:

- contact geometry
- stroke direction
- pressure
- receptor subtype / coarse region tags already present on the bounded path

Machine-validated authority metrics:

- `raw_contact_exact_rate = 1.0`
- `raw_direction_exact_rate = 1.0`
- `raw_pressure_exact_rate = 1.0`
- `raw_receptor_region_exact_rate = 1.0`
- `baseline_delta = 0.0`

## Explicit Non-Claims

This release does not claim authoritative preservation of:

- thermal deltas
- vibrotactile/RA-II descriptor detail beyond the bounded path
- timing deltas
- anchor offsets
- proprioception
- full embodied-touch semantics

Those payload classes remain helper-decodable but non-sovereign on the authoritative path:

- `helper_sidechannel_recovery_rate = 1.0`
- `authority_sidechannel_retention_rate = 0.0`

This negative is part of the release truth, not a temporary omission.

## Reproducibility Artifact

- Artifact: `v0.0/proofs/artifacts/geogram3/geogram3_native_falsifier_matrix.json`
- Native test: `v0.0/code/tests/test_touch_native_optional.py`

Minimal reproduction:

```bash
source .venv-gf/bin/activate
python -m maturin build --release --manifest-path v0.0/code/rust/zpe_touch_codec/Cargo.toml --interpreter "$(which python)" --out /tmp/geogram3-dist
python -m pip install --force-reinstall /tmp/geogram3-dist/zpe_touch_codec-*.whl
pytest v0.0/code/tests/test_touch_native_optional.py v0.0/code/tests/test_touch_pack_regression.py v0.0/code/tests_phase3/touch/test_touch_augmented.py -q
PYTHONPATH=v0.0/code python v0.0/code/scripts/geogram3_native_falsifier_matrix.py --output v0.0/proofs/artifacts/geogram3/geogram3_native_falsifier_matrix.json
```

## Release Judgement

`L6` is publishable now as a bounded contact-geometry codec with explicit sovereignty limits. Any broader touch claim would be false.
