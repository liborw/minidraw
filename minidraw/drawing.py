from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union, Optional

from .primitives import (
    Primitive,
    Group,
    Line,
    Circle,
    Rectangle,
    Polyline,
    Arc,
    Text,
)
from .style import Style
from .render import RenderEngine, SVGRenderEngine


@dataclass
class Drawing:
    """Container for drawable primitives and groups."""

    elements: list[Primitive | Group] = field(default_factory=list)
    scale: float = 1.0

    # ------------------------------------------------------------------
    # Element Management
    # ------------------------------------------------------------------
    def add(self, *items: Primitive | Group) -> None:
        """Add one or more primitives or groups to the drawing."""
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
    # Fluent Creation API (with typed Style)
    # ------------------------------------------------------------------
    def line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        style: Optional[Style] = None,
    ) -> Line:
        line = Line(start=start, end=end, style=style or Style())
        self.add(line)
        return line

    def circle(
        self,
        center: tuple[float, float],
        radius: float,
        *,
        style: Optional[Style] = None,
    ) -> Circle:
        c = Circle(_center=center, radius=radius, style=style or Style())
        self.add(c)
        return c

    def rectangle(
        self,
        pos: tuple[float, float],
        size: tuple[float, float],
        *,
        style: Optional[Style] = None,
    ) -> Rectangle:
        r = Rectangle(pos=pos, size=size, style=style or Style())
        self.add(r)
        return r

    def polyline(
        self,
        points: list[tuple[float, float]],
        *,
        style: Optional[Style] = None,
    ) -> Polyline:
        p = Polyline(points=points, style=style or Style())
        self.add(p)
        return p

    def arc(
        self,
        center: tuple[float, float],
        radius: float,
        start_angle: float,
        end_angle: float,
        *,
        style: Optional[Style] = None,
    ) -> Arc:
        a = Arc(center=center, radius=radius, start_angle=start_angle, end_angle=end_angle, style=style or Style())
        self.add(a)
        return a

    def text(
        self,
        pos: tuple[float, float],
        content: str,
        *,
        style: Optional[Style] = None,
    ) -> Text:
        t = Text(pos=pos, content=content, style=style or Style())
        self.add(t)
        return t

    def group(
        self,
        *elements: Primitive | Group,
        style: Optional[Style] = None,
    ) -> Group:
        g = Group(elements=list(elements), style=style or Style())
        self.add(g)
        return g

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render_to_file(self, path: str, engine: Union[str, RenderEngine] = "svg", *, pretty: bool = True) -> None:
        """Render the drawing to an SVG file."""
        svg_code = self.render(engine, pretty_print=pretty)
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg_code)

    def render(
        self,
        engine: Union[str, RenderEngine] = "svg",
        *,
        pretty_print: bool = False,
    ) -> str:
        """Render all elements using the selected engine."""
        if isinstance(engine, str):
            if engine.lower() == "svg":
                renderer = SVGRenderEngine()
            else:
                raise NotImplementedError(f"Render engine '{engine}' not supported.")
        else:
            renderer = engine

        return renderer.render(self.elements, pretty_print=pretty_print)
