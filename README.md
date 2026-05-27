# ZPE-Touch

> Product-page mirror for `/encoding/ZPE-Touch/`.
> Live public repo: [Zer0pa/ZPE-Touch](https://github.com/Zer0pa/ZPE-Touch).
> GitHub Markdown cannot reproduce the website typography, CSS, JavaScript, scroll behavior, or live bento layout; this README translates the product page into GitHub-safe Markdown evidence blocks.

## 0. Install / Developer Commands

The product page is the positioning authority. This section is the only retained developer-surface material from the previous root README.

```bash
python -m pip install --upgrade pip
python -m pip install . build pytest
python -m pytest tests/test_touch_pack_regression.py tests/test_touch_native_optional.py tests/test_touch_fiber_branches.py -q
```

## Product Page Mirror

**Product-page title:** ZPE-Touch · Bounded tactile branch proof · Zer0pa

**Product-page description:** ZPE-Touch · bounded tactile branch proof · contact plus thermal / RA_II vibrotactile / proprioceptive branches pass V_01..V_03 · PyPI zpe-touch 0.1.0 has one Linux cp311 wheel · no external codec benchmark closure · SAL-7.1

### Hero Translation

> 00 · ZPE-TOUCH · TOUCH-STREAM VALIDATIONRESEARCH-READY · V_01..V_03 PASS The many dimensions of touch. Four touch streams, each independently recoverable — contact, thermal, vibrotactile, proprioceptive · ZPE-Touch · PyPI zpe-touch 0.1.0 · github.com/Zer0pa/ZPE-Touch When you hold something, your hand reports four things at once: contact pressure, surface temperature, vibration, and where the limb sits in space. Machines have always collapsed those into a single tactile stream. ZPE-Touch gives each sense its own branch and ships them together in one packet. A contact-only decoder, applied to a thermal payload, returns 0.0 — the isolation is exact, not approximate. V_01, V_02, V_03 PASS on a fresh clone.

## Positioning

| Field | Value |
| --- | --- |
| Section | encoding |
| Product route | /encoding/ZPE-Touch/ |
| Live public repository | https://github.com/Zer0pa/ZPE-Touch |
| Repo identity used here | ZPE-Touch |
| Website display identity | ZPE-Touch |
| Verdict | STAGED |
| Posture | always_in_beta |
| Headline metric | CONTACT_BASE_PRESERVATION: 1.0. ZPE-Touch canonical authority surface; useful now, improving continuously. |
| Honest blocker | Affective touch.; Full embodied touch.; Ambient thermal scene modeling. |
| Mechanics asset from product page | TOUCH.gif |

## Key Metrics

| Metric | Value | Baseline |
| --- | --- | --- |
| CONTACT_BASE_PRESERVATION | 1.0 | legacy contact decoder |
| THERMAL_EXACT | 1.0 | contact-only decoder (0.0) |
| VIBROTACTILE_EXACT | 1.0 | contact-only decoder (0.0) |
| PROPRIOCEPTIVE_EXACT | 1.0 | contact-only decoder (0.0) |

## Proof Anchors

| Path | State |
| --- | --- |
| docs/BOUNDED_SCOPE.md | VERIFIED |
| proofs/manifests/VERIFICATION_SUMMARY.md | VERIFIED |
| proofs/artifacts/contact_release_summary.json | VERIFIED |
| proofs/artifacts/fiber_release_summary.json | VERIFIED |
| validation/results/fresh_clone_verification.json | VERIFIED |

## What We Prove

- The frozen contact branch preserves contact geometry, receptor identity, body region, and pressure exactly on the shipped bounded surface.
- Thermal payloads roundtrip exactly on an explicit bounded branch with state and history carried in the stream. A contact-only decoder recovers 0.0 of this payload; the thermal branch decoder recovers 1.0.
- Vibrotactile payloads roundtrip exactly on an explicit bounded RA_II branch with state and history carried in the stream. Same contact-only gap: 0.0 vs 1.0.
- Proprioceptive payloads roundtrip exactly on an explicit bounded joint-angle and tension branch with ordered history carried in the stream. Same contact-only gap: 0.0 vs 1.0.
- Cross-fiber wrong-decoder collisions stay at zero across thermal, vibrotactile, and proprioceptive validation (wrong_decoder_collision_rate = 0.0 for all three).
- Same-contact/different-history cases do not alias (same_contact_history_alias_rate = 0.0 for all three fiber types).
- Native Rust backend word output and decode metadata match the local Python reference path exactly.

## What We Do Not Claim

- Affective touch.
- Full embodied touch.
- Ambient thermal scene modeling.
- Non-RA_II vibrotactile semantics.
- Full-body kinematics.
- Silent recovery of thermal, vibrotactile, or proprioceptive data from contact-only words.
- Compass-8 product readiness or any public product claim.
- Comparative benchmarks against external touch codecs. No named external baseline exists for this scope.

## Blockers / Failures

> Affective touch.; Full embodied touch.; Ambient thermal scene modeling.

## Verification Surface

| Code | Check | Verdict |
| --- | --- | --- |
| V_01 | Contact branch roundtrip stays exact on the local Python reference path. | PASS |
| V_02 | Native Rust backend matches the local reference contact words and decode metadata. | PASS |
| V_03 | Thermal, vibrotactile, and proprioceptive branches stay exact, isolated, and contact-preserving. | PASS |

## License

| Field | Value |
| --- | --- |
| License | SAL-7.0 |
| Authority source | proofs/manifests/VERIFICATION_SUMMARY.md |

## Upcoming Workstreams

| Category | Summary |
| --- | --- |
| Active Engineering | Deployable haptic stream API. Build Python+Rust API wrapping branch-isolation primitives (contact base + thermal / vibrotactile / proprioceptive branches). Lane's transition from frozen-scope research artifact to product-shaped component; Compass-8 NO preserved. |
| Operations / External Dependency | Maintain CI gates and license-resolver synchronization with Zer0pa/ZPE-License-Commercial. |

## Related Repos

No related repos are declared on the product page frontmatter.

<details>
<summary>Full Visible Product-Page Bento Translation</summary>

This section preserves the product page cells as Markdown text blocks. It intentionally omits shared site navigation, footer chrome, CSS, and scripts.

### Bento Cell 1

> 00 · ZPE-TOUCH · TOUCH-STREAM VALIDATIONRESEARCH-READY · V_01..V_03 PASS The many dimensions of touch. Four touch streams, each independently recoverable — contact, thermal, vibrotactile, proprioceptive · ZPE-Touch · PyPI zpe-touch 0.1.0 · github.com/Zer0pa/ZPE-Touch When you hold something, your hand reports four things at once: contact pressure, surface temperature, vibration, and where the limb sits in space. Machines have always collapsed those into a single tactile stream. ZPE-Touch gives each sense its own branch and ships them together in one packet. A contact-only decoder, applied to a thermal payload, returns 0.0 — the isolation is exact, not approximate. V_01, V_02, V_03 PASS on a fresh clone.

### Bento Cell 2

> 01 · THE GAPONE STREAM, FOUR SENSATIONS Touch carries four distinct sensations at once. No research format has kept all four separately recoverable.

### Bento Cell 3

> 02 · MARKETSADJACENT R&D DOMAINS Haptics R&D teamsbest-fit Tactile-sensing labsworkflow Robot-skin sensing R&Dcandidate Teleoperation + embodied-interaction R&Dresearch XR haptics experimentersconditional Best-fit R&D teams only. No TAM, procurement readiness, or broad tactile-codec adoption claimed.

### Bento Cell 4

> 03 · VALUE R&Dscope Four touch senses round-trip exactly. Distribution breadth and external comparators remain open.

### Bento Cell 5

> 04 · INSIGHT Touch is not one sensation. It has always been four.

### Bento Cell 6

> 05.1 · CURRENT TECHONE STREAM, NO ISOLATION Today's haptic pipelines carry contact, temperature, vibration, and limb position in one undifferentiated stream. To inspect the thermal record of a grasp, a researcher must decode the whole touch event and pull the heat back out by hand.

### Bento Cell 7

> 05.2 · OUR TECHFOUR BRANCHES, EACH EXACT ZPE-Touch gives each sense its own typed branch in the packet: contact, thermal, RA_II vibrotactile, and proprioceptive. Each branch round-trips exactly. A decoder built for contact, applied to a thermal payload, returns 0.0 — exactly zero, not an approximation. Same-contact alias rate sits at 0.0, collision rate at 0.0. The four senses do not bleed.

### Bento Cell 8

> 05.3 · BENCHMARKSDECLARED FIXTURES Contact1.0exact rate Thermal1.0exact rate Vibrotactile1.0exact rate Proprioceptive1.0exact rate V_01 PASSPASS V_02 PASSPASS V_03 PASSPASS Scope: declared fixtures only. No external tactile-codec comparator. Four-branch exactness, not field claims.

### Bento Cell 9

> 06 · MEASUREMENTBRANCH-ISOLATED VERIFICATION Each branch measured separately. V_01..V_03 PASS on a fresh clone.

### Bento Cell 10

> 06.1 · COMPARATIVE PERFORMANCE · BRANCH EXACT RATES Contact stream1.0 exact Thermal stream1.0 exact Vibrotactile stream1.0 exact Proprioceptive stream1.0 exact V_01..V_03 PASS on a fresh clone. Branch-aware decoders return the exact payload for their sense; a contact-only decoder returns 0.0 from thermal, vibrotactile, and proprioceptive payloads. Source: proofs/manifests/VERIFICATION_SUMMARY.md.

### Bento Cell 11

> 07 · KEY METRICSMEASURED RESULTS

### Bento Cell 12

> 07.1 · CONTACT 1.0 Exact rate · contact branch on fresh clone

### Bento Cell 13

> 07.2 · THERMAL 1.0 Exact rate · contact-only decoder returns 0.0

### Bento Cell 14

> 07.3 · VIBROTACTILE 1.0 Exact rate · RA_II vibrotactile branch isolated

### Bento Cell 15

> 07.4 · VERIFICATIONS 3/3 V_01..V_03 PASS · fresh clone, Rust and Python agree

### Bento Cell 16

> 07.5 · PROPRIOCEPTIVE 1.0 Exact rate · joint-angle and tension branch

### Bento Cell 17

> 08 · BRANCH ISOLATIONEXACT OR ZERO Four streams. Four branches. Apply the wrong decoder — zero recovery.

### Bento Cell 18

> 08.1 · WHAT BRANCH ISOLATION MEANSTHE PROOF On the declared validation surface — contact, thermal, RA_II vibrotactile, proprioceptive — V_01 through V_03 PASS on a fresh clone. The native Rust backend and the Python reference path produce matching output. Branch isolation is verified end to end. A contact-only decoder, applied to a thermal payload, returns 0.0 — not an approximation, exactly zero. Same-contact alias rate: 0.0. Collision rate: 0.0. The four senses are genuinely separate. The claim holds for these declared streams on declared fixtures.

### Bento Cell 19

> 08.2 · HONEST BLOCKER Honest Blocker · Scope: declared fixtures. PyPI zpe-touch 0.1.0 ships one Linux cp311-abi3 wheel — no source distribution, no macOS, no Windows. API hardening and external benchmarks remain open. Compass-8 stays outside scope. No affective touch, no full embodied touch, no ambient thermal modeling.

### Bento Cell 20

> 09 TOUCH WITH FOUR HONEST CHANNELS.

### Bento Cell 21

> 09.1 · THE AMBITION The aim is a tactile packet built from four typed senses: contact as the base, with thermal, RA_II vibrotactile, and proprioceptive histories carried alongside it and each one recoverable on its own. Getting there means closing API hardening, broader distribution, and external comparators across haptic systems that do not share a stack.

### Bento Cell 22

> 09.2 · WHAT WORKS NOW Working today: four sense-isolated branches, each round-tripping exactly, on declared validation fixtures.

### Bento Cell 23

> 09.3 · WHAT'S STILL OPEN Still open: API hardening, broader distribution, external comparators, affective and ambient-thermal touch.

### Bento Cell 24

> 09.4 · LAB FORMAT · NEAR-TERM (12–24 MO) A shared file for tactile sessions A haptics lab can hand off a session knowing the receiver sees contact, temperature, vibration, and limb position as four separate things. Reviewers pull the thermal record from one experiment without re-decoding the rest of the touch event.

### Bento Cell 25

> 09.5 · XR TRANSPORT · NEAR-TERM (12–24 MO) XR sessions carry touch as four senses An XR or teleoperation session transmits all four touch dimensions together, but a downstream tool can read just the vibration channel or just the joint trace. Design teams compare what a controller did to what a hand actually felt, side by side.

### Bento Cell 26

> 09.6 · ROBOT SKIN · MID-TERM (24–48 MO) Robot-skin archives split by sense A robotics group recording tactile sensor arrays keeps contact pressure, surface temperature, micro-vibration, and joint state as four indexable signals. A later study queries only the thermal record from a grasp without re-processing the rest of the session.

### Bento Cell 27

> 09.7 · TELEOPERATION · MID-TERM (24–48 MO) Remote touch sessions stay reviewable Surgeons, undersea operators, and remote-arm pilots end a session with a recording where each tactile sense is its own track. A second clinician or a regulator inspects the vibration channel of one moment without replaying the full embodied feed.

### Bento Cell 28

> 09.8 · TOUCH AS DATA · PARADIGM (48 MO+) Touch becomes a thing you store For the first time, a touch event lives as four parallel records you can open later — pressure here, heat there, vibration alongside, limb posture beside that. Touch enters the same regime as text, audio, and motion: storable, addressable, inspectable years after the hand moved on.

</details>

---

Source mapping: product route `/encoding/ZPE-Touch/` -> live public repo `Zer0pa/ZPE-Touch`. README generated from product-page authority plus retained install/dev commands only.
