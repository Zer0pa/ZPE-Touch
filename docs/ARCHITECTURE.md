# Architecture

`zpe-touch` ships as a mixed Rust/Python repo.

## Runtime Map

- `src/lib.rs`: native authority path for contact, thermal, vibrotactile, and proprioceptive words
- `python/zpe_touch/codec.py`: public Python surface and native fallback loader
- `python/zpe_touch/pack.py`: local Python reference path for the frozen contact branch and bounded z-layer utilities
- `python/zpe_touch/imc.py`: touch-only IMC shim used by the local regression checks

## Authority Rules

- Contact is frozen.
- Thermal, vibrotactile, and proprioceptive are separate bounded adopters.
- State and history remain explicit inside each fiber branch.
- Wrong-decoder success is a failure condition.

## Verification Map

- `tests/test_touch_pack_regression.py` checks the frozen contact branch
- `tests/test_touch_native_optional.py` checks native parity against the local reference path
- `tests/test_touch_fiber_branches.py` checks thermal, vibrotactile, and proprioceptive isolation
- `scripts/generate_contact_release_summary.py` writes the contact release summary
- `scripts/generate_fiber_release_summary.py` writes the branch release summary
- `scripts/generate_public_touch_artifacts.py` writes the committed proof and validation JSON files
