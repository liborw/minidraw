from __future__ import annotations
import json
from typing import Iterable
from ..primitives import Line, Circle, Rectangle, Polyline, Arc, Text, Group, Primitive
from ..style import Style
from .base import Backend


class PythonBackend(Backend):
    """Render primitives or groups into equivalent Python Drawing code."""

    def __init__(self, *, use_style: bool = False):
        """
        Parameters
        ----------
        use_style:
            If False, style arguments are omitted from generated code.
        """
        self.use_style = use_style

    def render_to_string(
        self,
        drawable: Primitive | Group | Iterable[Primitive | Group],
    ) -> str:
        drawables = [drawable] if isinstance(drawable, (Primitive, Group)) else list(drawable)

        # If styles are used, import Style in the generated code
        imports = "from minidraw import Drawing, Style" if self.use_style else "from minidraw import Drawing"
        code = [imports, "", "d = Drawing()", ""]
        for d in drawables:
            code.extend(self._emit_item(d, "d", inherited_style=Style()))
        code.append("")
        code.append('d.render_to_file("output.svg")')
        return "\n".join(code)

    # -----------------------------------------------------------
    # Recursive emission
    # -----------------------------------------------------------
    def _emit_item(self, item: Primitive | Group, target: str, inherited_style: Style) -> list[str]:
        style = item.style.merged(inherited_style)

        def fmt(style: Style) -> str:
            if not self.use_style:
                return ""
            return f", style={self._fmt_style(style)}"

        if isinstance(item, Line):
            return [f"{target}.line(({item.start.abs_x:.2f}, {item.start.abs_y:.2f}), "
                    f"({item.end.abs_x:.2f}, {item.end.abs_y:.2f}){fmt(style)})"]

        elif isinstance(item, Circle):
            return [f"{target}.circle(({item.center_point.abs_x:.2f}, {item.center_point.abs_y:.2f}), "
                    f"{item.radius:.2f}{fmt(style)})"]

        elif isinstance(item, Rectangle):
            w, h = item.size
            return [f"{target}.rectangle(({item.pos.abs_x:.2f}, {item.pos.abs_y:.2f}), "
                    f"({w:.2f}, {h:.2f}){fmt(style)})"]

        elif isinstance(item, Polyline):
            pts = ", ".join(f"({p.abs_x:.2f}, {p.abs_y:.2f})" for p in item.points)
            return [f"{target}.polyline([{pts}]{fmt(style)})"]

        elif isinstance(item, Arc):
            return [f"{target}.arc(({item.center_point.abs_x:.2f}, {item.center_point.abs_y:.2f}), "
                    f"{item.radius:.2f}, {item.start_angle:.2f}, {item.end_angle:.2f}{fmt(style)})"]

        elif isinstance(item, Text):
            return [f"{target}.text(({item.pos.abs_x:.2f}, {item.pos.abs_y:.2f}), "
                    f"{repr(item.content)}{fmt(style)})"]

        elif isinstance(item, Group):
            lines = []
            for e in item.elements:
                lines.extend(self._emit_item(e, target, inherited_style=style))
            return lines

        else:
            return [f"# Unsupported element: {type(item).__name__}"]

    # -----------------------------------------------------------
    # Style serialization
    # -----------------------------------------------------------
    def _fmt_style(self, style: Style) -> str:
        """Return a string that reconstructs a Style object in code form."""
        parts: list[str] = []
        for field_name, value in style.__dict__.items():
            if value is None:
                continue
            if isinstance(value, str):
                parts.append(f"{field_name}={repr(value)}")
            elif isinstance(value, list):
                parts.append(f"{field_name}={value}")
            else:
                parts.append(f"{field_name}={value}")
        return f"Style({', '.join(parts)})" if parts else "Style()"
