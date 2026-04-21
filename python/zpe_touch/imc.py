from __future__ import annotations

from dataclasses import dataclass, field

from .codec import decode_touch, encode_touch
from .types import TouchStroke


@dataclass
class IMCResult:
    touch_blocks: list[tuple[dict | None, list[TouchStroke]]]
    modality_counts: dict[str, int]
    stream_valid: bool = True
    validation_errors: list[str] = field(default_factory=list)


class IMCEncoder:
    def __init__(self) -> None:
        self._touch_blocks: list[list[TouchStroke]] = []

    def add_touch(self, strokes: list[TouchStroke]) -> "IMCEncoder":
        self._touch_blocks.append(list(strokes))
        return self

    def build(self) -> list[int]:
        words: list[int] = []
        for strokes in self._touch_blocks:
            words.extend(encode_touch(strokes))
        return words


class IMCDecoder:
    def decode(self, stream: list[int]) -> IMCResult:
        metadata, strokes = decode_touch(stream)
        touch_words = int((metadata or {}).get("consumed_touch_words", 0))
        return IMCResult(
            touch_blocks=[(metadata, strokes)] if strokes else [],
            modality_counts={
                "touch": touch_words,
            },
        )
