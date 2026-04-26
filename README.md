# zpe-touch

[![License: SAL v7.0](https://img.shields.io/badge/license-SAL%20v7.0-e5e7eb?labelColor=111111)](LICENSE)

## What This Is

`zpe-touch` is a bounded touch stream codec. It encodes contact geometry, receptor identity, body region, and pressure on a frozen base, and carries thermal, vibrotactile, and proprioceptive payloads on explicit independent branches. Each branch roundtrips exactly; a contact-only decoder recovers none of the fiber payload. That isolation is the core property this repo proves.

Touch is one lane in the Zer0pa 17-lane ZPE codec portfolio, each lane an independent encoding product for its own signal domain. Useful now, improving continuously.

The public scope is narrow by design: contact remains explicit, each fiber branch stays independent, and affective touch is out of scope. This repo ships technique evidence and CI-anchored proof artifacts, not a product-readiness claim. Compass-8 posture (V2 §7.2): `NO` — the internal technique evidence here is implementation, not a Compass-8 product claim.

## Key Metrics

| Metric | Value | Baseline | Source |
|---|---|---|---|
| CONTACT_BASE_PRESERVATION | 1.0 | legacy contact decoder | `proofs/artifacts/contact_release_summary.json` |
| THERMAL_EXACT | 1.0 | contact-only decoder (0.0) | `proofs/artifacts/fiber_release_summary.json` |
| VIBROTACTILE_EXACT | 1.0 | contact-only decoder (0.0) | `proofs/artifacts/fiber_release_summary.json` |
| PROPRIOCEPTIVE_EXACT | 1.0 | contact-only decoder (0.0) | `proofs/artifacts/fiber_release_summary.json` |
| WRONG_DECODER_COLLISION | 0.0 | — | `proofs/artifacts/fiber_release_summary.json` |
| SAME_CONTACT_HISTORY_ALIAS | 0.0 | — | `proofs/artifacts/fiber_release_summary.json` |

The decisive baseline comparison is `branch_minus_contact_only = 1.0` for all three fiber types: a contact-only decoder recovers 0.0 of the fiber payload; the branch decoder recovers 1.0. That gap is what "exact on an independent bounded branch" means in practice.

**Branch word overhead** (proof-audited, not a gate metric): thermal +4.0 words/stroke; vibrotactile +7.0 words/stroke; proprioceptive +7.75 words/stroke over the frozen contact base (16 contact words per 4-stroke batch). Source: `proofs/artifacts/fiber_release_summary.json` overhead block.

## What We Prove

- The frozen contact branch preserves contact geometry, receptor identity, body region, and pressure exactly on the shipped bounded surface. Proof: `proofs/artifacts/contact_release_summary.json`. Test: `tests/test_touch_pack_regression.py`.
- Thermal payloads roundtrip exactly on an explicit bounded branch with state and history carried in the stream. A contact-only decoder recovers 0.0 of this payload; the thermal branch decoder recovers 1.0. Proof: `proofs/artifacts/fiber_release_summary.json` (`thermal.contact_only_delta`). Test: `tests/test_touch_fiber_branches.py::test_thermal_branch_roundtrip_preserves_contact_and_history`.
- Vibrotactile payloads roundtrip exactly on an explicit bounded `RA_II` branch with state and history carried in the stream. Same contact-only gap: 0.0 vs 1.0. Proof: `proofs/artifacts/fiber_release_summary.json` (`vibrotactile.contact_only_delta`). Test: `tests/test_touch_fiber_branches.py::test_vibrotactile_branch_roundtrip_is_independent_of_contact_base`.
- Proprioceptive payloads roundtrip exactly on an explicit bounded joint-angle and tension branch with ordered history carried in the stream. Same contact-only gap: 0.0 vs 1.0. Proof: `proofs/artifacts/fiber_release_summary.json` (`proprioceptive.contact_only_delta`). Test: `tests/test_touch_fiber_branches.py::test_proprioceptive_branch_roundtrip_preserves_joint_trajectory`.
- Cross-fiber wrong-decoder collisions stay at zero across thermal, vibrotactile, and proprioceptive validation (`wrong_decoder_collision_rate = 0.0` for all three). Proof: `proofs/artifacts/fiber_release_summary.json` isolation block.
- Same-contact/different-history cases do not alias (`same_contact_history_alias_rate = 0.0` for all three fiber types). Proof: `proofs/artifacts/fiber_release_summary.json` isolation block.
- Native Rust backend word output and decode metadata match the local Python reference path exactly. Proof: `proofs/artifacts/contact_release_summary.json` (`evidence` block). Test: `tests/test_touch_native_optional.py::test_touch_native_matches_python_reference_words_and_decode`.

## What We Don't Claim

- Affective touch.
- Full embodied touch.
- Ambient thermal scene modeling.
- Non-`RA_II` vibrotactile semantics.
- Full-body kinematics.
- Silent recovery of thermal, vibrotactile, or proprioceptive data from contact-only words.
- Compass-8 product readiness or any public product claim.
- Comparative benchmarks against external touch codecs. No named external baseline exists for this scope.

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

## Upcoming Workstreams

This section captures the active lane priorities — what the next agent or contributor picks up, and what investors should expect. Cadence is continuous, not milestoned.

- **Deployable haptic stream API** — Active Engineering. Build Python+Rust API wrapping the existing branch-isolation primitives (contact base + thermal / vibrotactile / proprioceptive fiber branches). Foundation is mature; this is the lane's transition from frozen-scope research artifact to product-shaped component. Compass-8 NO posture preserved.
