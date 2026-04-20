# Geogram 5 L6 Touch Final Report

Date: 2026-04-20  
Lane: `L6`  
Status: final

## Claim Class

`geometry-decomposable but not yet stroke-decomposable`

The contact base remains the Geogram 3 stroke codec. The Geogram 5 extension that passed is a typed bundle branch over that base, not a claim that all richer touch semantics collapse into the original contact-stroke basis by themselves.

## Frozen Scope

Frozen base:

- Geogram 3 bounded contact geometry
- receptor identity
- body region
- pressure profile

Tested fibers, each on its own independent authority branch:

- thermal: per-direction thermal delta plus adaptation ledger aligned to the frozen contact stroke
- vibrotactile: `RA_II`-only bounded frequency/amplitude/envelope/adaptation sequence aligned to the frozen contact stroke
- proprioceptive: bounded joint-angle/tension trajectory attached to the frozen touch episode as an explicit ordered ledger

Still out of scope:

- affective touch
- full embodied-touch semantics
- ambient thermal scene modeling
- non-`RA_II` vibrotactile semantics
- full-body kinematics

## Authoritative Adopter Status

`bounded_adopter_per_fiber`

All three tested fibers clear bounded adoption on independent typed bundle branches while the legacy contact decoder continues to read the unchanged contact base.

## Authority Metrics

| Fiber | Fiber exact mean | Worst cell | Contact base preservation | Wrong-decoder collision |
| --- | --- | --- | --- | --- |
| thermal | `1.0` | `1.0` | `1.0` | `0.0` |
| vibrotactile | `1.0` | `1.0` | `1.0` | `0.0` |
| proprioceptive | `1.0` | `1.0` | `1.0` | `0.0` |

Meaning:

- the authority branch recovers the tested fiber payloads exactly
- the frozen contact base survives unchanged on the legacy decoder
- cross-fiber wrong-decoder attacks do not recover spurious bundles

## Audit-Only Proxy Metrics

These are audit-only. They do not clear the gate by themselves.

| Fiber | Bundle words | Contact words | Fiber overhead total | Fiber overhead mean |
| --- | --- | --- | --- | --- |
| thermal | `32` | `16` | `16` | `4.0` |
| vibrotactile | `44` | `16` | `28` | `7.0` |
| proprioceptive | `47` | `16` | `31` | `7.75` |

## Helper Leakage Result

Helper exactness was held as an oracle-only audit surface.

For all three fibers:

- `oracle_helper_fiber_exact_rate_mean = 1.0`
- `authority_fiber_exact_rate_mean = 1.0`
- `exact_rate_gain_helper_minus_authority = 0.0`

Meaning:

- helper access does not create the first real pass
- the decisive information is already present on the authority branch

## Worst-Cell Result

The decisive falsifiers for this lane were:

- same contact, different fiber history
- same contact, different adaptation ledger
- wrong fiber decoder on the same touch stream
- legacy contact decoder on the new bundle streams

Results:

- `same_contact_history_alias_rate = 0.0` for thermal, vibrotactile, and proprioceptive branches
- `cross_fiber_decoder_attack_success_rate = 0.0` for thermal, vibrotactile, and proprioceptive branches
- `contact_base_preservation_rate = 1.0` on every tested branch

## Direct-Baseline Delta

Direct baseline here means the frozen contact base without the candidate fiber branch.

For all three fibers:

- `direct_baseline_fiber_exact_rate_mean = 0.0`
- `authority_minus_direct_baseline = 1.0`

Meaning:

- the base codec alone still carries none of the tested fiber payloads
- the gain is coming from the new typed authority branch, not from reinterpretation theater

## What Was Attempted

I kept the contact codec frozen and added three separate Rust-native bundle families inside `zpe-touch-codec`:

- thermal frame + thermal sample words
- vibrotactile frame + paired `RA_II` descriptor words
- proprioceptive frame + ordered joint-angle/tension words

Each bundle family was required to satisfy all of:

- exact roundtrip on its own authority branch
- unchanged contact decoding on the legacy branch
- zero recovery on the wrong fiber decoder
- zero same-contact/different-history collapse

## What Failed

The contact-only direct baseline still fails completely for all three fibers.

That is the correct negative control, not a regression:

