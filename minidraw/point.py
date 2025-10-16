from __future__ import annotations
from dataclasses import dataclass
from typing import Self, TypeAlias, Tuple
from math import sin, cos, radians
from .spatial import Spatial

# ------------------------------------------------------------
# Type alias
# ------------------------------------------------------------
PointLike: TypeAlias = "Point | Tuple[float, float]"


@dataclass
class Point(Spatial):
    """A simple 2D point supporting direct affine transformations."""

    x: float = 0.0
    y: float = 0.0

    # --------------------------------------------------------
    # Construction
    # --------------------------------------------------------
    def __init__(self, x: float = 0.0, y: float = 0):
        self.x = x
        self.y = y

    # --------------------------------------------------------
    # Coordinate accessors
    # --------------------------------------------------------
    def as_tuple(self) -> tuple[float, float]:
        """Return the point as a tuple (x, y)."""
        return (self.x, self.y)

    # --------------------------------------------------------
    # Spatial transformations
    # --------------------------------------------------------
    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        """Translate by (dx, dy)."""
        obj = self._maybe_copy(copy)
        obj.x = obj.x + dx
        obj.y = obj.y + dy
        return obj

    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        """Rotate around a given center (defaults to origin)."""

        if center is None:
            return self._maybe_copy(copy)

        center_point = to_point(center)
        center_x, center_y = center_point.as_tuple()

        dx = self.x - center_x
        dy = self.y - center_y
        a = radians(angle_deg)

        rotated_x = dx * cos(a) - dy * sin(a)
        rotated_y = dx * sin(a) + dy * cos(a)

        obj = self._maybe_copy(copy)
        obj.x = center_x + rotated_x
        obj.y = center_y + rotated_y
        return obj

    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        """Scale relative to a given center (defaults to origin)."""
        if center is None:
            center_x = 0.0
            center_y = 0.0
        else:
            center_point = to_point(center)
            center_x, center_y = center_point.as_tuple()

        dx = self.x - center_x
        dy = self.y - center_y

        obj = self._maybe_copy(copy)
        obj.x = center_x + dx * scale_x
        obj.y = center_y + dy * scale_y
        return obj

    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        """Mirror across a line passing through `point` at `angle` degrees."""
        mirror_point = Point(point)
        px, py = mirror_point.as_tuple()

        a = radians(angle)
        cos_a = cos(a)
        sin_a = sin(a)

        dx = self.x - px
        dy = self.y - py

        # rotate to align mirror line with x-axis
        dx_rot = dx * cos_a + dy * sin_a
        dy_rot = -dx * sin_a + dy * cos_a

        # reflect across x-axis (invert y)
        dy_rot = -dy_rot

        # rotate back
        new_x = px + dx_rot * cos_a - dy_rot * sin_a
        new_y = py + dx_rot * sin_a + dy_rot * cos_a

        obj = self._maybe_copy(copy)
        obj.x = new_x
        obj.y = new_y
        return obj

    # --------------------------------------------------------
    # Utility
    # --------------------------------------------------------
    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return f"Point({self.x:.2f}, {self.y:.2f})"


def to_point(p: Tuple[float, float] | Point) -> Point:
    if isinstance(p, Point):
        return p
    else:
        return Point(p[0], p[1])
