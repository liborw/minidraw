from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Self, Tuple

from minidraw.point import PointLike


class Spatial(ABC):
    """
    Common interface for all 2D geometric objects that can undergo spatial transformations.
    All transformations mutate the object in place.
    """

    # --------------------------------------------------------
    # Abstract transformation API
    # --------------------------------------------------------
    @abstractmethod
    def translate(self, dx: float, dy: float) -> Self:
        """Translate locally by (dx, dy)."""
        ...

    @abstractmethod
    def rotate(self, angle_deg: float, center: PointLike | None = None) -> Self:
        """Rotate around a given center."""
        ...

    @abstractmethod
    def scale(
        self, sx: float, sy: float | None = None, center: PointLike | None = None
    ) -> Self:
        """Scale around a given center."""
        ...

    @abstractmethod
    def mirror(self, axis_p1: PointLike, axis_p2: PointLike) -> Self:
        """Mirror across a line defined by two points (axis_p1 → axis_p2)."""
        ...

    # --------------------------------------------------------
    # Convenience helpers
    # --------------------------------------------------------
    def flip_lr(self) -> Self:
        """Flip left–right (mirror around the vertical axis through origin)."""
        return self.mirror((-1e6, 0), (1e6, 0))

    def flip_ud(self) -> Self:
        """Flip up–down (mirror around the horizontal axis through origin)."""
        return self.mirror((0, -1e6), (0, 1e6))