- thermal does not appear on the frozen contact branch
- vibrotactile does not appear on the frozen contact branch
- proprioceptive state does not appear on the frozen contact branch

The only implementation-level failure encountered during execution was a PyO3 interop issue where `Vec<u8>` fields surfaced as Python `bytes` instead of lists in the bundle decoders. That was fixed in the native extension output and the full test surface was rerun cleanly.

## What Was Fixed And Retested

Fixed:

- Rust bundle decoders now return Python lists for `directions` and `pressure_profile` instead of `bytes`
- local test bootstrap now injects the sibling `zpe-core` path inside `tests/common.py` so the split repo can be verified in a clean local environment

Retested:

- native module rebuild with `maturin develop`
- legacy touch tests
- new per-fiber bundle tests

Verified result:

- `7` tests passing in the canonical local environment

## Per-Fiber Verdicts

### Thermal

Verdict: `bounded_adopter`

What survived:

- per-direction thermal deltas
- explicit adaptation ledger
- same-contact/different-history separation
- unchanged frozen contact decode

What did not change:

- the underlying contact base
- the out-of-scope affective branch

### Vibrotactile

Verdict: `bounded_adopter`

What survived:

- bounded `RA_II` frequency/amplitude/envelope/adaptation descriptors
- same-contact/different-history separation
- unchanged frozen contact decode

What did not change:

- non-`RA_II` semantics remain unclaimed
- the contact base remains frozen

### Proprioceptive

Verdict: `bounded_adopter`

What survived:

- bounded ordered joint-angle/tension trajectory
- same-contact/different-history separation
- unchanged frozen contact decode

What did not change:

- no full-body kinematics claim
- the contact base remains frozen

## Frozen Non-Claims

- no affective-touch claim
- no claim that full embodied touch is now solved
- no claim that the old contact base silently “always had” these fibers
- no cross-fiber laundering claim
- no packet-of-packets claim; the passing object is one flat touch stream per tested fiber branch

## Final Verdict

The bundle hypothesis passes its `L6` test in bounded form.

Thermal, vibrotactile, and proprioceptive fibers each transition as independent bounded adopters on the authority path when carried as typed bundle words over the frozen Geogram 3 contact base, with explicit state/history ledgers and zero cross-fiber decoder collision.

This is not a full embodied-touch codec claim. It is three honest bounded scope extensions over the existing contact codec.

## Verified Scientific Learning

- For `L6`, the limiting factor was not that richer touch channels are impossible to carry on the authority path.
- The real blocker was that Geogram 3 froze contact geometry without a typed bundle surface for the non-contact fibers.
- Once the branch is made explicit and fiber-specific, the richer channels no longer need helper laundering or contact-base inflation.
- The correct `L6` object is therefore: frozen contact base plus independent typed fibers plus explicit history/adaptation ledger.

## Cross-Project Value

`L6` is now positive evidence for the Geogram 5 cross-pollination hypothesis:

- bundle objects can extend a bounded base cleanly without rewriting the base
- typed fibers can remain independent instead of laundering through one mixed side channel
- explicit history/state ledgers matter for keeping same-base cases from collapsing

This strengthens the line of sight for other strong-fit lanes, especially where the base geometry is already real but decisive higher-order structure is still helper-bound.

## Evidence Filed

Authority anchor:

- `/Users/Zer0pa/ZPE_CANONICAL/zpe-touch-codec/geogram5/artifacts/l6_touch_geogram5.json`

Executable evidence:

- `zpe-touch-codec/src/lib.rs`
- `zpe-touch-codec/tests/test_touch_fiber_bundles.py`
- `zpe-touch-codec/tests/test_touch_native_optional.py`
- `zpe-touch-codec/tests/test_touch_pack_regression.py`
- `zpe-touch-codec/scripts/generate_l6_geogram5_artifact.py`

Frozen inherited truth:

- `zpe-touch-codec/docs/L6_TOUCH_BOUNDED_RELEASE_SCOPE.md`

## Next Executable Task

The next honest step is not to widen the claim prose.

The next honest step is to decide, per transitioned fiber, whether the Orchestrator wants:

1. release-boundary preparation for bounded thermal / vibrotactile / proprioceptive scope extensions
2. tighter external falsifier pressure from `L13` FABAG-V1 against `L6-with-fibers`
3. broader nuisance coverage before any public widening beyond the bounded scopes frozen above
