from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self
import copy

if TYPE_CHECKING:
    from .point import PointLike


class Spatial(ABC):
    """Common interface for all 2D geometric objects that can undergo spatial transforms."""

    # --------------------------------------------------------
    # Abstract transformation API
    # --------------------------------------------------------
    @abstractmethod
    def translate(self, dx: float, dy: float, *, copy: bool = True) -> Self:
        """Translate by (dx, dy)."""
        ...

    @abstractmethod
    def rotate(self, angle_deg: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        """Rotate around a given center."""
        ...

    @abstractmethod
    def resize(self, scale_x: float, scale_y: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        """Scale relative to a given center."""
        ...

    @abstractmethod
    def mirror(self, point: PointLike = (0, 0), angle: float = 0.0, *, copy: bool = True) -> Self:
        """Mirror across a line passing through `point` at `angle` degrees."""
        ...

    # --------------------------------------------------------
    # Common helpers
    # --------------------------------------------------------
    def scale(self, factor: float, center: PointLike | None = None, *, copy: bool = True) -> Self:
        """Uniform scaling."""
        return self.resize(factor, factor, center, copy=copy)

    def mirror_vertical(self, x: float = 0.0, *, copy: bool = True) -> Self:
        """Mirror across a vertical axis (angle = 90°)."""
        return self.mirror(point=(x, 0), angle=90.0, copy=copy)

    def mirror_horizontal(self, y: float = 0.0, *, copy: bool = True) -> Self:
        """Mirror across a horizontal axis (angle = 0°)."""
        return self.mirror(point=(0, y), angle=0.0, copy=copy)

    def _maybe_copy(self, copy_: bool) -> Self:
        return copy.deepcopy(self) if copy_ else self
