from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

DIRS: tuple[tuple[int, int], ...] = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
)


@dataclass(frozen=True)
class MoveTo:
    x: int
    y: int


@dataclass(frozen=True)
class DrawDir:
    direction: int

    def __post_init__(self) -> None:
        if not 0 <= self.direction <= 7:
            raise ValueError(f"direction must be in [0, 7], got {self.direction}")

    def delta(self) -> tuple[int, int]:
        return DIRS[self.direction]


class ReceptorType(IntEnum):
    SA_I = 0
    RA_I = 1
    RA_II = 2
    SA_II = 3


class BodyRegion(IntEnum):
    THUMB_TIP = 0
    INDEX_TIP = 1
    MIDDLE_TIP = 2
    RING_TIP = 3
    PINKY_TIP = 4
    PALM_THENAR = 5
    PALM_HYPOTHENAR = 6
    PALM_CENTER = 7
    DORSAL_HAND = 8
    WRIST_FOREARM = 9
    LIPS = 10
    TONGUE = 11
    FACE = 12
    TORSO = 13
    ARM_LEG = 14
    FOOT_SOLE = 15


class TouchZLevel(IntEnum):
    SURFACE = 0
    DERMAL = 1
    ANATOMICAL = 2
    PROPRIOCEPTIVE = 3


@dataclass
class TouchStroke:
    commands: list[MoveTo | DrawDir]
    receptor: ReceptorType = ReceptorType.SA_I
    region: BodyRegion = BodyRegion.INDEX_TIP
    pressure_profile: list[int] | None = None

    def __post_init__(self) -> None:
        if self.pressure_profile is None:
            self.pressure_profile = []
        for command in self.commands:
            if not isinstance(command, (MoveTo, DrawDir)):
                raise TypeError(f"unsupported command {command!r}")
        for pressure in self.pressure_profile:
            if not 0 <= pressure <= 7:
                raise ValueError(f"pressure level must be in [0, 7], got {pressure}")
        if len(self.pressure_profile) > self.draw_count:
            raise ValueError("pressure_profile length cannot exceed number of DrawDir commands")

    @property
    def draw_count(self) -> int:
        return sum(1 for command in self.commands if isinstance(command, DrawDir))


def ensure_body_region(region: int | BodyRegion) -> BodyRegion:
    return region if isinstance(region, BodyRegion) else BodyRegion(region)


def ensure_receptor_type(receptor: int | ReceptorType) -> ReceptorType:
    return receptor if isinstance(receptor, ReceptorType) else ReceptorType(receptor)
