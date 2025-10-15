from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union, Optional

from .primitives import (
    Primitive, Group, Line, Circle, Rectangle, Polyline, Arc, Text
)
from .render import RenderEngine, SVGRenderEngine


@dataclass
class Drawing:
    """Container for primitives and groups, similar to Diagram."""

    elements: list[Primitive | Group] = field(default_factory=list)
    scale: float = 1.0

    # ------------------------------------------------------------------
    # Element Management
    # ------------------------------------------------------------------
    def add(self, *items: Primitive | Group) -> None:
        """Add one or more primitives or groups."""
        for i in items:
            if isinstance(i, (Primitive, Group)):
                self.elements.append(i)
            else:
                raise TypeError(f"Unsupported type: {type(i)}")

    def clear(self) -> None:
        """Remove all elements from the drawing."""
        self.elements.clear()

    def __iter__(self):
        yield from self.elements

    # ------------------------------------------------------------------
    # Helper Constructors (Fluent API)
    # ------------------------------------------------------------------
    def line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        style: Optional[dict] = None,
    ) -> Line:
        line = Line(start, end, style=style or {})
        self.add(line)
        return line

    def circle(
        self,
        center: tuple[float, float],
        radius: float,
        *,
        style: Optional[dict] = None,
    ) -> Circle:
        c = Circle(center, radius, style=style or {})
        self.add(c)
        return c

    def rectangle(
        self,
        pos: tuple[float, float],
        size: tuple[float, float],
        *,
        style: Optional[dict] = None,
    ) -> Rectangle:
        r = Rectangle(pos, size, style=style or {})
        self.add(r)
        return r

    def polyline(
        self,
        points: list[tuple[float, float]],
        *,
        style: Optional[dict] = None,
    ) -> Polyline:
        p = Polyline(points, style=style or {})
        self.add(p)
        return p

    def arc(
        self,
        center: tuple[float, float],
        radius: float,
        start_angle: float,
        end_angle: float,
        *,
        style: Optional[dict] = None,
    ) -> Arc:
        a = Arc(center, radius, start_angle, end_angle, style=style or {})
        self.add(a)
        return a

    def text(
        self,
        pos: tuple[float, float],
        content: str,
        *,
        style: Optional[dict] = None,
    ) -> Text:
        t = Text(pos, content, style=style or {})
        self.add(t)
        return t

    def group(
        self,
        *elements: Primitive | Group,
        style: Optional[dict] = None,
    ) -> Group:
        g = Group(list(elements), style=style or {})
        self.add(g)
        return g

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_to_file(self, path: str, engine: Union[str, RenderEngine] = "svg") -> None:
        svg_code = self.render(engine)
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg_code)

    def render(self, engine: Union[str, RenderEngine] = "svg") -> str:
        """Render all elements using the selected engine."""
        if isinstance(engine, str):
            if engine == "svg":
                renderer = SVGRenderEngine()
            else:
                raise NotImplementedError(f"Render engine '{engine}' not supported.")
        else:
            renderer = engine

        return renderer.render(self.elements)
