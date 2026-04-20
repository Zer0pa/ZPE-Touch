from __future__ import annotations

import importlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.common import configure_env

configure_env()

from source.touch.codec import decode_touch
from source.touch.types import DrawDir, TouchStroke


def _native_touch_module():
    for name in ("zpe_touch_codec.zpe_touch_codec", "zpe_touch_codec"):
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError:
            continue
    raise ModuleNotFoundError("zpe_touch_codec native module is not installed")


NATIVE = _native_touch_module()


def _contact_payload(
    *,
    receptor: int,
    region: int,
    directions: list[int],
    pressure_profile: list[int],
) -> dict[str, object]:
    return {
        "receptor": receptor,
        "region": region,
        "directions": directions,
        "pressure_profile": pressure_profile,
    }


def _contact_signature(stroke: TouchStroke) -> tuple[int, int, tuple[int, ...], tuple[int, ...]]:
    return (
        int(stroke.receptor),
        int(stroke.region),
        tuple(command.direction for command in stroke.commands if isinstance(command, DrawDir)),
        tuple(int(value) for value in (stroke.pressure_profile or [])),
    )


def _contact_signature_from_payload(payload: dict[str, object]) -> tuple[int, int, tuple[int, ...], tuple[int, ...]]:
    return (
        int(payload["receptor"]),
        int(payload["region"]),
        tuple(int(value) for value in payload["directions"]),
        tuple(int(value) for value in payload["pressure_profile"]),
    )


THERMAL_FIXTURES = [
    {
        **_contact_payload(receptor=0, region=1, directions=[0, 1, 2], pressure_profile=[2, 3, 4]),
        "thermal_profile": [
            {"delta": -3, "adaptation": 0},
            {"delta": -2, "adaptation": 1},
            {"delta": -1, "adaptation": 2},
        ],
    },
    {
        **_contact_payload(receptor=0, region=1, directions=[0, 1, 2], pressure_profile=[2, 3, 4]),
        "thermal_profile": [
            {"delta": 3, "adaptation": 0},
            {"delta": 2, "adaptation": 1},
            {"delta": 1, "adaptation": 2},
        ],
    },
    {
        **_contact_payload(receptor=0, region=1, directions=[0, 1, 2], pressure_profile=[2, 3, 4]),
        "thermal_profile": [
            {"delta": 3, "adaptation": 9},
            {"delta": 2, "adaptation": 10},
            {"delta": 1, "adaptation": 11},
        ],
    },
    {
        **_contact_payload(receptor=3, region=9, directions=[7, 6, 5], pressure_profile=[5, 4, 3]),
        "thermal_profile": [
            {"delta": 1, "adaptation": 4},
            {"delta": 0, "adaptation": 5},
            {"delta": -1, "adaptation": 6},
        ],
    },
]


VIBRO_FIXTURES = [
    {
        **_contact_payload(receptor=2, region=0, directions=[7, 6, 5], pressure_profile=[3, 2, 1]),
        "vibrotactile_profile": [
            {"band": 3, "amplitude": 9, "envelope": 1, "adaptation": 2},
            {"band": 5, "amplitude": 8, "envelope": 2, "adaptation": 3},
            {"band": 7, "amplitude": 7, "envelope": 3, "adaptation": 4},
        ],
    },
    {
        **_contact_payload(receptor=2, region=0, directions=[7, 6, 5], pressure_profile=[3, 2, 1]),
        "vibrotactile_profile": [
            {"band": 12, "amplitude": 9, "envelope": 1, "adaptation": 2},
            {"band": 10, "amplitude": 8, "envelope": 2, "adaptation": 3},
            {"band": 8, "amplitude": 7, "envelope": 3, "adaptation": 4},
        ],
    },
    {
        **_contact_payload(receptor=2, region=0, directions=[7, 6, 5], pressure_profile=[3, 2, 1]),
        "vibrotactile_profile": [
            {"band": 12, "amplitude": 9, "envelope": 1, "adaptation": 10},
            {"band": 10, "amplitude": 8, "envelope": 2, "adaptation": 11},
            {"band": 8, "amplitude": 7, "envelope": 3, "adaptation": 12},
        ],
    },
    {
        **_contact_payload(receptor=2, region=7, directions=[0, 1, 2], pressure_profile=[4, 4, 4]),
        "vibrotactile_profile": [
            {"band": 2, "amplitude": 6, "envelope": 0, "adaptation": 1},
            {"band": 4, "amplitude": 6, "envelope": 0, "adaptation": 1},
            {"band": 6, "amplitude": 6, "envelope": 0, "adaptation": 1},
        ],
    },
]


