# zpe-touch

[![License: SAL v7.1](https://img.shields.io/badge/license-SAL%20v7.1-e5e7eb?labelColor=111111)](LICENSE)

## What This Is

Bounded touch-stream codec. Contact geometry and receptor fields stay isolated from thermal, vibrotactile, and proprioceptive branches.

Touch is one lane in the Zer0pa 17-lane ZPE codec portfolio, each lane an independent encoding product for its own signal domain. Useful now, improving continuously.

The public scope is narrow by design: contact remains explicit, each fiber branch stays independent, and affective touch is out of scope. This repo ships technique evidence and CI-anchored proof artifacts, not a product-readiness claim. Compass-8 posture (V2 §7.2): `NO` — the internal technique evidence here is implementation, not a Compass-8 product claim.

## Codec Mechanics

<p>
  <img src=".github/assets/readme/lane-mechanics/TOUCH.gif" alt="ZPE-Touch Codec Mechanics animation" width="100%">
</p>

| Field | Value |
| ------- | ------- |
| Architecture | TOUCH_STREAM |
| Encoding | TOUCH_FIBER_BRANCH_V1 |
| Mechanics Asset | `.github/assets/readme/lane-mechanics/TOUCH.gif` |

## Key Metrics

| Metric | Value | Baseline |
| -------- | ------- | ---------- |
| CONTACT_BASE_PRESERVATION | 1.0 | legacy contact decoder |
| THERMAL_EXACT | 1.0 | contact-only decoder (0.0) |
| VIBROTACTILE_EXACT | 1.0 | contact-only decoder (0.0) |
| PROPRIOCEPTIVE_EXACT | 1.0 | contact-only decoder (0.0) |

> Source: `proofs/manifests/VERIFICATION_SUMMARY.md`

## Repo Identity

| Field | Value |
| ------- | ------- |
| Identifier | ZPE-Touch |
| Repository | https://github.com/Zer0pa/ZPE-Touch |
| Section | encoding |
| Visibility | PUBLIC |
| Architecture | TOUCH_STREAM |
| Encoding | TOUCH_FIBER_BRANCH_V1 |
| Commit SHA | 2681f25e927d |
| License | SAL-7.1 |
| Authority Source | proofs/manifests/VERIFICATION_SUMMARY.md |

## Readiness

| Field | Value |
| ------- | ------- |
| Verdict | STAGED |
| Checks | 3/3 |
| Anchors | 5 display anchors |
| Commit | 4d26abb94786 |
| Authority | proofs/manifests/VERIFICATION_SUMMARY.md |

### Honest Blocker

Affective touch.; Full embodied touch.; Ambient thermal scene modeling.

## What We Prove

- The frozen contact branch preserves contact geometry, receptor identity, body region, and pressure exactly on the shipped bounded surface.
- Thermal payloads roundtrip exactly on an explicit bounded branch with state and history carried in the stream. A contact-only decoder recovers 0.0 of this payload; the thermal branch decoder recovers 1.0.
- Vibrotactile payloads roundtrip exactly on an explicit bounded RA_II branch with state and history carried in the stream. Same contact-only gap: 0.0 vs 1.0.
- Proprioceptive payloads roundtrip exactly on an explicit bounded joint-angle and tension branch with ordered history carried in the stream. Same contact-only gap: 0.0 vs 1.0.
- Cross-fiber wrong-decoder collisions stay at zero across thermal, vibrotactile, and proprioceptive validation (wrong_decoder_collision_rate = 0.0 for all three).
- Same-contact/different-history cases do not alias (same_contact_history_alias_rate = 0.0 for all three fiber types).
- Native Rust backend word output and decode metadata match the local Python reference path exactly.

## What We Don't Claim

- Affective touch.
- Full embodied touch.
- Ambient thermal scene modeling.
- Non-RA_II vibrotactile semantics.
- Full-body kinematics.
- Silent recovery of thermal, vibrotactile, or proprioceptive data from contact-only words.
- Compass-8 product readiness or any public product claim.
- Comparative benchmarks against external touch codecs. No named external baseline exists for this scope.

## Verification Status

| Code | Check | Verdict |
| ------ | ------- | --------- |
| V_01 | Contact branch roundtrip stays exact on the local Python reference path. | PASS |
| V_02 | Native Rust backend matches the local reference contact words and decode metadata. | PASS |
| V_03 | Thermal, vibrotactile, and proprioceptive branches stay exact, isolated, and contact-preserving. | PASS |

## Proof Anchors

| Path | State |
| ------ | ------- |
| `docs/BOUNDED_SCOPE.md` | VERIFIED |
| `proofs/manifests/VERIFICATION_SUMMARY.md` | VERIFIED |
| `proofs/artifacts/contact_release_summary.json` | VERIFIED |
| `proofs/artifacts/fiber_release_summary.json` | VERIFIED |
| `validation/results/fresh_clone_verification.json` | VERIFIED |

## Repo Shape

| Field | Value |
| ------- | ------- |
| Proof Anchors | 5 display anchors |
| Modality Lanes | 3 |
| Architecture | TOUCH_STREAM |
| Encoding | TOUCH_FIBER_BRANCH_V1 |
| Verification | 3/3 checks |
| Authority Source | proofs/manifests/VERIFICATION_SUMMARY.md |

## Extended Metrics

Rows retained from the previous expanded `## Key Metrics` table. The public product page uses the first four rows only.

| Metric | Value | Baseline | Source |
|---|---|---|---|
| WRONG_DECODER_COLLISION | 0.0 | — | `proofs/artifacts/fiber_release_summary.json` |
| SAME_CONTACT_HISTORY_ALIAS | 0.0 | — | `proofs/artifacts/fiber_release_summary.json` |

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

## Upcoming Workstreams

This section captures the active lane priorities — what the next agent or contributor picks up, and what investors should expect. Cadence is continuous, not milestoned.

- **Deployable haptic stream API** — Active Engineering. Build Python+Rust API wrapping the existing branch-isolation primitives (contact base + thermal / vibrotactile / proprioceptive fiber branches). Foundation is mature; this is the lane's transition from frozen-scope research artifact to product-shaped component. Compass-8 NO posture preserved.
