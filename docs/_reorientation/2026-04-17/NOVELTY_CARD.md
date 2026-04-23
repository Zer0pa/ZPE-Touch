# ZPE-Touch Novelty Card

**Product:** ZPE-Touch
**Domain:** Deterministic bounded touch encoding with an intact contact-stream base and explicit thermal, vibrotactile, and proprioceptive side branches.
**What we sell:** Exact bounded replay of contact structure with independent typed side branches for operational tactile pipelines that need auditable branch separation.

## Novel contributions

1. **Frozen contact-stroke base with three typed fiber branches** — The product keeps contact as the frozen base object and attaches thermal, vibrotactile, and proprioceptive information as three explicit typed branches rather than mixing them into one undifferentiated stream. `python/zpe_touch/pack.py` and `python/zpe_touch/codec.py` preserve the contact base separately from the branch payloads, and `tests/test_touch_fiber_branches.py` verifies that each branch round-trips while preserving the same contact signature. The novel contribution is the base-preservation-plus-typed-branch contract itself.

2. **Cross-fiber collision and wrong-decoder discipline** — Wrong-decoder collisions stay at zero on the bounded released surface, and absent or incompatible side branches decode deterministically rather than leaking across branch boundaries. `tests/test_touch_fiber_branches.py` explicitly checks that thermal words do not decode as vibrotactile or proprioceptive payloads, and vice versa. The novel contribution is the zero-cross-fiber-collision discipline coupled to the typed-branch architecture.

## Standard techniques used (explicit, not novel)

- Fixed-width bit packing for bounded contact and branch words
- Finite-enum field packing for receptor, region, direction, and branch values
- Explicit side-channel control words
- Rust/Python parity verification and pytest regression testing

## Compass-8 / 8-primitive architecture

NO (at product-claim level). LICENSE §7.16 remains authoritative.

The codec uses an 8-direction stroke field internally for body-region contact representation. This is an implementation technique, not a Compass-8 Pattern per LICENSE §1.8, because the public novelty claim here is the frozen contact base plus typed thermal, vibrotactile, and proprioceptive branches rather than a directional magnitude/run-length architecture. The internal direction field is visible in `python/zpe_touch/types.py`, `python/zpe_touch/pack.py`, and `src/lib.rs`, but it is not the Novel Contribution of this product.

## Open novelty questions for the license agent

- None in this pass.
