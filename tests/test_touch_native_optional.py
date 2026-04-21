from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _has_native_touch_module() -> bool:
    for name in ("zpe_touch._native",):
        try:
            if importlib.util.find_spec(name) is not None:
                return True
        except ModuleNotFoundError:
            continue
    return False


if not _has_native_touch_module():
    pytest.skip("zpe-touch wheel is not installed", allow_module_level=True)

from tests.common import configure_env

configure_env()

from zpe_touch.codec import decode_touch, encode_touch, get_touch_backend_info
from zpe_touch.pack import pack_touch_strokes, unpack_touch_words
from zpe_touch.types import BodyRegion, DrawDir, MoveTo, ReceptorType, TouchStroke


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


def _signature(stroke: TouchStroke) -> tuple[int, int, tuple[int, ...], tuple[int, ...]]:
    return (
        int(stroke.receptor),
        int(stroke.region),
        tuple(command.direction for command in stroke.commands if isinstance(command, DrawDir)),
        tuple(int(value) for value in (stroke.pressure_profile or [])),
    )


def test_touch_native_backend_reports_rust() -> None:
    info = get_touch_backend_info()

    assert info["backend"] == "rust"
    assert info["native"] is True
    assert info["fallback_used"] is False
    assert info["module_file"]


def test_touch_native_matches_python_reference_words_and_decode() -> None:
    strokes = _build_strokes()

    native_words = encode_touch(strokes)
    python_words = pack_touch_strokes(strokes)
    native_meta, native_decoded = decode_touch(native_words)
    python_meta, python_decoded = unpack_touch_words(python_words)

    assert native_words == python_words
    assert native_meta == python_meta
    assert [_signature(stroke) for stroke in native_decoded] == [_signature(stroke) for stroke in python_decoded]
