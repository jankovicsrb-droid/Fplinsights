POSITION_MAP: dict[int, str] = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
POSITION_REVERSE: dict[str, int] = {v: k for k, v in POSITION_MAP.items()}

POSITIONS: list[str] = ["GK", "DEF", "MID", "FWD"]


def position_label(element_type: int | None) -> str:
    return POSITION_MAP.get(element_type, "?")


def position_code(label: str | None) -> int | None:
    if not label:
        return None
    return POSITION_REVERSE.get(label.upper())