PROPRIO_FIXTURES = [
    {
        **_contact_payload(receptor=1, region=7, directions=[4, 4, 4], pressure_profile=[6, 6, 6]),
        "proprioceptive_profile": [
            {"joint_id": 5, "angle_q": 64, "tension": 3},
            {"joint_id": 5, "angle_q": 96, "tension": 5},
        ],
    },
    {
        **_contact_payload(receptor=1, region=7, directions=[4, 4, 4], pressure_profile=[6, 6, 6]),
        "proprioceptive_profile": [
            {"joint_id": 5, "angle_q": 64, "tension": 11},
            {"joint_id": 5, "angle_q": 96, "tension": 13},
        ],
    },
    {
        **_contact_payload(receptor=1, region=7, directions=[4, 4, 4], pressure_profile=[6, 6, 6]),
        "proprioceptive_profile": [
            {"joint_id": 3, "angle_q": 40, "tension": 4},
            {"joint_id": 5, "angle_q": 80, "tension": 6},
            {"joint_id": 6, "angle_q": 120, "tension": 8},
        ],
    },
    {
        **_contact_payload(receptor=0, region=1, directions=[0, 1, 2], pressure_profile=[2, 3, 4]),
        "proprioceptive_profile": [
            {"joint_id": 1, "angle_q": 30, "tension": 2},
            {"joint_id": 3, "angle_q": 70, "tension": 4},
        ],
    },
]


def _assert_base_preserved(words: list[int], fixtures: list[dict[str, object]]) -> None:
    _meta, decoded = decode_touch(words)
    assert [_contact_signature(stroke) for stroke in decoded] == [
        _contact_signature_from_payload(fixture) for fixture in fixtures
    ]


def test_thermal_bundle_roundtrip_preserves_contact_and_history() -> None:
    words = list(NATIVE.pack_thermal_bundle_payloads(THERMAL_FIXTURES))
    metadata, decoded = NATIVE.unpack_thermal_bundle_words_payload(words)

    assert metadata["decoded_bundles"] == len(THERMAL_FIXTURES)
    assert metadata["ignored_words"] == 0
    assert decoded == THERMAL_FIXTURES
    _assert_base_preserved(words, THERMAL_FIXTURES)

    # Same contact, different thermal histories must remain distinct on the authority path.
    assert decoded[1]["thermal_profile"] != decoded[2]["thermal_profile"]
    assert NATIVE.unpack_vibrotactile_bundle_words_payload(words)[0]["decoded_bundles"] == 0
    assert NATIVE.unpack_proprioceptive_bundle_words_payload(words)[0]["decoded_bundles"] == 0


def test_vibrotactile_bundle_roundtrip_is_independent_of_contact_base() -> None:
    words = list(NATIVE.pack_vibrotactile_bundle_payloads(VIBRO_FIXTURES))
    metadata, decoded = NATIVE.unpack_vibrotactile_bundle_words_payload(words)

    assert metadata["decoded_bundles"] == len(VIBRO_FIXTURES)
    assert metadata["ignored_words"] == 0
    assert decoded == VIBRO_FIXTURES
    _assert_base_preserved(words, VIBRO_FIXTURES)

    # Direct baseline still collapses when contact is identical and only the fiber changes.
    assert _contact_signature_from_payload(VIBRO_FIXTURES[0]) == _contact_signature_from_payload(VIBRO_FIXTURES[1])
    assert decoded[0]["vibrotactile_profile"] != decoded[1]["vibrotactile_profile"]
    assert NATIVE.unpack_thermal_bundle_words_payload(words)[0]["decoded_bundles"] == 0
    assert NATIVE.unpack_proprioceptive_bundle_words_payload(words)[0]["decoded_bundles"] == 0


def test_proprioceptive_bundle_roundtrip_preserves_joint_trajectory() -> None:
    words = list(NATIVE.pack_proprioceptive_bundle_payloads(PROPRIO_FIXTURES))
    metadata, decoded = NATIVE.unpack_proprioceptive_bundle_words_payload(words)

    assert metadata["decoded_bundles"] == len(PROPRIO_FIXTURES)
    assert metadata["ignored_words"] == 0
    assert decoded == PROPRIO_FIXTURES
    _assert_base_preserved(words, PROPRIO_FIXTURES)

    # Same contact, different posture history must remain separable.
    assert _contact_signature_from_payload(PROPRIO_FIXTURES[0]) == _contact_signature_from_payload(PROPRIO_FIXTURES[1])
    assert decoded[0]["proprioceptive_profile"] != decoded[1]["proprioceptive_profile"]
    assert NATIVE.unpack_thermal_bundle_words_payload(words)[0]["decoded_bundles"] == 0
    assert NATIVE.unpack_vibrotactile_bundle_words_payload(words)[0]["decoded_bundles"] == 0
