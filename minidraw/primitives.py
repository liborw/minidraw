from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from .transform import rotate_point, scale_point
from .style import Style


@dataclass(kw_only=True)
class Primitive:
    """Base class for drawable primitives."""
    style: Style = field(default_factory=Style)

    def apply_style(self, inherited: Style) -> Style:
        """Merge this primitive's style with inherited style."""
        return self.style.merged(inherited)

    # Default transforms (no-op by default, overridden in subclasses)
    def translate(self, dx: float, dy: float) -> None: ...
    def rotate(self, angle_deg: float, center: tuple[float, float]) -> None: ...
    def resize(self, scale_x: float, scale_y: float, center: tuple[float, float]) -> None: ...
    def mirror(self, vertical=False, horizontal=False, center=None) -> None: ...


# -------------------------------------------------------------------
# Primitive Implementations
# -------------------------------------------------------------------

@dataclass
class Line(Primitive):
    start: tuple[float, float] = (0, 0)
    end: tuple[float, float] = (0, 0)

    def translate(self, dx: float, dy: float) -> None:
        self.start = (self.start[0] + dx, self.start[1] + dy)
        self.end = (self.end[0] + dx, self.end[1] + dy)

    def rotate(self, angle_deg: float, center: tuple[float, float]) -> None:
        self.start = rotate_point(self.start, angle_deg, center)
        self.end = rotate_point(self.end, angle_deg, center)

    def resize(self, scale_x: float, scale_y: float, center: tuple[float, float]) -> None:
        self.start = scale_point(self.start, scale_x, scale_y, center)
        self.end = scale_point(self.end, scale_x, scale_y, center)


@dataclass
class Circle(Primitive):
    center: tuple[float, float] = (0, 0)
    radius: float = 1.0

    def translate(self, dx: float, dy: float) -> None:
        self.center = (self.center[0] + dx, self.center[1] + dy)

    def resize(self, scale_x: float, scale_y: float, center: tuple[float, float]) -> None:
        self.center = scale_point(self.center, scale_x, scale_y, center)
        self.radius *= (scale_x + scale_y) / 2


@dataclass
class Rectangle(Primitive):
    pos: tuple[float, float] = (0, 0)
    size: tuple[float, float] = (1, 1)

    def translate(self, dx: float, dy: float) -> None:
        self.pos = (self.pos[0] + dx, self.pos[1] + dy)

    def resize(self, scale_x: float, scale_y: float, center: tuple[float, float]) -> None:
        self.pos = scale_point(self.pos, scale_x, scale_y, center)
        self.size = (self.size[0] * scale_x, self.size[1] * scale_y)


@dataclass
class Polyline(Primitive):
    points: List[tuple[float, float]] = field(default_factory=list)

    def translate(self, dx: float, dy: float) -> None:
        self.points = [(x + dx, y + dy) for x, y in self.points]

    def rotate(self, angle_deg: float, center: tuple[float, float]) -> None:
        self.points = [rotate_point(p, angle_deg, center) for p in self.points]

    def resize(self, scale_x: float, scale_y: float, center: tuple[float, float]) -> None:
        self.points = [scale_point(p, scale_x, scale_y, center) for p in self.points]


@dataclass
class Arc(Primitive):
    center: tuple[float, float] = (0, 0)
    radius: float = 1.0
    start_angle: float = 0.0
    end_angle: float = 90.0

    def translate(self, dx: float, dy: float) -> None:
        self.center = (self.center[0] + dx, self.center[1] + dy)

    def resize(self, scale_x: float, scale_y: float, center: tuple[float, float]) -> None:
        self.center = scale_point(self.center, scale_x, scale_y, center)
        self.radius *= (scale_x + scale_y) / 2


@dataclass
class Text(Primitive):
    pos: tuple[float, float] = (0, 0)
    content: str = ""

    def translate(self, dx: float, dy: float) -> None:
        self.pos = (self.pos[0] + dx, self.pos[1] + dy)


@dataclass
class Group(Primitive):
    elements: List[Primitive | Group] = field(default_factory=list)

    def add(self, element: Primitive | Group) -> None:
        self.elements.append(element)

    def translate(self, dx: float, dy: float) -> None:
        for e in self.elements:
            e.translate(dx, dy)

    def rotate(self, angle_deg: float, center: tuple[float, float]) -> None:
        for e in self.elements:
            e.rotate(angle_deg, center)

    def resize(self, scale_x: float, scale_y: float, center: tuple[float, float]) -> None:
        for e in self.elements:
            e.resize(scale_x, scale_y, center)

    def mirror(self, vertical=False, horizontal=False, center=None) -> None:
        pass  # reserved for future
