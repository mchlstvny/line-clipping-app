from app.core.geometry import Line, Point, Rectangle


def clip_line(line: Line, window: Rectangle) -> Line | None:
    x1, y1 = line.start.x, line.start.y
    x2, y2 = line.end.x, line.end.y

    dx = x2 - x1
    dy = y2 - y1

    p = [
        -dx,
        dx,
        -dy,
        dy,
    ]

    q = [
        x1 - window.xmin,
        window.xmax - x1,
        y1 - window.ymin,
        window.ymax - y1,
    ]

    t_enter = 0.0
    t_exit = 1.0

    for pi, qi in zip(p, q):
        # Line is parallel to this clipping boundary
        if pi == 0:
            if qi < 0:
                return None

            continue

        t = qi / pi

        if pi < 0:
            t_enter = max(t_enter, t)
        else:
            t_exit = min(t_exit, t)

        if t_enter > t_exit:
            return None

    clipped_start = Point(
        x1 + t_enter * dx,
        y1 + t_enter * dy,
    )

    clipped_end = Point(
        x1 + t_exit * dx,
        y1 + t_exit * dy,
    )

    return Line(
        start=clipped_start,
        end=clipped_end,
    )