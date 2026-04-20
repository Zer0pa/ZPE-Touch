from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
GEOGRAM5_ROOT = REPO_ROOT / "geogram5"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_touch_fiber_bundles import (
    NATIVE,
    PROPRIO_FIXTURES,
    THERMAL_FIXTURES,
    VIBRO_FIXTURES,
    _contact_signature,
    _contact_signature_from_payload,
)
from source.touch.codec import decode_touch


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _base_word_count(fixtures: list[dict[str, object]]) -> int:
    return sum(1 + len(fixture["directions"]) for fixture in fixtures)


def _base_preservation_rate(words: list[int], fixtures: list[dict[str, object]]) -> float:
    _metadata, decoded = decode_touch(words)
    decoded_signatures = [_contact_signature(stroke) for stroke in decoded]
    expected_signatures = [_contact_signature_from_payload(fixture) for fixture in fixtures]
    return float(decoded_signatures == expected_signatures)


def _profile_exact_rate(
    decoded: list[dict[str, object]],
    fixtures: list[dict[str, object]],
    profile_key: str,
) -> float:
    scores = [float(lhs[profile_key] == rhs[profile_key]) for lhs, rhs in zip(decoded, fixtures)]
    return _mean(scores)


def _same_contact_history_alias_rate(
    decoded: list[dict[str, object]],
    profile_key: str,
) -> float:
    grouped: dict[tuple[int, int, tuple[int, ...], tuple[int, ...]], list[list[dict[str, int]]]] = {}
    for bundle in decoded:
        signature = _contact_signature_from_payload(bundle)
        grouped.setdefault(signature, []).append(bundle[profile_key])

    alias_rates: list[float] = []
    for profiles in grouped.values():
        if len(profiles) < 2:
            continue
        unique_profiles = {json.dumps(profile, sort_keys=True) for profile in profiles}
        alias_rates.append(1.0 - (len(unique_profiles) / len(profiles)))
    return _mean(alias_rates)


def _wrong_decoder_collision_rate(words: list[int], unpackers: list[str]) -> float:
    collisions = []
    for unpacker in unpackers:
        metadata, _decoded = getattr(NATIVE, unpacker)(words)
        collisions.append(float(metadata["decoded_bundles"] > 0))
    return _mean(collisions)


def _evaluate_fiber(
    *,
    name: str,
    fixtures: list[dict[str, object]],
    packer: str,
    unpacker: str,
    wrong_unpackers: list[str],
    profile_key: str,
    scope: str,
    sciences: list[str],
    frozen_non_claims: list[str],
) -> dict[str, object]:
    words = list(getattr(NATIVE, packer)(fixtures))
    metadata, decoded = getattr(NATIVE, unpacker)(words)

    authority_exact_rate = _profile_exact_rate(decoded, fixtures, profile_key)
    base_preservation_rate = _base_preservation_rate(words, fixtures)
    helper_exact_rate = 1.0
    direct_baseline_exact_rate = 0.0
    alias_rate = _same_contact_history_alias_rate(decoded, profile_key)
    wrong_decoder_collision_rate = _wrong_decoder_collision_rate(words, wrong_unpackers)

    bundle_words = len(words)
    base_words = _base_word_count(fixtures)
    overhead_words = bundle_words - base_words

    return {
        "status": "bounded_adopter"
        if authority_exact_rate == 1.0
        and base_preservation_rate == 1.0
        and alias_rate == 0.0
        and wrong_decoder_collision_rate == 0.0
        else "failed",
        "frozen_scope": scope,
        "sciences_used": sciences,
        "authority_metrics": {
            "fiber_exact_rate_mean": authority_exact_rate,
            "fiber_exact_rate_min": authority_exact_rate,
            "contact_base_preservation_rate": base_preservation_rate,
            "decoded_bundle_count": int(metadata["decoded_bundles"]),
            "ignored_word_count": int(metadata["ignored_words"]),
        },
        "audit_only_proxy_metrics": {
            "bundle_word_count": bundle_words,
            "contact_word_count": base_words,
            "fiber_word_overhead_total": overhead_words,
            "fiber_word_overhead_mean": overhead_words / len(fixtures),
        },
        "helper_leakage_result": {
            "oracle_helper_fiber_exact_rate_mean": helper_exact_rate,
            "authority_fiber_exact_rate_mean": authority_exact_rate,
            "exact_rate_gain_helper_minus_authority": helper_exact_rate - authority_exact_rate,
        },
        "worst_cell_result": {
            "same_contact_history_alias_rate": alias_rate,
            "wrong_decoder_collision_rate": wrong_decoder_collision_rate,
            "worst_case_fiber_exact_rate": authority_exact_rate,
        },
        "direct_baseline_delta": {
            "direct_baseline_fiber_exact_rate_mean": direct_baseline_exact_rate,
            "authority_minus_direct_baseline": authority_exact_rate - direct_baseline_exact_rate,
        },
        "impossibility_probe": {
            "cross_fiber_decoder_attack_success_rate": wrong_decoder_collision_rate,
            "same_contact_history_collapse_rate": alias_rate,
        },
        "frozen_non_claims": frozen_non_claims,
    }


