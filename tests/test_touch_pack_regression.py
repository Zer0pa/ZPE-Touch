from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.common import configure_env

configure_env()

from source.core.imc import IMCDecoder, IMCEncoder
from source.touch.pack import pack_touch_strokes, unpack_touch_words
from source.touch.types import BodyRegion, DrawDir, MoveTo, ReceptorType, TouchStroke


def _build_touch_regression_strokes() -> list[TouchStroke]:
    return [
        TouchStroke(
            commands=[MoveTo(0, 0), DrawDir(0), DrawDir(1), DrawDir(2)],
            receptor=ReceptorType.SA_I,
            region=BodyRegion.INDEX_TIP,
            pressure_profile=[2, 3, 4],
        ),
        TouchStroke(
            commands=[MoveTo(0, 0), DrawDir(4), DrawDir(4), DrawDir(4)],
            receptor=ReceptorType.RA_I,
            region=BodyRegion.PALM_CENTER,
            pressure_profile=[6, 6, 6],
        ),
        TouchStroke(
            commands=[MoveTo(0, 0), DrawDir(7), DrawDir(6), DrawDir(5)],
            receptor=ReceptorType.RA_II,
            region=BodyRegion.THUMB_TIP,
            pressure_profile=[3, 2, 1],
        ),
    ]


def _touch_sig(stroke: TouchStroke) -> tuple[int, int, tuple[int, ...]]:
    directions = tuple(cmd.direction for cmd in stroke.commands[1:] if isinstance(cmd, DrawDir))
    return (int(stroke.receptor), int(stroke.region), directions)


def test_touch_pack_roundtrip_preserves_third_raii_thumb_tip_stroke() -> None:
    strokes = _build_touch_regression_strokes()

    words = pack_touch_strokes(strokes)
    metadata, decoded = unpack_touch_words(words)

    assert metadata == {
        "consumed_touch_words": 12,
        "header_words": 3,
        "ignored_words": 0,
    }
    assert [_touch_sig(stroke) for stroke in decoded] == [_touch_sig(stroke) for stroke in strokes]


def test_touch_only_imc_roundtrip_keeps_touch_block_intact() -> None:
    strokes = _build_touch_regression_strokes()

    stream = IMCEncoder().add_touch(strokes).build()
    result = IMCDecoder().decode(stream)

    assert result.modality_counts["touch"] == 12
    assert result.modality_counts["taste"] == 0
    assert len(result.touch_blocks) == 1
    assert [_touch_sig(stroke) for stroke in result.touch_blocks[0][1]] == [_touch_sig(stroke) for stroke in strokes]
