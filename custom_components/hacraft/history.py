"""Pure helpers for hacraft/get_history (no Home Assistant imports, so they can be tested on their own)."""
from __future__ import annotations

_ON = {"on", "open", "opening", "playing", "home", "detected", "heat", "cool", "cleaning"}
_OFF = {"off", "closed", "closing", "idle", "paused", "not_home", "clear", "docked"}


def state_to_number(state: str | None) -> float | None:
    """A state as a number for graphing: numbers as they are, on/off-style states as 1/0, anything else None."""
    if state is None:
        return None
    text = str(state).strip()
    try:
        value = float(text)
    except ValueError:
        lowered = text.lower()
        if lowered in _ON:
            return 1.0
        if lowered in _OFF:
            return 0.0
        return None
    if value != value or value in (float("inf"), float("-inf")):
        return None
    return value


def downsample(points: list[tuple[float, float]], start: float, end: float, count: int) -> list[float | None]:
    """Spread a state history over ``count`` evenly spaced moments between ``start`` and ``end``.

    ``points`` are (timestamp, value) pairs sorted by time. Each output slot is the value that was current at
    the end of its time slice (a state holds until it changes), or None if nothing was known yet. The last slot
    is therefore the value now.
    """
    if count < 1 or end <= start:
        return []
    step = (end - start) / count
    result: list[float | None] = []
    index = 0
    current: float | None = None
    for slot in range(count):
        slot_end = start + step * (slot + 1)
        while index < len(points) and points[index][0] <= slot_end:
            current = points[index][1]
            index += 1
        result.append(current)
    return result
