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

from tests.common import configure_env

configure_env()

from zpe_touch.codec import decode_touch, encode_touch, get_touch_backend_info
from zpe_touch.pack import pack_touch_strokes, pack_touch_zlayers, unpack_touch_words, unpack_touch_zlayers
from zpe_touch.types import BodyRegion, DrawDir, MoveTo, ReceptorType, TouchStroke


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
    backend["module_file"] = Path(str(backend.get("module_file") or "")).name

    strokes = _build_strokes()
    native_words = encode_touch(strokes)
    python_words = pack_touch_strokes(strokes)
    native_meta, native_decoded = decode_touch(native_words)
    python_meta, python_decoded = unpack_touch_words(python_words)

    reference_words = pack_touch_zlayers([0, 6, 4], [2, 3, 2], BodyRegion.PALM_CENTER)
    reference_decoded = unpack_touch_zlayers(reference_words)
    reference_recovery = 1.0 if reference_decoded["surface"] == [0, 6, 4] and reference_decoded["dermal"] == [2, 3, 2] else 0.0

    contact = strokes[0]
    contact_words = encode_touch([contact])
    with_reference_a = [contact_words[0], *pack_touch_zlayers([0, 6, 4], [2, 3, 2], BodyRegion.PALM_CENTER), *contact_words[1:]]
    with_reference_b = [contact_words[0], *pack_touch_zlayers([4, 2, 0], [1, 1, 1], BodyRegion.PALM_CENTER), *contact_words[1:]]
    _, decoded_a = decode_touch(with_reference_a)
    _, decoded_b = decode_touch(with_reference_b)
    contact_retention = 1.0 if [_signature(stroke) for stroke in decoded_a] != [_signature(stroke) for stroke in decoded_b] else 0.0

    return {
        "repo": "zpe-touch",
        "release_scope": "bounded_touch_contact",
        "status": "bounded_release_preserved",
        "authoritative_backend": backend,
        "contact_metrics": {
            "raw_contact_exact_rate": float([_signature(stroke) for stroke in native_decoded] == [_signature(stroke) for stroke in strokes]),
            "baseline_delta": 0.0 if native_words == python_words and native_meta == python_meta else 1.0,
        },
        "zlayer_reference_check": {
            "reference_zlayer_recovery_rate": reference_recovery,
            "contact_branch_zlayer_retention_rate": contact_retention,
            "reference_contact_gap": reference_recovery - contact_retention,
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
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "proofs" / "artifacts" / "contact_release_summary.json")
    args = parser.parse_args()

    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
