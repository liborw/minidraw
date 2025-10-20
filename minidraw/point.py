from __future__ import annotations
from typing import TypeAlias, Tuple, Optional
import math

# ------------------------------------------------------------
# Type alias
# ------------------------------------------------------------
PointLike: TypeAlias = "Point | Tuple[float, float]"


class Point:
    """
    Represents a 2D point that can be part of a hierarchical coordinate system.
    All transformations work in local coordinates.
    """

    def __init__(self, x: float, y: float, parent: Optional["Point"] = None, name: Optional[str] = None):
        self.x = x
        self.y = y
        self.parent = parent
        self.name = name

    # ---------- Representation ----------

    def __repr__(self):
        ax, ay = self.abs()
        return f"Point({ax:.3f}, {ay:.3f}, name={self.name!r})"

    def copy(self) -> "Point":
        return Point(self.x, self.y, self.parent, self.name)

    # ---------- Hierarchy helpers ----------

    def ref(self, name: Optional[str] = None) -> "Point":
        """Creates a new point with this point as its local origin."""
        return Point(0, 0, parent=self, name=name)

    def right_of(self, dx: float, name: Optional[str] = None) -> "Point":
        """Creates a point dx units to the right (local)."""
        return Point(dx, 0, parent=self, name=name)

    def left_of(self, dx: float, name: Optional[str] = None) -> "Point":
        """Creates a point dx units to the left (local)."""
        return Point(-dx, 0, parent=self, name=name)

    def above(self, dy: float, name: Optional[str] = None) -> "Point":
        """Creates a point dy units above (local)."""
        return Point(0, dy, parent=self, name=name)

    def below(self, dy: float, name: Optional[str] = None) -> "Point":
        """Creates a point dy units below (local)."""
        return Point(0, -dy, parent=self, name=name)

    def detach(self) -> "Point":
        """
        Breaks the parent link and converts to absolute coordinates.
        """
        ax, ay = self.abs()
        self.x, self.y = ax, ay
        self.parent = None
        return self

    # ---------- Coordinates ----------

    def abs(self) -> Tuple[float, float]:
        """Returns absolute coordinates recursively."""
        if self.parent is None:
            return self.x, self.y
        px, py = self.parent.abs()
        return px + self.x, py + self.y

    # ---------- Local transformations ----------

    def translate(self, dx: float, dy: float):
        """Translates this point locally by (dx, dy)."""
        self.x += dx
        self.y += dy
        return self

    def rotate(self, angle_deg: float, center: Tuple[float, float] = (0.0, 0.0)):
        """Rotates locally around a given center."""
        cx, cy = center
        angle = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        dx, dy = self.x - cx, self.y - cy
        self.x = cx + dx * cos_a - dy * sin_a
        self.y = cy + dx * sin_a + dy * cos_a
        return self

    def scale(self, sx: float, sy: Optional[float] = None, center: Tuple[float, float] = (0.0, 0.0)):
        """Scales locally around a given center."""
        if sy is None:
            sy = sx
        cx, cy = center
        self.x = sx * (self.x - cx) + cx
        self.y = sy * (self.y - cy) + cy
        return self

    def mirror(self, axis_p1: Tuple[float, float], axis_p2: Tuple[float, float]):
        """Mirrors locally around a line defined by two points."""
        x1, y1 = axis_p1
        x2, y2 = axis_p2
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0:
            raise ValueError("Mirror axis points must be distinct")

        length2 = dx * dx + dy * dy
        ux, uy = dx / math.sqrt(length2), dy / math.sqrt(length2)

        vx, vy = self.x - x1, self.y - y1
        proj = vx * ux + vy * uy

        cx, cy = x1 + proj * ux, y1 + proj * uy
        self.x = 2 * cx - self.x
        self.y = 2 * cy - self.y
        return self

    def flip_lr(self):
        """Flips left-right (mirror around vertical axis)."""
        self.x = -self.x
        return self

    def flip_ud(self):
        """Flips up-down (mirror around horizontal axis)."""
        self.y = -self.y
        return self


def to_point(p: Tuple[float, float] | Point) -> Point:
    if isinstance(p, Point):
        return p
    else:
        return Point(p[0], p[1])
