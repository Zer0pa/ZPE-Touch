from __future__ import annotations

from typing import Iterable, Sequence

from .types import (
    BodyRegion,
    DrawDir,
    MoveTo,
    ReceptorType,
    TouchStroke,
    TouchZLevel,
    ensure_body_region,
    ensure_receptor_type,
)

MODE_EXTENSION = 0b10
DATA_VERSION = 0
HEADER_VERSION = 1
CONTROL_VERSION = 2

TOUCH_TYPE_BIT = 0x0800
LEGACY_HEADER_RECEPTOR_SHIFT = 9
HEADER_RECEPTOR_LOW_SHIFT = 9
HEADER_RECEPTOR_HIGH_SHIFT = 4
HEADER_REGION_SHIFT = 5
LEGACY_HEADER_TAG = 0x001F
HEADER_TAG = 0x0007
DIRECTION_SHIFT = 3

CONTROL_TAG_SHIFT = 8
CONTROL_TAG_MASK = 0x7
CONTROL_ZLAYER = 5

Z_LEVEL_SHIFT = 6
Z_LEVEL_MASK = 0x3
Z_VALUE_MASK = 0x3F


def _pack_extension_word(version: int, payload: int) -> int:
    return (MODE_EXTENSION << 18) | ((version & 0x3) << 16) | (payload & 0xFFFF)


def _build_header_word(receptor: int, region: int) -> int:
    if not 0 <= receptor <= 3:
        raise ValueError(f"receptor out of range: {receptor}")
    if not 0 <= region <= 15:
        raise ValueError(f"region out of range: {region}")

    payload = TOUCH_TYPE_BIT
    payload |= (receptor & 0x1) << HEADER_RECEPTOR_LOW_SHIFT
    payload |= (region & 0xF) << HEADER_REGION_SHIFT
    payload |= ((receptor >> 1) & 0x1) << HEADER_RECEPTOR_HIGH_SHIFT
    payload |= HEADER_TAG
    return _pack_extension_word(HEADER_VERSION, payload)


def _build_step_word(direction: int, pressure: int) -> int:
    if not 0 <= direction <= 7:
        raise ValueError(f"direction out of range: {direction}")
    if not 0 <= pressure <= 7:
        raise ValueError(f"pressure out of range: {pressure}")

    payload = TOUCH_TYPE_BIT
    payload |= (direction & 0x7) << DIRECTION_SHIFT
    payload |= pressure & 0x7
    return _pack_extension_word(DATA_VERSION, payload)


def _word_mode(word: int) -> int:
    return (word >> 18) & 0x3


def _word_version(word: int) -> int:
    return (word >> 16) & 0x3


def _is_touch_extension_word(word: int) -> bool:
    return _word_mode(word) == MODE_EXTENSION and (word & TOUCH_TYPE_BIT) != 0


def _is_header_word(word: int) -> bool:
    if not _is_touch_extension_word(word) or _word_version(word) != HEADER_VERSION:
        return False
    payload = word & 0xFFFF
    return (payload & LEGACY_HEADER_TAG) == LEGACY_HEADER_TAG or (payload & 0xF) == HEADER_TAG


def _decode_header_word(word: int) -> tuple[int, int]:
    payload = word & 0xFFFF
    region_val = (payload >> HEADER_REGION_SHIFT) & 0xF
    if (payload & LEGACY_HEADER_TAG) == LEGACY_HEADER_TAG:
        receptor_val = (payload >> LEGACY_HEADER_RECEPTOR_SHIFT) & 0x3
        return receptor_val, region_val

    receptor_low = (payload >> HEADER_RECEPTOR_LOW_SHIFT) & 0x1
    receptor_high = (payload >> HEADER_RECEPTOR_HIGH_SHIFT) & 0x1
    receptor_val = receptor_low | (receptor_high << 1)
    return receptor_val, region_val


def pack_zlayer_word(z_level: TouchZLevel | int, value: int) -> int:
    z_level_int = int(z_level.value) if isinstance(z_level, TouchZLevel) else int(z_level)
    if not 0 <= z_level_int <= 3:
        raise ValueError(f"z_level must be in [0, 3], got {z_level_int}")
    if not 0 <= value <= Z_VALUE_MASK:
        raise ValueError(f"value must be in [0, {Z_VALUE_MASK}], got {value}")

    payload = TOUCH_TYPE_BIT
    payload |= (CONTROL_ZLAYER & CONTROL_TAG_MASK) << CONTROL_TAG_SHIFT
    payload |= (z_level_int & Z_LEVEL_MASK) << Z_LEVEL_SHIFT
    payload |= value & Z_VALUE_MASK
    return _pack_extension_word(CONTROL_VERSION, payload)


