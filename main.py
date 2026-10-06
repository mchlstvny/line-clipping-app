from app.core.geometry import Line, Point, Rectangle


def main():
    start = Point(100, 100)
    end = Point(400, 300)

    line = Line(start=start, end=end)

    clipping_window = Rectangle(
        xmin=150,
        ymin=100,
        xmax=350,
        ymax=250,
    )

    print("Line:", line)
    print("Clipping window:", clipping_window)


if __name__ == "__main__":
    main()