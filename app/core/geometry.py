from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Line:
    start: Point
    end: Point


@dataclass(frozen=True)
class Rectangle:
    xmin: float
    ymin: float
    xmax: float
    ymax: float