def unpack_zlayer_word(word: int) -> tuple[TouchZLevel, int]:
    if not (_is_touch_extension_word(word) and _word_version(word) == CONTROL_VERSION):
        raise ValueError("word is not a z-layer control word")
    tag = (word >> CONTROL_TAG_SHIFT) & CONTROL_TAG_MASK
    if tag != CONTROL_ZLAYER:
        raise ValueError("control word is not z-layer data")
    z_level = TouchZLevel((word >> Z_LEVEL_SHIFT) & Z_LEVEL_MASK)
    value = word & Z_VALUE_MASK
    return z_level, value


def pack_touch_zlayers(
    directions: Sequence[int],
    pressures: Sequence[int],
    region: BodyRegion,
) -> list[int]:
    words: list[int] = []
    for direction in directions:
        if not 0 <= direction <= 7:
            raise ValueError(f"direction must be in [0, 7], got {direction}")
        words.append(pack_zlayer_word(TouchZLevel.SURFACE, direction))
    for pressure in pressures:
        if not 0 <= pressure <= 7:
            raise ValueError(f"pressure must be in [0, 7], got {pressure}")
        words.append(pack_zlayer_word(TouchZLevel.DERMAL, pressure))
    words.append(pack_zlayer_word(TouchZLevel.ANATOMICAL, int(region.value)))
    return words


def unpack_touch_zlayers(words: Iterable[int]) -> dict[str, object]:
    surface: list[int] = []
    dermal: list[int] = []
    anatomical_values: list[int] = []
    proprioceptive_values: list[int] = []
    ignored = 0

    for word in words:
        if not (_is_touch_extension_word(word) and _word_version(word) == CONTROL_VERSION):
            ignored += 1
            continue
        tag = (word >> CONTROL_TAG_SHIFT) & CONTROL_TAG_MASK
        if tag != CONTROL_ZLAYER:
            ignored += 1
            continue
        try:
            z_level, value = unpack_zlayer_word(word)
        except ValueError:
            ignored += 1
            continue

        if z_level == TouchZLevel.SURFACE:
            surface.append(value)
        elif z_level == TouchZLevel.DERMAL:
            dermal.append(value)
        elif z_level == TouchZLevel.ANATOMICAL:
            anatomical_values.append(value)
        elif z_level == TouchZLevel.PROPRIOCEPTIVE:
            proprioceptive_values.append(value)
        else:
            ignored += 1

    anatomical_region = BodyRegion(anatomical_values[-1] & 0xF) if anatomical_values else None
    return {
        "surface": surface,
        "dermal": dermal,
        "anatomical_values": anatomical_values,
        "anatomical_region": anatomical_region,
        "proprioceptive_values": proprioceptive_values,
        "ignored_words": ignored,
    }


def pack_touch_strokes(
    strokes: Iterable[TouchStroke],
    metadata: dict | None = None,
) -> list[int]:
    del metadata
    words: list[int] = []
    for stroke in strokes:
        directions = [command.direction for command in stroke.commands if isinstance(command, DrawDir)]
        if not directions:
            continue

        receptor = int(ensure_receptor_type(stroke.receptor).value)
        region = int(ensure_body_region(stroke.region).value)
        words.append(_build_header_word(receptor=receptor, region=region))

        for index, direction in enumerate(directions):
            pressure = stroke.pressure_profile[index] if index < len(stroke.pressure_profile) else 0
            words.append(_build_step_word(direction=direction, pressure=pressure))
    return words


def unpack_touch_words(words: Iterable[int]) -> tuple[dict[str, int], list[TouchStroke]]:
    decoded: list[TouchStroke] = []
    current: TouchStroke | None = None
    consumed = 0
    headers = 0
    ignored = 0

    for word in words:
        if not _is_touch_extension_word(word):
            ignored += 1
            continue

        if _is_header_word(word):
            receptor_val, region_val = _decode_header_word(word)
            if current is not None and current.draw_count > 0:
                decoded.append(current)

            current = TouchStroke(
                commands=[MoveTo(0, 0)],
                receptor=ReceptorType(receptor_val),
                region=BodyRegion(region_val),
                pressure_profile=[],
            )
            headers += 1
            consumed += 1
            continue

        if _word_version(word) != DATA_VERSION:
            ignored += 1
            continue
        if current is None:
            ignored += 1
            continue

        direction = (word >> DIRECTION_SHIFT) & 0x7
        pressure = word & 0x7
        current.commands.append(DrawDir(direction))
        current.pressure_profile.append(pressure)
        consumed += 1

    if current is not None and current.draw_count > 0:
        decoded.append(current)

    return {
        "consumed_touch_words": consumed,
        "header_words": headers,
        "ignored_words": ignored,
    }, decoded
