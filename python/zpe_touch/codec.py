from __future__ import annotations

from importlib import import_module
from typing import Any, Iterable

from .pack import pack_touch_strokes, unpack_touch_words
from .types import BodyRegion, DrawDir, MoveTo, ReceptorType, TouchStroke, ensure_body_region, ensure_receptor_type

_NATIVE_MODULE = None
_NATIVE_IMPORT_ERROR: Exception | None = None


def _load_native_module():
    global _NATIVE_MODULE, _NATIVE_IMPORT_ERROR
    if _NATIVE_MODULE is not None:
        return _NATIVE_MODULE
    if _NATIVE_IMPORT_ERROR is not None:
        return None

    last_error: Exception | None = None
    for module_name in ("zpe_touch._native",):
        try:
            _NATIVE_MODULE = import_module(module_name)
            return _NATIVE_MODULE
        except Exception as exc:  # pragma: no cover - import surface is environment-specific
            last_error = exc
    _NATIVE_IMPORT_ERROR = last_error
    return None


def _stroke_to_payload(stroke: TouchStroke) -> dict[str, object]:
    return {
        "receptor": int(ensure_receptor_type(stroke.receptor).value),
        "region": int(ensure_body_region(stroke.region).value),
        "directions": [command.direction for command in stroke.commands if isinstance(command, DrawDir)],
        "pressure_profile": [int(value) for value in (stroke.pressure_profile or [])],
    }


def _stroke_from_payload(payload: dict[str, object]) -> TouchStroke:
    directions = [DrawDir(int(direction)) for direction in payload.get("directions", [])]
    return TouchStroke(
        commands=[MoveTo(0, 0), *directions],
        receptor=ReceptorType(int(payload["receptor"])),
        region=BodyRegion(int(payload["region"])),
        pressure_profile=[int(value) for value in payload.get("pressure_profile", [])],
    )


def get_touch_backend_info() -> dict[str, Any]:
    native = _load_native_module()
    if native is None:
        return {
            "backend": "python",
            "native": False,
            "fallback_used": True,
            "module_name": None,
            "module_file": None,
        }

    info = dict(native.backend_info()) if hasattr(native, "backend_info") else {}
    info.update(
        {
            "backend": str(info.get("backend", "rust")),
            "native": bool(info.get("native", True)),
            "fallback_used": bool(info.get("fallback_used", False)),
            "module_name": str(getattr(native, "__name__", "zpe_touch._native")),
            "module_file": str(getattr(native, "__file__", "") or ""),
        }
    )
    return info


def encode_touch(
    strokes: Iterable[TouchStroke],
    metadata: dict | None = None,
) -> list[int]:
    stroke_list = list(strokes)
    native = _load_native_module()
    if native is not None:
        payload = [_stroke_to_payload(stroke) for stroke in stroke_list]
        return [int(word) for word in native.pack_touch_strokes_payload(payload)]
    return pack_touch_strokes(strokes=stroke_list, metadata=metadata)


def decode_touch(words: Iterable[int]) -> tuple[dict | None, list[TouchStroke]]:
    word_list = [int(word) for word in words]
    native = _load_native_module()
    if native is not None:
        metadata, payloads = native.unpack_touch_words_payload(word_list)
        return dict(metadata), [_stroke_from_payload(dict(payload)) for payload in payloads]
    return unpack_touch_words(words=word_list)
