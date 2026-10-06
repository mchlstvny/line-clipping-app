from app.core.constants import INSIDE, LEFT, RIGHT, BOTTOM, TOP
from app.core.geometry import Line, Point, Rectangle


def compute_region_code(point: Point, window: Rectangle) -> int:
    code = INSIDE

    if point.x < window.xmin:
        code |= LEFT
    elif point.x > window.xmax:
        code |= RIGHT

    if point.y < window.ymin:
        code |= BOTTOM
    elif point.y > window.ymax:
        code |= TOP

    return code

def clip_line(line: Line, window: Rectangle) -> Line | None:
    x1, y1 = line.start.x, line.start.y
    x2, y2 = line.end.x, line.end.y

    code1 = compute_region_code(line.start, window)
    code2 = compute_region_code(line.end, window)

    while True:
        # both endpoints are inside
        if code1 == 0 and code2 == 0:
            return Line(
                start=Point(x1, y1),
                end=Point(x2, y2),
            )

        # both endpoints are outside on the same side
        if code1 & code2:
            return None

        # choose the endpoint that is outside
        code_out = code1 if code1 != 0 else code2

        # find intersection with clipping boundary
        if code_out & TOP:
            x = x1 + (x2 - x1) * (window.ymax - y1) / (y2 - y1)
            y = window.ymax

        elif code_out & BOTTOM:
            x = x1 + (x2 - x1) * (window.ymin - y1) / (y2 - y1)
            y = window.ymin

        elif code_out & RIGHT:
            y = y1 + (y2 - y1) * (window.xmax - x1) / (x2 - x1)
            x = window.xmax

        else:  # LEFT
            y = y1 + (y2 - y1) * (window.xmin - x1) / (x2 - x1)
            x = window.xmin

        # replace the outside endpoint
        if code_out == code1:
            x1, y1 = x, y
            code1 = compute_region_code(Point(x1, y1), window)
        else:
            x2, y2 = x, y
            code2 = compute_region_code(Point(x2, y2), window)