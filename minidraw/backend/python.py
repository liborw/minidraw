from __future__ import annotations
from typing import Iterable, List
from pathlib import Path

from ..primitives import Primitive, Group, Line, Circle, Rectangle, Polyline, Arc, Text
from ..style import Style
from .base import Backend, Drawable, to_elements


class PythonBackend(Backend):
    """Backend that generates runnable Python code reproducing a drawing using absolute coordinates."""

    def __init__(self, ignore_style: bool = False, standalone: bool = True):
        self.ignore_style = ignore_style
        self.standalone = standalone
        self.group_counter = 0

    # ------------------------------------------------------------------
    # Rendering entrypoints
    # ------------------------------------------------------------------
    def render_to_string(self, drawable: Drawable) -> str:

        drawables = to_elements(drawable)
        lines: List[str] = []

        # Header
        if self.standalone:
            lines += [
                "from minidraw import Drawing, Group, Style, Line, Circle, Rectangle, Polyline, Arc, Text",
                "",
                "d = Drawing()",
            ]

        # Body
        for e in drawables:
            lines.extend(self._render_primitive(e, var_prefix="d"))

        # Footer
        if self.standalone:
            lines += ["", "d.render_to_file('output.svg')"]

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Primitive dispatch
    # ------------------------------------------------------------------
    def _render_primitive(self, p: Primitive, var_prefix: str) -> List[str]:
        """Dispatch rendering to the appropriate primitive renderer."""
        if isinstance(p, Group):
            return self._render_group(p, var_prefix)
        if isinstance(p, Line):
            return self._render_line(p, var_prefix)
        if isinstance(p, Circle):
            return self._render_circle(p, var_prefix)
        if isinstance(p, Rectangle):
            return self._render_rectangle(p, var_prefix)
        if isinstance(p, Polyline):
            return self._render_polyline(p, var_prefix)
        if isinstance(p, Arc):
            return self._render_arc(p, var_prefix)
        if isinstance(p, Text):
            return self._render_text(p, var_prefix)
        return []

    # ------------------------------------------------------------------
    # Individual primitive renderers
    # ------------------------------------------------------------------
    def _render_group(self, p: Group, var_prefix: str) -> List[str]:
        self.group_counter += 1
        gname = f"g{self.group_counter}"
        lines: List[str] = []
        style_part = self._style_arg(p.style)
        style_text = f"({style_part})" if style_part else "()"
        lines.append(f"{gname} = Group{style_text}")
        for e in p.elements:
            lines.extend(self._render_primitive(e, var_prefix=gname))
        lines.append(f"{var_prefix}.add({gname})")
        return lines

    def _render_line(self, p: Line, var_prefix: str) -> List[str]:
        x1, y1 = p.start.abs()
        x2, y2 = p.end.abs()
        return [f"{var_prefix}.add(Line(({x1}, {y1}), ({x2}, {y2}){self._style_suffix(p)}))"]

    def _render_circle(self, p: Circle, var_prefix: str) -> List[str]:
        cx, cy = p.center_point.abs()
        return [f"{var_prefix}.add(Circle(({cx}, {cy}), {p.radius}{self._style_suffix(p)}))"]

    def _render_rectangle(self, p: Rectangle, var_prefix: str) -> List[str]:
        x, y = p.pos.abs()
        w, h = p.size
        return [f"{var_prefix}.add(Rectangle(({x}, {y}), ({w}, {h}){self._style_suffix(p)}))"]

    def _render_polyline(self, p: Polyline, var_prefix: str) -> List[str]:
        pts = ", ".join(f"({x}, {y})" for x, y in (pt.abs() for pt in p.points))
        closed_part = f", closed={p.closed}" if p.closed else ""
        return [f"{var_prefix}.add(Polyline([{pts}]{closed_part}{self._style_suffix(p)}))"]

    def _render_arc(self, p: Arc, var_prefix: str) -> List[str]:
        cx, cy = p.center_point.abs()
        return [
            f"{var_prefix}.add(Arc(({cx}, {cy}), {p.radius}, {p.start_angle}, {p.end_angle}{self._style_suffix(p)}))"
        ]

    def _render_text(self, p: Text, var_prefix: str) -> List[str]:
        x, y = p.pos.abs()
        text_value = repr(p.content)
        rotation_part = f", rotation={p.rotation}" if getattr(p, "rotation", 0) else ""
        return [f"{var_prefix}.add(Text(({x}, {y}), {text_value}{rotation_part}{self._style_suffix(p)}))"]

    # ------------------------------------------------------------------
    # Style formatting
    # ------------------------------------------------------------------
    def _style_suffix(self, p: Primitive) -> str:
        if self.ignore_style:
            return ""
        style_str = self._style_arg(p.style)
        return f", style={style_str}" if style_str else ""

    def _style_arg(self, style: Style) -> str:
        if self.ignore_style or style is None:
            return ""
        args = []
        if style.stroke is not None:
            args.append(f"stroke={style.stroke!r}")
        if style.stroke_width is not None:
            args.append(f"stroke_width={style.stroke_width}")
        if style.fill is not None:
            args.append(f"fill={style.fill!r}")
        if style.opacity is not None:
            args.append(f"opacity={style.opacity}")
        if style.dash is not None:
            args.append(f"dash={style.dash}")
        if style.linecap is not None:
            args.append(f"linecap={style.linecap!r}")
        if style.linejoin is not None:
            args.append(f"linejoin={style.linejoin!r}")
        if style.font_size is not None:
            args.append(f"font_size={style.font_size}")
        if style.font_family is not None:
            args.append(f"font_family={style.font_family!r}")
        if style.text_anchor is not None:
            args.append(f"text_anchor={style.text_anchor!r}")
        if not args:
            return ""
        return f"Style({', '.join(args)})"
