# zpe-touch

[![License: SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-e5e7eb?labelColor=111111)](LICENSE)

## What This Is

`zpe-touch` is an internal technique evidence surface for bounded touch stream encoding, not a Compass-8 product claim. It keeps the frozen contact base explicit and carries thermal, vibrotactile, and proprioceptive data on separate bounded branches.

The public scope is intentionally narrow: contact remains explicit, each added branch stays independent, and affective touch remains out of scope. Under the V2 section 7.2 Compass-8 posture, Touch is `NO`: this repo documents bounded internal technique evidence only.

## Key Metrics

| Metric | Value | Baseline |
|---|---|---|
| CONTACT_BASE_PRESERVATION | 1.0 | legacy |
| THERMAL_EXACT | 1.0 | contact-only |
| VIBROTACTILE_EXACT | 1.0 | contact-only |
| PROPRIOCEPTIVE_EXACT | 1.0 | contact-only |

> Source: `proofs/artifacts/contact_release_summary.json` and `proofs/artifacts/fiber_release_summary.json`

## What We Prove

- The frozen contact branch preserves contact geometry, receptor identity, body region, and pressure exactly on the shipped bounded surface.
- Thermal payloads roundtrip exactly on an explicit bounded branch with state and history carried in the stream.
- Vibrotactile payloads roundtrip exactly on an explicit bounded `RA_II` branch with state and history carried in the stream.
- Proprioceptive payloads roundtrip exactly on an explicit bounded joint-angle and tension branch with ordered history carried in the stream.
- Cross-fiber wrong-decoder collisions stay at zero across thermal, vibrotactile, and proprioceptive validation.

## What We Don't Claim

- Affective touch.
- Full embodied touch.
- Ambient thermal scene modeling.
- Non-`RA_II` vibrotactile semantics.
- Full-body kinematics.
- Silent recovery of thermal, vibrotactile, or proprioceptive data from contact-only words.
- Compass-8 product readiness or any public product claim.

## Tests and Verification

| Code | Check | Verdict |
|---|---|---|
| V_01 | Contact branch roundtrip stays exact on the local Python reference path. | PASS |
| V_02 | Native Rust backend matches the local reference contact words and decode metadata. | PASS |
| V_03 | Thermal, vibrotactile, and proprioceptive branches stay exact, isolated, and contact-preserving. | PASS |

## Proof Anchors

| Path | Role |
|---|---|
| `docs/BOUNDED_SCOPE.md` | Scope boundary and reproduction commands |
| `proofs/manifests/VERIFICATION_SUMMARY.md` | Verification index |
| `proofs/artifacts/contact_release_summary.json` | Contact proof artifact |
| `proofs/artifacts/fiber_release_summary.json` | Fiber proof artifact |
| `validation/results/fresh_clone_verification.json` | Fresh-clone verification result |

## Quick Start

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
