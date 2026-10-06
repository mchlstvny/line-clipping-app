from app.algorithms import cohen_sutherland, liang_barsky
from app.core.geometry import Line, Rectangle


def clip_line(
    line: Line,
    window: Rectangle,
    algorithm: str,
) -> Line | None:
    if algorithm == "cohen-sutherland":
        return cohen_sutherland.clip_line(line, window)

    if algorithm == "liang-barsky":
        return liang_barsky.clip_line(line, window)

    raise ValueError(f"Unknown clipping algorithm: {algorithm}")