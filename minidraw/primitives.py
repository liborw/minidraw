from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Self
from abc import ABC, abstractmethod
import copy

from .point import Point, PointLike
from .style import Style


# ----------------------------------------------------------------------
# Abstract Base Primitive
# ----------------------------------------------------------------------

@dataclass(kw_only=True)
class Primitive(ABC):
    style: Style = field(default_factory=Style)

    @abstractmethod
    def center(self) -> tuple[float, float]:
        """Return the natural geometric center of the primitive."""
        ...

    @abstractmethod
    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        ...

    @abstractmethod
    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        ...

    @abstractmethod
    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        ...

    @abstractmethod
    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        ...

    # ---------------------------------------------------------------
    # Common helpers
    # ---------------------------------------------------------------
    def _maybe_copy(self, copy_: bool) -> Self:
        return copy.deepcopy(self) if copy_ else self

    def apply_style(self, inherited: Style | None) -> Style:
        """Merge this primitive's style with an inherited style."""
        if inherited is None:
            return self.style
        return self.style.merge(inherited)

    def scale(self, factor: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        """Uniform scaling convenience method."""
        if center is None:
            center = self.center()
        return self.resize(factor, factor, center, copy=copy)

    def mirror_vertical(self, x: float = 0.0, *, copy: bool = True) -> Self:
        """Mirror across a vertical line (angle = 90°)."""
        return self.mirror(point=(x, 0), angle=90.0, copy=copy)

    def mirror_horizontal(self, y: float = 0.0, *, copy: bool = True) -> Self:
        """Mirror across a horizontal line (angle = 0°)."""
        return self.mirror(point=(0, y), angle=0.0, copy=copy)


# ----------------------------------------------------------------------
# Line
# ----------------------------------------------------------------------

@dataclass
class Line(Primitive):
    start: Point
    end: Point

    def __init__(self, start: PointLike = (0, 0), end: PointLike = (0, 0), **kwargs):
        super().__init__(**kwargs)
        self.start = Point(start)
        self.end = Point(end)

    def center(self) -> tuple[float, float]:
        return ((self.start.abs_x + self.end.abs_x) / 2, (self.start.abs_y + self.end.abs_y) / 2)

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.start = obj.start.translated(dx, dy)
        obj.end = obj.end.translated(dx, dy)
        return obj

    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center())
        obj = self._maybe_copy(copy)
        obj.start = obj.start.rotated(angle_deg, c)
        obj.end = obj.end.rotated(angle_deg, c)
        return obj

    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center())
        obj = self._maybe_copy(copy)
        obj.start = obj.start.scaled(scale_x, scale_y, c)
        obj.end = obj.end.scaled(scale_x, scale_y, c)
        return obj

    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.start = obj.start.mirrored(point, angle)
        obj.end = obj.end.mirrored(point, angle)
        return obj


# ----------------------------------------------------------------------
# Circle
# ----------------------------------------------------------------------

@dataclass
class Circle(Primitive):
    center_point: Point
    radius: float = 1.0

    def __init__(self, center: PointLike = (0, 0), radius: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.center_point = Point(center)
        self.radius = radius

    def center(self) -> tuple[float, float]:
        return self.center_point.as_tuple()

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center_point = obj.center_point.translated(dx, dy)
        return obj

    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center_point)
        obj = self._maybe_copy(copy)
        obj.center_point = obj.center_point.rotated(angle_deg, c)
        return obj

    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center_point)
        obj = self._maybe_copy(copy)
        obj.center_point = obj.center_point.scaled(scale_x, scale_y, c)
        obj.radius *= (scale_x + scale_y) / 2
        return obj

    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center_point = obj.center_point.mirrored(point, angle)
        return obj


# ----------------------------------------------------------------------
# Rectangle
# ----------------------------------------------------------------------

@dataclass
class Rectangle(Primitive):
    pos: Point
    size: tuple[float, float] = (1, 1)

    def __init__(self, pos: PointLike = (0, 0), size: tuple[float, float] = (1, 1), **kwargs):
        super().__init__(**kwargs)
        self.pos = Point(pos)
        self.size = size

    def center(self) -> tuple[float, float]:
        w, h = self.size
        x, y = self.pos.as_tuple()
        return (x + w / 2, y + h / 2)

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = obj.pos.translated(dx, dy)
        return obj

    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center())
        obj = self._maybe_copy(copy)
        obj.pos = obj.pos.rotated(angle_deg, c)
        return obj

    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center())
        obj = self._maybe_copy(copy)
        obj.pos = obj.pos.scaled(scale_x, scale_y, c)
        obj.size = (obj.size[0] * scale_x, obj.size[1] * scale_y)
        return obj

    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = obj.pos.mirrored(point, angle)
        return obj


