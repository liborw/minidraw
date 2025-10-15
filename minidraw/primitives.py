from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Self
from abc import ABC, abstractmethod
import copy

from .transform import rotate_point, scale_point, mirror_point_angle


# ----------------------------------------------------------------------
# Abstract Base Primitive
# ----------------------------------------------------------------------

@dataclass(kw_only=True)
class Primitive(ABC):
    style: Dict[str, Any] = field(default_factory=dict)

    def apply_style(self, inherited: dict[str, Any]) -> dict[str, Any]:
        return {**inherited, **self.style}

    def _maybe_copy(self, copy_: bool) -> Self:
        return copy.deepcopy(self) if copy_ else self

    @abstractmethod
    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self: ...

    @abstractmethod
    def rotate(self, angle_deg: float, center: tuple[float, float] = (0, 0), *, copy: bool = True) -> Self: ...

    @abstractmethod
    def resize(self, scale_x: float, scale_y: float, center: tuple[float, float] = (0, 0), *, copy: bool = True) -> Self: ...

    @abstractmethod
    def mirror(self, point=(0,0), angle: float = 0.0, *, copy: bool = True) -> Self: ...

    @abstractmethod
    def center(self) -> tuple[float, float]:
        """Return the natural geometric center of the primitive."""
        ...

    def scale(self, factor: float, center: tuple[float, float] = (0, 0), *, copy: bool = True) -> Self:
        """Uniform scaling convenience method."""
        return self.resize(factor, factor, center, copy=copy)

    def mirror_vertical(self, x: float = 0.0, *, copy: bool = True) -> Self:
        """Mirror across a vertical line (angle = 90°)."""
        return self.mirror(point=(x, 0), angle=90.0, copy=copy)

    def mirror_horizontal(self, y: float = 0.0, *, copy: bool = True) -> Self:
        """Mirror across a horizontal line (angle = 0°)."""
        return self.mirror(point=(0, y), angle=0.0, copy=copy)


# ----------------------------------------------------------------------
# Concrete Primitives
# ----------------------------------------------------------------------

@dataclass
class Line(Primitive):
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.start = (obj.start[0] + dx, obj.start[1] + dy)
        obj.end = (obj.end[0] + dx, obj.end[1] + dy)
        return obj

    def rotate(self, angle_deg: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.start = rotate_point(obj.start, angle_deg, center)
        obj.end = rotate_point(obj.end, angle_deg, center)
        return obj

    def resize(self, scale_x: float, scale_y: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.start = scale_point(obj.start, scale_x, scale_y, center)
        obj.end = scale_point(obj.end, scale_x, scale_y, center)
        return obj

    def mirror(self, point=(0,0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.start = mirror_point_angle(obj.start, point, angle)
        obj.end = mirror_point_angle(obj.end, point, angle)
        return obj


@dataclass
class Circle(Primitive):
    center: tuple[float, float] = (0, 0)
    radius: float = 1.0

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center = (obj.center[0] + dx, obj.center[1] + dy)
        return obj

    def rotate(self, angle_deg: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center = rotate_point(obj.center, angle_deg, center)
        return obj

    def resize(self, scale_x: float, scale_y: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center = scale_point(obj.center, scale_x, scale_y, center)
        obj.radius *= (scale_x + scale_y) / 2
        return obj

    def mirror(self, point=(0,0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center = mirror_point_angle(obj.center, point, angle)
        return obj


@dataclass
class Rectangle(Primitive):
    pos: tuple[float, float] = (0, 0)
    size: tuple[float, float] = (1, 1)

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = (obj.pos[0] + dx, obj.pos[1] + dy)
        return obj

    def rotate(self, angle_deg: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = rotate_point(obj.pos, angle_deg, center)
        return obj

    def resize(self, scale_x: float, scale_y: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = scale_point(obj.pos, scale_x, scale_y, center)
        obj.size = (obj.size[0] * scale_x, obj.size[1] * scale_y)
        return obj

    def mirror(self, point=(0,0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = mirror_point_angle(obj.pos, point, angle)
        return obj


@dataclass
class Polyline(Primitive):
    points: List[tuple[float, float]] = field(default_factory=list)

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.points = [(x + dx, y + dy) for x, y in obj.points]
        return obj

    def rotate(self, angle_deg: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.points = [rotate_point(p, angle_deg, center) for p in obj.points]
        return obj

    def resize(self, scale_x: float, scale_y: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.points = [scale_point(p, scale_x, scale_y, center) for p in obj.points]
        return obj

    def mirror(self, point=(0,0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.points = [mirror_point_angle(p, point, angle) for p in obj.points]
        return obj


@dataclass
class Arc(Primitive):
    center: tuple[float, float] = (0, 0)
    radius: float = 1.0
    start_angle: float = 0.0
    end_angle: float = 90.0

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center = (obj.center[0] + dx, obj.center[1] + dy)
        return obj

    def rotate(self, angle_deg: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center = rotate_point(obj.center, angle_deg, center)
        obj.start_angle += angle_deg
        obj.end_angle += angle_deg
        return obj

    def resize(self, scale_x: float, scale_y: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center = scale_point(obj.center, scale_x, scale_y, center)
        obj.radius *= (scale_x + scale_y) / 2
        return obj

    def mirror(self, point=(0,0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.center = mirror_point_angle(obj.center, point, angle)
        return obj


@dataclass
class Text(Primitive):
    pos: tuple[float, float] = (0, 0)
    content: str = ""

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = (obj.pos[0] + dx, obj.pos[1] + dy)
        return obj

    def rotate(self, angle_deg: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = rotate_point(obj.pos, angle_deg, center)
        return obj

    def resize(self, scale_x: float, scale_y: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = scale_point(obj.pos, scale_x, scale_y, center)
        return obj

    def mirror(self, point=(0,0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        obj.pos = mirror_point_angle(obj.pos, point, angle)
        return obj


@dataclass
class Group(Primitive):
    elements: List[Primitive | Group] = field(default_factory=list)

    def add(self, element: Primitive | Group) -> None:
        self.elements.append(element)

    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        for e in obj.elements:
            e.translate(dx, dy, copy=False)
        return obj

    def rotate(self, angle_deg: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        for e in obj.elements:
            e.rotate(angle_deg, center, copy=False)
        return obj

    def resize(self, scale_x: float, scale_y: float, center=(0, 0), *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        for e in obj.elements:
            e.resize(scale_x, scale_y, center, copy=False)
        return obj

    def mirror(self, point=(0,0), angle: float = 0.0, *, copy: bool = True) -> Self:
        obj = self._maybe_copy(copy)
        for e in obj.elements:
            e.mirror(point=point, angle=angle, copy=False)
        return obj
