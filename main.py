from app.algorithms.liang_barsky import clip_line
from app.core.geometry import Line, Point, Rectangle


def main():
    window = Rectangle(
        xmin=150,
        ymin=100,
        xmax=350,
        ymax=250,
    )

    test_lines = [
        Line(Point(200, 150), Point(300, 200)),  # Completely inside
        Line(Point(100, 175), Point(250, 175)),  # Enters from left
        Line(Point(250, 150), Point(400, 150)),  # Exits to right
        Line(Point(50, 50), Point(100, 75)),     # Completely outside
        Line(Point(50, 50), Point(450, 300)),    # Crosses diagonally
    ]

    for index, line in enumerate(test_lines, start=1):
        result = clip_line(line, window)

        print(f"Line {index}:")
        print(f"  Original: {line}")
        print(f"  Clipped:  {result}")
        print()


if __name__ == "__main__":
    main()