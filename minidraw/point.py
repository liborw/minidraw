from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Self, TypeAlias, Tuple

# ------------------------------------------------------------
# Type alias
# ------------------------------------------------------------
PointLike: TypeAlias = "Point | Tuple[float, float]"


@dataclass
class Point:
    """A hierarchical 2D point that can be defined relative to another point."""

    x: float = 0.0
    y: float = 0.0
    parent: Optional[Self] = None

    # --------------------------------------------------------
    # Construction helper
    # --------------------------------------------------------
    @staticmethod
    def ensure(value: PointLike) -> Point:
        """Ensure that a value is a Point."""
        if isinstance(value, Point):
            return value
        if isinstance(value, tuple) and len(value) == 2:
            return Point(*value)
        raise TypeError(f"Expected Point or (x, y) tuple, got {type(value).__name__}")

    # --------------------------------------------------------
    # Coordinate accessors
    # --------------------------------------------------------
    @property
    def abs_x(self) -> float:
        return self.x + (self.parent.abs_x if self.parent else 0)

    @property
    def abs_y(self) -> float:
        return self.y + (self.parent.abs_y if self.parent else 0)

    def as_tuple(self) -> tuple[float, float]:
        return (self.abs_x, self.abs_y)

    # --------------------------------------------------------
    # Relative transform
    # --------------------------------------------------------
    def translated(self, dx: float, dy: float) -> Self:
        """Return a new point defined relative to this one."""
        return type(self)(dx, dy, parent=self)

    # --------------------------------------------------------
    # Utility
    # --------------------------------------------------------
    def __iter__(self):
        yield self.abs_x
        yield self.abs_y

    def __repr__(self) -> str:
        if self.parent:
            return f"Point({self.x:+.2f}, {self.y:+.2f}, rel→{repr(self.parent)})"
        return f"Point({self.x:.2f}, {self.y:.2f})"
