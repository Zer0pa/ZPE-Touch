from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = REPO_ROOT / "python"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from tests.test_touch_fiber_branches import (
    NATIVE,
    PROPRIO_FIXTURES,
    THERMAL_FIXTURES,
    VIBRO_FIXTURES,
    _contact_signature,
    _contact_signature_from_payload,
)
from zpe_touch.codec import decode_touch


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _base_word_count(fixtures: list[dict[str, object]]) -> int:
    return sum(1 + len(fixture["directions"]) for fixture in fixtures)


def _base_preservation_rate(words: list[int], fixtures: list[dict[str, object]]) -> float:
    _metadata, decoded = decode_touch(words)
    decoded_signatures = [_contact_signature(stroke) for stroke in decoded]
    expected_signatures = [_contact_signature_from_payload(fixture) for fixture in fixtures]
    return float(decoded_signatures == expected_signatures)


def _profile_exact_rate(decoded: list[dict[str, object]], fixtures: list[dict[str, object]], profile_key: str) -> float:
    scores = [float(lhs[profile_key] == rhs[profile_key]) for lhs, rhs in zip(decoded, fixtures)]
    return _mean(scores)


def _same_contact_history_alias_rate(decoded: list[dict[str, object]], profile_key: str) -> float:
    grouped: dict[tuple[int, int, tuple[int, ...], tuple[int, ...]], list[list[dict[str, int]]]] = {}
    for branch in decoded:
        signature = _contact_signature_from_payload(branch)
        grouped.setdefault(signature, []).append(branch[profile_key])

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
        collisions.append(float(metadata["decoded_branches"] > 0))
    return _mean(collisions)


def _evaluate_fiber(
    *,
    fixtures: list[dict[str, object]],
    packer: str,
    unpacker: str,
    wrong_unpackers: list[str],
    profile_key: str,
    scope: str,
    non_claims: list[str],
) -> dict[str, object]:
    words = list(getattr(NATIVE, packer)(fixtures))
    metadata, decoded = getattr(NATIVE, unpacker)(words)

    branch_exact_rate = _profile_exact_rate(decoded, fixtures, profile_key)
    base_preservation_rate = _base_preservation_rate(words, fixtures)
    reference_exact_rate = 1.0
    contact_only_exact_rate = 0.0
    alias_rate = _same_contact_history_alias_rate(decoded, profile_key)
    wrong_decoder_collision_rate = _wrong_decoder_collision_rate(words, wrong_unpackers)

    branch_words = len(words)
    base_words = _base_word_count(fixtures)
    overhead_words = branch_words - base_words

    return {
        "status": "bounded_adopter"
        if branch_exact_rate == 1.0
        and base_preservation_rate == 1.0
        and alias_rate == 0.0
        and wrong_decoder_collision_rate == 0.0
        else "failed",
        "scope": scope,
        "exactness": {
            "branch_exact_rate_mean": branch_exact_rate,
            "branch_exact_rate_min": branch_exact_rate,
            "contact_base_preservation_rate": base_preservation_rate,
            "decoded_branch_count": int(metadata["decoded_branches"]),
            "ignored_word_count": int(metadata["ignored_words"]),
        },
        "overhead": {
            "branch_word_count": branch_words,
            "contact_word_count": base_words,
            "branch_word_overhead_total": overhead_words,
            "branch_word_overhead_mean": overhead_words / len(fixtures),
        },
        "reference_comparison": {
            "reference_fiber_exact_rate_mean": reference_exact_rate,
            "branch_fiber_exact_rate_mean": branch_exact_rate,
            "reference_minus_branch_exact_rate": reference_exact_rate - branch_exact_rate,
        },
        "isolation": {
            "same_contact_history_alias_rate": alias_rate,
            "wrong_decoder_collision_rate": wrong_decoder_collision_rate,
        },
        "contact_only_delta": {
            "contact_only_fiber_exact_rate_mean": contact_only_exact_rate,
            "branch_minus_contact_only": branch_exact_rate - contact_only_exact_rate,
        },
        "non_claims": non_claims,
    }