# ----------------------------------------------------------------------
# Polyline
# ----------------------------------------------------------------------

@dataclass
class Polyline(Primitive):
    points: List[Point] = field(default_factory=list)

    def __init__(self, points: List[PointLike] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.points = [Point(p) for p in (points or [])]

    def center(self) -> tuple[float, float]:
        if not self.points:
            return (0, 0)
        xs = [p.abs_x for p in self.points]
        ys = [p.abs_y for p in self.points]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.points = [p.translated(dx, dy) for p in obj.points]
        return obj

    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center())
        obj = self._maybe_copy(copy)
        obj.points = [p.rotated(angle_deg, c) for p in obj.points]
        return obj

    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center())
        obj = self._maybe_copy(copy)
        obj.points = [p.scaled(scale_x, scale_y, c) for p in obj.points]
        return obj

    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.points = [p.mirrored(point, angle) for p in obj.points]
        return obj


# ----------------------------------------------------------------------
# Arc
# ----------------------------------------------------------------------

@dataclass
class Arc(Primitive):
    center_point: Point
    radius: float = 1.0
    start_angle: float = 0.0
    end_angle: float = 90.0

    def __init__(self, center: PointLike = (0, 0), radius: float = 1.0, start_angle: float = 0.0, end_angle: float = 90.0, **kwargs):
        super().__init__(**kwargs)
        self.center_point = Point(center)
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def center(self) -> tuple[float, float]:
        return self.center_point.as_tuple()

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center_point = obj.center_point.translated(dx, dy)
        return obj

    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center_point)
        obj = self._maybe_copy(copy)
        obj.center_point = obj.center_point.rotated(angle_deg, c)
        obj.start_angle += angle_deg
        obj.end_angle += angle_deg
        return obj

    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center_point)
        obj = self._maybe_copy(copy)
        obj.center_point = obj.center_point.scaled(scale_x, scale_y, c)
        obj.radius *= (scale_x + scale_y) / 2
        return obj

    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center_point = obj.center_point.mirrored(point, angle)
        return obj


# ----------------------------------------------------------------------
# Text
# ----------------------------------------------------------------------

@dataclass
class Text(Primitive):
    pos: Point
    content: str = ""

    def __init__(self, pos: PointLike = (0, 0), content: str = "", **kwargs):
        super().__init__(**kwargs)
        self.pos = Point(pos)
        self.content = content

    def center(self) -> tuple[float, float]:
        return self.pos.as_tuple()

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = obj.pos.translated(dx, dy)
        return obj

    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.pos)
        obj = self._maybe_copy(copy)
        obj.pos = obj.pos.rotated(angle_deg, c)
        return obj

    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.pos)
        obj = self._maybe_copy(copy)
        obj.pos = obj.pos.scaled(scale_x, scale_y, c)
        return obj

    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = obj.pos.mirrored(point, angle)
        return obj


# ----------------------------------------------------------------------
# Group
# ----------------------------------------------------------------------

@dataclass
class Group(Primitive):
    elements: List[Primitive | Group] = field(default_factory=list)

    def center(self) -> tuple[float, float]:
        if not self.elements:
            return (0, 0)
        xs, ys = zip(*(e.center() for e in self.elements))
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def add(self, element: Primitive | Group) -> None:
        self.elements.append(element)

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        for e in obj.elements:
            e.translate(dx, dy, copy=False)
        return obj

    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center())
        obj = self._maybe_copy(copy)
        for e in obj.elements:
            e.rotate(angle_deg, c, copy=False)
        return obj

    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        c = Point(center or self.center())
        obj = self._maybe_copy(copy)
        for e in obj.elements:
            e.resize(scale_x, scale_y, c, copy=False)
        return obj

    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        for e in obj.elements:
            e.mirror(point=point, angle=angle, copy=False)
        return obj
