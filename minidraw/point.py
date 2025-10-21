from __future__ import annotations
from typing import TypeAlias, Tuple, Optional, Self
import math

# ------------------------------------------------------------
# Type alias
# ------------------------------------------------------------
PointLike: TypeAlias = "Point | Tuple[float, float]"


class Point:
    """
    Represents a 2D point that can be part of a hierarchical coordinate system.
    All transformations operate in local coordinates, but may use global pivots.
    """

    def __init__(self, x: float, y: float, parent: Optional[Self] = None, name: Optional[str] = None):
        self.x = x
        self.y = y
        self.parent = parent
        self.name = name

    # --------------------------------------------------------
    # Representation
    # --------------------------------------------------------
    def __repr__(self):
        ax, ay = self.abs()
        return f"Point({ax:.3f}, {ay:.3f}, name={self.name!r})"

    def copy(self) -> Self:
        return type(self)(self.x, self.y, self.parent, self.name)

    # --------------------------------------------------------
    # Hierarchy helpers
    # --------------------------------------------------------
    def ref(self, name: Optional[str] = None) -> Self:
        """Create a new point with this point as its local origin."""
        return type(self)(0, 0, parent=self, name=name)

    def right_of(self, dx: float, name: Optional[str] = None) -> Self:
        """Create a point dx units to the right (local)."""
        return type(self)(dx, 0, parent=self, name=name)

    def left_of(self, dx: float, name: Optional[str] = None) -> Self:
        """Create a point dx units to the left (local)."""
        return type(self)(-dx, 0, parent=self, name=name)

    def above(self, dy: float, name: Optional[str] = None) -> Self:
        """Create a point dy units above (local)."""
        return type(self)(0, -dy, parent=self, name=name)

    def below(self, dy: float, name: Optional[str] = None) -> Self:
        """Create a point dy units below (local)."""
        return type(self)(0, dy, parent=self, name=name)

    def detach(self) -> Self:
        """Break the parent link and convert to absolute coordinates."""
        ax, ay = self.abs()
        self.x, self.y = ax, ay
        self.parent = None
        return self

    # --------------------------------------------------------
    # Coordinate access
    # --------------------------------------------------------
    def rel(self) -> Tuple[float, float]:
        """Return local coordinates (relative to parent)."""
        return self.x, self.y

    def abs(self) -> Tuple[float, float]:
        """Return absolute coordinates recursively."""
        if self.parent is None:
            return self.x, self.y
        px, py = self.parent.abs()
        return px + self.x, py + self.y

    # --------------------------------------------------------
    # Coordinate conversions
    # --------------------------------------------------------
    def to_local(self, ref: PointLike) -> Tuple[float, float]:
        """
        Express `ref` (tuple or Point) in this point's *local coordinate system*.

        If `ref` is a tuple, it's treated as absolute coordinates.
        If `ref` is a Point, its absolute position is computed via .abs().
        """
        # 1. Get absolute position of ref
        if isinstance(ref, Point):
            rx, ry = ref.abs()
        else:
            rx, ry = ref

        # 2. Get absolute position of this point's parent
        if self.parent is not None:
            px, py = self.parent.abs()
            return rx - px, ry - py
        else:
            return rx, ry

    # --------------------------------------------------------
    # Transformations
    # --------------------------------------------------------
    def translate(self, dx: float, dy: float) -> Self:
        """Translate locally by (dx, dy)."""
        self.x += dx
        self.y += dy
        return self

    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        """Rotate locally around a given pivot (Point or tuple)."""
        if center is not None:
            cx, cy = self.to_local(center)
        else:
            cx, cy = (0, 0)
        angle = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        dx, dy = self.x - cx, self.y - cy
        self.x = cx + dx * cos_a - dy * sin_a
        self.y = cy + dx * sin_a + dy * cos_a
        return self

    def scale(self, sx: float, sy: Optional[float] = None, center: PointLike | None = None) -> Self:
        """Scale locally around a given pivot (Point or tuple)."""
        if sy is None:
            sy = sx
        if center is not None:
            cx, cy = self.to_local(center)
        else:
            cx, cy = (0, 0)
        self.x = sx * (self.x - cx) + cx
        self.y = sy * (self.y - cy) + cy
        return self

    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        """Mirror locally around a line defined by two points (can be Point or tuple)."""
        x1, y1 = self.to_local(axis_p1)
        x2, y2 = self.to_local(axis_p2)

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

    def flip_lr(self) -> Self:
        """Flip left-right (mirror around vertical axis)."""
        self.x = -self.x
        return self

    def flip_ud(self) -> Self:
        """Flip up-down (mirror around horizontal axis)."""
        self.y = -self.y
        return self


# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------
def to_point(p: Tuple[float, float] | Point) -> Point:
    """Convert tuple or Point to Point (no parent linkage)."""
    if isinstance(p, Point):
        return p
    else:
        return Point(p[0], p[1])
