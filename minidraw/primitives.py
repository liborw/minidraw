from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Self, Sequence, Tuple
import copy
from abc import abstractmethod

from .point import Point, PointLike, to_point
from .style import Style
from .spatial import Spatial


# ======================================================================
# Abstract Base Primitive
# ======================================================================

@dataclass(kw_only=True)
class Primitive(Spatial):
    """Base class for all drawable primitives implementing Spatial transformations."""
    style: Style = field(default_factory=Style)

    # ------------------------------------------------------------
    # Abstract geometric interface
    # ------------------------------------------------------------
    @abstractmethod
    def center(self) -> Point:
        """Return the geometric center of the primitive in local coordinates."""
        ...

    # ------------------------------------------------------------
    # Common utilities
    # ------------------------------------------------------------
    def copy(self) -> Self:
        """Return a deep copy of this primitive."""
        return copy.deepcopy(self)

    def set_style(self, style: Style) -> Self:
        """Assign a new style and return self."""
        self.style = style
        return self

# ======================================================================
# Line
# ======================================================================

@dataclass
class Line(Primitive):
    start: Point
    end: Point

    def __init__(self, start: PointLike = (0, 0), end: PointLike = (0, 0), **kwargs):
        super().__init__(**kwargs)
        self.start = to_point(start)
        self.end = to_point(end)

    def center(self) -> Point:
        return Point((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2)

    def translate(self, dx: float, dy: float) -> Self:
        self.start.translate(dx, dy)
        self.end.translate(dx, dy)
        return self

    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        c = center or self.center()
        self.start.rotate(angle_deg, c)
        self.end.rotate(angle_deg, c)
        return self

    def scale(self, sx: float, sy: float | None = None, center: PointLike | None = None) -> Self:
        c = center or self.center()
        self.start.scale(sx, sy, c)
        self.end.scale(sx, sy, c)
        return self

    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        self.start.mirror(axis_p1, axis_p2)
        self.end.mirror(axis_p1, axis_p2)
        return self


# ======================================================================
# Circle
# ======================================================================

@dataclass
class Circle(Primitive):
    center_point: Point
    radius: float = 1.0

    def __init__(self, center: PointLike = (0, 0), radius: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.center_point = to_point(center)
        self.radius = radius

    def center(self) -> Point:
        return self.center_point

    def translate(self, dx: float, dy: float) -> Self:
        self.center_point.translate(dx, dy)
        return self

    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        c = center or self.center_point
        self.center_point.rotate(angle_deg, c)
        return self

    def scale(self, sx: float, sy: float | None = None, center: PointLike | None = None) -> Self:
        c = center or self.center_point
        self.center_point.scale(sx, sy, c)
        factor = (sx + (sy or sx)) / 2
        self.radius *= factor
        return self

    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        self.center_point.mirror(axis_p1, axis_p2)
        return self


# ======================================================================
# Rectangle
# ======================================================================

@dataclass
class Rectangle(Primitive):
    pos: Point
    size: Tuple[float, float]
    radius: Optional[float] = None

    def __init__(self, pos: PointLike = (0, 0), size: Tuple[float, float] = (10.0, 10.0), radius: Optional[float] = None, **kwargs):
        super().__init__(**kwargs)
        self.pos = to_point(pos)
        self.size = size
        self.radius = radius

    def center(self) -> Point:
        w, h = self.size
        return Point(self.pos.x + w / 2, self.pos.y + h / 2)

    def translate(self, dx: float, dy: float) -> Self:
        self.pos.translate(dx, dy)
        return self

    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        c = center or self.center()
        self.pos.rotate(angle_deg, c)
        return self

    def scale(self, sx: float, sy: float | None = None, center: PointLike | None = None) -> Self:
        c = center or self.center()
        self.pos.scale(sx, sy, c)
        self.size = (self.size[0] * sx, self.size[1] * (sy or sx))
        return self

    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        self.pos.mirror(axis_p1, axis_p2)
        return self


# ======================================================================
# Polyline
# ======================================================================

@dataclass
class Polyline(Primitive):
    points: List[Point] = field(default_factory=list)
    closed: bool = False

    def __init__(self, points: Sequence[PointLike] | None = None, closed: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.points = [to_point(p) for p in (points or [])]
        self.closed = closed

    def center(self) -> Point:
        if not self.points:
            return Point(0, 0)
        xs, ys = zip(*(p for p in self.points))
        return Point(sum(xs) / len(xs), sum(ys) / len(ys))

    def translate(self, dx: float, dy: float) -> Self:
        for p in self.points:
            p.translate(dx, dy)
        return self

    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        c = center or self.center()
        for p in self.points:
            p.rotate(angle_deg, c)
        return self

    def scale(self, sx: float, sy: float | None = None, center: PointLike | None = None) -> Self:
        c = center or self.center()
        for p in self.points:
            p.scale(sx, sy, c)
        return self

    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        for p in self.points:
            p.mirror(axis_p1, axis_p2)
        return self


# ======================================================================
# Arc
# ======================================================================

@dataclass
class Arc(Primitive):
    center_point: Point
    radius: float = 1.0
    start_angle: float = 0.0
    end_angle: float = 90.0

    def __init__(self, center: PointLike = (0, 0), radius: float = 1.0, start_angle: float = 0.0, end_angle: float = 90.0, **kwargs):
        super().__init__(**kwargs)
        self.center_point = to_point(center)
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def center(self) -> Point:
        return self.center_point

    def translate(self, dx: float, dy: float) -> Self:
        self.center_point.translate(dx, dy)
        return self

    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        c = center or self.center_point
        self.center_point.rotate(angle_deg, c)
        self.start_angle += angle_deg
        self.end_angle += angle_deg
        return self

    def scale(self, sx: float, sy: float | None = None, center: PointLike | None = None) -> Self:
        c = center or self.center_point
        self.center_point.scale(sx, sy, c)
        factor = (sx + (sy or sx)) / 2
        self.radius *= factor
        return self

    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        self.center_point.mirror(axis_p1, axis_p2)
        return self


# ======================================================================
# Text
# ======================================================================

@dataclass
class Text(Primitive):
    pos: Point
    content: str = ""

    def __init__(self, pos: PointLike = (0, 0), content: str = "", **kwargs):
        super().__init__(**kwargs)
        self.pos = to_point(pos)
        self.content = content

    def center(self) -> Point:
        return self.pos

    def translate(self, dx: float, dy: float) -> Self:
        self.pos.translate(dx, dy)
        return self

    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        c = center or self.pos
        self.pos.rotate(angle_deg, c)
        return self

    def scale(self, sx: float, sy: float | None = None, center: PointLike | None = None) -> Self:
        c = center or self.pos
        self.pos.scale(sx, sy, c)
        return self

    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        self.pos.mirror(axis_p1, axis_p2)
        return self


# ======================================================================
# Group
# ======================================================================

@dataclass
class Group(Primitive):
    elements: List[Primitive] = field(default_factory=list)

    def add(self, *elements: Primitive) -> None:
        self.elements.extend(elements)

    def center(self) -> Point:
        if not self.elements:
            return Point(0, 0)
        xs, ys = zip(*(e.center() for e in self.elements))
        return Point(sum(xs) / len(xs), sum(ys) / len(ys))

    def translate(self, dx: float, dy: float) -> Self:
        for e in self.elements:
            e.translate(dx, dy)
        return self

    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        c = center or self.center()
        for e in self.elements:
            e.rotate(angle_deg, c)
        return self

    def scale(self, sx: float, sy: float | None = None, center: PointLike | None = None) -> Self:
        c = center or self.center()
        for e in self.elements:
            e.scale(sx, sy, c)
        return self

    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        for e in self.elements:
            e.mirror(axis_p1, axis_p2)
        return self
