from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, TypeAlias

from ..shapes.shape import Shape
from ..primitives import Primitive

Drawable: TypeAlias = "Primitive | Shape | Iterable[Primitive]"


def to_elements(drawable: Drawable) -> Iterable[Primitive]:
    if isinstance(drawable, Shape):
        return drawable.elements()
    elif isinstance(drawable, Primitive):
        return [drawable]
    else:
        return drawable


class Backend(ABC):
    """Abstract base class for all rendering backends."""

    @abstractmethod
    def render_to_string(
        self,
        drawable: Drawable,
    ) -> str:
        """Render primitives or groups and return backend-specific output as a string."""
        raise NotImplementedError(
            f"Backend {self.__class__.__name__} does not support text rendering; use render_to_file instead."
        )

    def render_to_file(
        self,
        path: Path ,
        drawable: Drawable,
    ) -> None:
        """Render primitives or groups to a file.

        By default, this calls `render_to_string` and writes the result to disk.
        Backends that do not produce text output (e.g., raster backends) should
        override this method directly.
        """
        content = self.render_to_string(drawable)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
