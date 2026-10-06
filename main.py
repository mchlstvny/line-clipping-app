from app.core.geometry import Line, Point, Rectangle
from app.services.clipping_service import clip_line


def main():
    window = Rectangle(
        xmin=150,
        ymin=100,
        xmax=350,
        ymax=250,
    )

    line = Line(
        start=Point(50, 50),
        end=Point(450, 300),
    )

    algorithms = [
        "cohen-sutherland",
        "liang-barsky",
    ]

    for algorithm in algorithms:
        result = clip_line(line, window, algorithm)

        print(f"Algorithm: {algorithm}")
        print(f"Original:  {line}")
        print(f"Clipped:   {result}")
        print()


if __name__ == "__main__":
    main()