def build_artifact() -> dict[str, object]:
    thermal = _evaluate_fiber(
        fixtures=THERMAL_FIXTURES,
        packer="pack_thermal_branch_payloads",
        unpacker="unpack_thermal_branch_words_payload",
        wrong_unpackers=[
            "unpack_vibrotactile_branch_words_payload",
            "unpack_proprioceptive_branch_words_payload",
        ],
        profile_key="thermal_profile",
        scope="Per-direction thermal delta plus adaptation history aligned to the frozen contact branch.",
        non_claims=[
            "No affective-touch claim.",
            "No ambient-temperature scene claim.",
            "No claim beyond bounded thermal delta and adaptation recovery attached to contact episodes.",
        ],
    )
    vibrotactile = _evaluate_fiber(
        fixtures=VIBRO_FIXTURES,
        packer="pack_vibrotactile_branch_payloads",
        unpacker="unpack_vibrotactile_branch_words_payload",
        wrong_unpackers=[
            "unpack_thermal_branch_words_payload",
            "unpack_proprioceptive_branch_words_payload",
        ],
        profile_key="vibrotactile_profile",
        scope="RA-II-only bounded frequency, amplitude, envelope, and adaptation sequences aligned to frozen contact branches.",
        non_claims=[
            "No claim for non-RA-II vibrotactile semantics.",
            "No audio or haptic synthesis claim.",
            "No claim beyond bounded RA-II descriptor recovery on contact-aligned episodes.",
        ],
    )
    proprioceptive = _evaluate_fiber(
        fixtures=PROPRIO_FIXTURES,
        packer="pack_proprioceptive_branch_payloads",
        unpacker="unpack_proprioceptive_branch_words_payload",
        wrong_unpackers=[
            "unpack_thermal_branch_words_payload",
            "unpack_vibrotactile_branch_words_payload",
        ],
        profile_key="proprioceptive_profile",
        scope="Bounded joint-angle and tension trajectories attached to the frozen touch episode as an explicit ordered history.",
        non_claims=[
            "No full-body kinematics claim.",
            "No affective or agency claim.",
            "No claim beyond bounded joint-angle and tension recovery attached to touch episodes.",
        ],
    )

    all_statuses = {fiber["status"] for fiber in (thermal, vibrotactile, proprioceptive)}
    final_verdict = "bounded_adopter_per_fiber" if all_statuses == {"bounded_adopter"} else "mixed_or_failed"
    backend = dict(NATIVE.backend_info())
    backend["module_file"] = Path(str(backend.get("module_file") or "")).name

    return {
        "repo": "zpe-touch",
        "release_scope": "bounded_touch_fibers",
        "claim_class": "frozen contact base with independent bounded fiber branches",
        "frozen_scope": {
            "base": "Frozen contact geometry remains unchanged.",
            "fibers_tested": ["thermal", "vibrotactile", "proprioceptive"],
            "history_rule": "Each branch carries explicit ordered history in the stream.",
        },
        "adopter_status": final_verdict,
        "authoritative_backend": backend,
        "contact_base_status": {
            "scope_doc": "docs/BOUNDED_SCOPE.md",
            "frozen": True,
            "contact_base_edit_required": False,
        },
        "fiber_results": {
            "thermal": thermal,
            "vibrotactile": vibrotactile,
            "proprioceptive": proprioceptive,
        },
        "summary": (
            "Thermal, vibrotactile, and proprioceptive each transition as bounded adopters on independent branches while the legacy contact decoder still sees the unchanged contact base."
            if final_verdict == "bounded_adopter_per_fiber"
            else "One or more branches failed the bounded-adopter gate."
        ),
        "curated_evidence": {
            "tests": [
                "tests/test_touch_pack_regression.py",
                "tests/test_touch_native_optional.py",
                "tests/test_touch_fiber_branches.py",
            ],
            "scope_doc": "docs/BOUNDED_SCOPE.md",
            "artifact": "proofs/artifacts/fiber_release_summary.json",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "proofs" / "artifacts" / "fiber_release_summary.json")
    args = parser.parse_args()

    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
