from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
CORE_ROOT = REPO_ROOT.parent / "zpe-core"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from tests.common import configure_env

configure_env()

from source.touch.codec import decode_touch, encode_touch, get_touch_backend_info
from source.touch.pack import pack_touch_strokes, pack_touch_zlayers, unpack_touch_words, unpack_touch_zlayers
from source.touch.types import BodyRegion, DrawDir, MoveTo, ReceptorType, TouchStroke


def _signature(stroke: TouchStroke) -> tuple[int, int, tuple[int, ...], tuple[int, ...]]:
    return (
        int(stroke.receptor),
        int(stroke.region),
        tuple(command.direction for command in stroke.commands if isinstance(command, DrawDir)),
        tuple(int(value) for value in (stroke.pressure_profile or [])),
    )


def _build_strokes() -> list[TouchStroke]:
    return [
        TouchStroke(
            commands=[MoveTo(0, 0), DrawDir(0), DrawDir(1), DrawDir(2)],
            receptor=ReceptorType.SA_I,
            region=BodyRegion.INDEX_TIP,
            pressure_profile=[2, 3, 4],
        ),
        TouchStroke(
            commands=[MoveTo(0, 0), DrawDir(7), DrawDir(6), DrawDir(5)],
            receptor=ReceptorType.RA_II,
            region=BodyRegion.THUMB_TIP,
            pressure_profile=[3, 2, 1],
        ),
    ]


def build_payload() -> dict[str, object]:
    backend = get_touch_backend_info()
    if backend["backend"] != "rust":
        raise RuntimeError("touch backend is not native rust")

    strokes = _build_strokes()
    native_words = encode_touch(strokes)
    python_words = pack_touch_strokes(strokes)
    native_meta, native_decoded = decode_touch(native_words)
    python_meta, python_decoded = unpack_touch_words(python_words)

    helper_words = pack_touch_zlayers([0, 6, 4], [2, 3, 2], BodyRegion.PALM_CENTER)
    helper_decoded = unpack_touch_zlayers(helper_words)
    helper_recovery = 1.0 if helper_decoded["surface"] == [0, 6, 4] and helper_decoded["dermal"] == [2, 3, 2] else 0.0

    contact = strokes[0]
    authority_a = encode_touch([contact])
    authority_b = [authority_a[0], *pack_touch_zlayers([0, 6, 4], [2, 3, 2], BodyRegion.PALM_CENTER), *authority_a[1:]]
    authority_c = [authority_a[0], *pack_touch_zlayers([4, 2, 0], [1, 1, 1], BodyRegion.PALM_CENTER), *authority_a[1:]]
    _, decoded_b = decode_touch(authority_b)
    _, decoded_c = decode_touch(authority_c)
    sidechannel_retention = 1.0 if [_signature(stroke) for stroke in decoded_b] != [_signature(stroke) for stroke in decoded_c] else 0.0

    return {
        "lane": "L6",
        "repo": "zpe-touch-codec",
        "status": "bounded_release_preserved",
        "authoritative_backend": backend,
        "authority_metrics": {
            "raw_contact_exact_rate": float([_signature(stroke) for stroke in native_decoded] == [_signature(stroke) for stroke in strokes]),
            "baseline_delta": 0.0 if native_words == python_words and native_meta == python_meta else 1.0,
        },
        "helper_leakage_result": {
            "helper_sidechannel_recovery_rate": helper_recovery,
            "authority_sidechannel_retention_rate": sidechannel_retention,
            "helper_authority_gap": helper_recovery - sidechannel_retention,
        },
        "evidence": {
            "native_words_match_python_reference": native_words == python_words,
            "native_metadata_match_python_reference": native_meta == python_meta,
            "decoded_signatures_match_reference": [_signature(stroke) for stroke in native_decoded]
            == [_signature(stroke) for stroke in python_decoded],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts" / "l6_touch_split_matrix.json")
    args = parser.parse_args()

    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
