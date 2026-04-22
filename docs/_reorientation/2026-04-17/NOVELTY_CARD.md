# ZPE-Touch Novelty Card

**Product:** ZPE-Touch
**Domain:** Deterministic encoding of bounded touch contact-stroke geometry with three separate typed side-channel fiber branches (thermal, vibrotactile, proprioceptive).
**What we sell:** A lossless wire format for bounded touch events that preserves a frozen contact-stroke base alongside typed side-channel fibers, enabling decoder-side branch selection without stream corruption.

## Novel contributions

1. **Frozen contact-stroke base with three typed fiber branches.** A deterministic codec in which a touch contact stream is carried as a frozen base object (receptor identity, body region, 8-direction stroke geometry, pressure profile) and thermal, vibrotactile, and proprioceptive information attach as three explicit typed side-channel fiber branches on that same base, rather than being interleaved into a unified tactile stream. The base-preservation-plus-typed-side-channel architecture as the productised tactile codec surface is the novel contribution. Code: `src/lib.rs:35-80` (payload structs), `src/lib.rs:357-370` (contact base packing), `src/lib.rs:464-510` (thermal and vibrotactile fiber encoding). Nearest prior art: general biosignal multiplexing; no prior art known for typed-fiber attachment to a frozen tactile contact base in a compact word-stream format.

2. **Cross-fiber collision and wrong-decoder discipline.** An explicit cross-fiber collision contract and wrong-decoder rejection surface maintained at zero on the bounded released surface, with deterministic behaviour when a side-channel fiber is absent, corrupted, or incompatible with the current base stream. Each fiber branch version-tags its words (`FIBER_VERSION`, `VIBRO_VERSION`) and the decoder rejects structurally wrong words rather than silently degrading. The zero-cross-fiber-collision discipline coupled to the typed-fiber architecture is the novel contribution. Code: `src/lib.rs:157-163` (`is_tagged_word` contract), `src/lib.rs:470-478` (thermal reject path), `src/lib.rs:491-510` (vibrotactile reject path), `src/lib.rs:524-560` (proprioceptive reject path).

## Standard techniques used (explicit, not novel)

- 3-bit direction encoding (0–7) for contact-stroke direction steps on a body-region grid; this is a geometric stroke primitive, not Compass-8 signal tokenisation.
- Co-packed pressure nibble alongside direction in a single step word (`src/lib.rs:114-117`).
- Version field in extension-word header for forward compatibility.
- Linear frame-scan decode with ignored-word counting.

## Compass-8 / 8-primitive architecture

**NO** — ZPE-Touch does not use the Compass-8 signal-tokenisation pattern (8-directional Freeman-chain-code encoding with magnitude and run-length channels). The codec uses an 8-element direction alphabet (`src/lib.rs:18`, `src/lib.rs:105-117`) solely to encode the spatial direction of each contact-stroke step on a body-region contact grid. There is no magnitude channel, no run-length channel, and no delta-quantised signal lattice. The 8 directions are a geometry primitive for describing where a finger moves, not a signal-compression mechanism. The LICENSE §7.16 Compass-8 NO declaration is consistent with the code.

## Open novelty questions for the license agent

- None. The two novel contributions are internally consistent with the LICENSE §7.16 novelty schedule. Compass-8 classification is confirmed NO by code inspection.
