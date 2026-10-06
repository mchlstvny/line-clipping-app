from app.algorithms.cohen_sutherland import clip_line
from app.core.geometry import Line, Point, Rectangle


def main():
    window = Rectangle(
        xmin=150,
        ymin=100,
        xmax=350,
        ymax=250,
    )

    test_lines = [
        Line(Point(200, 150), Point(300, 200)),
        Line(Point(100, 175), Point(250, 175)),
        Line(Point(250, 150), Point(400, 150)),
        Line(Point(50, 50), Point(100, 75)),
        Line(Point(50, 50), Point(450, 300)),
    ]

    for index, line in enumerate(test_lines, start=1):
        result = clip_line(line, window)

        print(f"Line {index}:")
        print(f"  Original: {line}")
        print(f"  Clipped:  {result}")
        print()


if __name__ == "__main__":
    main()