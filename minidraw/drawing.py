from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
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
from .point import Point, PointLike
from .style import Style
from .backend import Backend, SVGBackend, PythonBackend


@dataclass
class Drawing:
    """Container for drawable primitives and groups."""

    elements: list[Primitive | Group] = field(default_factory=list)
    scale: float = 1.0
    defautl_style: Style = field(default_factory=Style)

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
    # Fluent Creation API (PointLike-compatible)
    # ------------------------------------------------------------------
    def line(
        self,
        start: PointLike,
        end: PointLike,
        *,
        style: Optional[Style] = None,
    ) -> Line:
        line = Line(start=Point.ensure(start), end=Point.ensure(end), style=style or Style())
        self.add(line)
        return line

    def circle(
        self,
        center: PointLike,
        radius: float,
        *,
        style: Optional[Style] = None,
    ) -> Circle:
        c = Circle(center=Point.ensure(center), radius=radius, style=style or Style())
        self.add(c)
        return c

    def rectangle(
        self,
        pos: PointLike,
        size: tuple[float, float],
        *,
        style: Optional[Style] = None,
    ) -> Rectangle:
        r = Rectangle(pos=Point.ensure(pos), size=size, style=style or Style())
        self.add(r)
        return r

    def polyline(
        self,
        points: list[PointLike],
        *,
        style: Optional[Style] = None,
    ) -> Polyline:
        p = Polyline(points=[Point.ensure(pt) for pt in points], style=style or Style())
        self.add(p)
        return p

    def arc(
        self,
        center: PointLike,
        radius: float,
        start_angle: float,
        end_angle: float,
        *,
        style: Optional[Style] = None,
    ) -> Arc:
        a = Arc(
            center=Point.ensure(center),
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
            style=style or Style(),
        )
        self.add(a)
        return a

    def text(
        self,
        pos: PointLike,
        content: str,
        *,
        style: Optional[Style] = None,
    ) -> Text:
        t = Text(pos=Point.ensure(pos), content=content, style=style or Style())
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
    def render_to_file(self, path: Union[Path,str], engine: Optional[Union[str, Backend]] = None) -> None:
        """Render the drawing to an SVG file."""
        path = Path(path)
        backend = self._to_backend(engine or path)
        backend.render_to_file(path, self.elements)

    def render_to_string(self, engine: str | Backend = "svg") -> str:
        backend = self._to_backend(engine)
        return backend.render_to_string(self.elements)

    def _to_backend(self, engine: str | Backend | Path) -> Backend:

        if isinstance(engine, Backend):
            return engine

        if isinstance(engine, Path):
            engine = engine.suffix

        if engine in ['svg', '.svg']:
            return  SVGBackend(pretty_print=True)
        elif engine in ['python', 'py', '.py']:
            return PythonBackend()
        else:
            raise NotImplementedError(f"Unknown backend: {engine}")