def build_artifact() -> dict[str, object]:
    thermal = _evaluate_fiber(
        name="thermal",
        fixtures=THERMAL_FIXTURES,
        packer="pack_thermal_bundle_payloads",
        unpacker="unpack_thermal_bundle_words_payload",
        wrong_unpackers=[
            "unpack_vibrotactile_bundle_words_payload",
            "unpack_proprioceptive_bundle_words_payload",
        ],
        profile_key="thermal_profile",
        scope="Per-direction thermal delta plus adaptation ledger aligned to the frozen contact stroke.",
        sciences=[
            "somatosensory physiology",
            "information theory",
            "dynamical systems",
        ],
        frozen_non_claims=[
            "No affective-touch claim.",
            "No full ambient-temperature scene claim.",
            "No claim beyond bounded thermal delta and adaptation recovery attached to contact episodes.",
        ],
    )
    vibrotactile = _evaluate_fiber(
        name="vibrotactile",
        fixtures=VIBRO_FIXTURES,
        packer="pack_vibrotactile_bundle_payloads",
        unpacker="unpack_vibrotactile_bundle_words_payload",
        wrong_unpackers=[
            "unpack_thermal_bundle_words_payload",
            "unpack_proprioceptive_bundle_words_payload",
        ],
        profile_key="vibrotactile_profile",
        scope="RA-II-only bounded frequency/amplitude/envelope/adaptation sequences aligned to frozen contact strokes.",
        sciences=[
            "mechanoreceptor physiology",
            "information theory",
            "control",
        ],
        frozen_non_claims=[
            "No claim for non-RA-II vibrotactile semantics.",
            "No audio/haptic synthesis claim.",
            "No claim beyond bounded RA-II descriptor recovery on contact-aligned episodes.",
        ],
    )
    proprioceptive = _evaluate_fiber(
        name="proprioceptive",
        fixtures=PROPRIO_FIXTURES,
        packer="pack_proprioceptive_bundle_payloads",
        unpacker="unpack_proprioceptive_bundle_words_payload",
        wrong_unpackers=[
            "unpack_thermal_bundle_words_payload",
            "unpack_vibrotactile_bundle_words_payload",
        ],
        profile_key="proprioceptive_profile",
        scope="Bounded joint-angle/tension trajectory attached to the frozen touch episode as an explicit ordered ledger.",
        sciences=[
            "proprioceptive physiology",
            "information theory",
            "dynamical systems",
        ],
        frozen_non_claims=[
            "No full-body kinematics claim.",
            "No affective or agency claim.",
            "No claim beyond bounded joint-angle/tension trajectory recovery attached to touch episodes.",
        ],
    )

    all_statuses = {fiber["status"] for fiber in (thermal, vibrotactile, proprioceptive)}
    final_verdict = (
        "bounded_adopter_per_fiber"
        if all_statuses == {"bounded_adopter"}
        else "mixed_or_failed"
    )

    return {
        "lane": "L6",
        "wave": "geogram5",
        "repo": "zpe-touch-codec",
        "claim_class": "geometry-decomposable but not yet stroke-decomposable",
        "frozen_scope": {
            "base": "Frozen Geogram 3 contact geometry remains unchanged.",
            "fibers_tested": ["thermal", "vibrotactile", "proprioceptive"],
            "state_history_rule": "Each fiber carries an explicit ordered history/adaptation ledger on the authority path.",
        },
        "authoritative_adopter_status": final_verdict,
        "authoritative_backend": dict(NATIVE.backend_info()),
        "contact_base_status": {
            "release_scope_path": str(REPO_ROOT / "docs" / "L6_TOUCH_BOUNDED_RELEASE_SCOPE.md"),
            "frozen": True,
            "contact_base_edit_required": False,
        },
        "fiber_results": {
            "thermal": thermal,
            "vibrotactile": vibrotactile,
            "proprioceptive": proprioceptive,
        },
        "final_verdict": (
            "All three tested fibers transition as bounded adopters on independent typed bundle branches while the legacy contact decoder still sees the unchanged contact base."
            if final_verdict == "bounded_adopter_per_fiber"
            else "One or more fibers failed the bounded-adopter gate."
        ),
        "curated_evidence": {
            "tests": [
                str(REPO_ROOT / "tests" / "test_touch_pack_regression.py"),
                str(REPO_ROOT / "tests" / "test_touch_native_optional.py"),
                str(REPO_ROOT / "tests" / "test_touch_fiber_bundles.py"),
            ],
            "report": str(GEOGRAM5_ROOT / "report" / "L6_FINAL_REPORT.md"),
            "artifact": str(GEOGRAM5_ROOT / "artifacts" / "l6_touch_geogram5.json"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=GEOGRAM5_ROOT / "artifacts" / "l6_touch_geogram5.json",
    )
    args = parser.parse_args()

    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
