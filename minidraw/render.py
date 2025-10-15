from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Union
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from math import sin, cos, radians

from .primitives import (
    Primitive,
    Line,
    Circle,
    Rectangle,
    Polyline,
    Arc,
    Text,
    Group,
)
from .style import Style


# ===============================================================
# Abstract Base Renderer
# ===============================================================

class RenderEngine(ABC):
    """Abstract base class for rendering primitives."""

    @abstractmethod
    def render(
        self,
        drawable: Primitive | Group | Iterable[Primitive | Group],
        pretty_print: bool = False,
    ) -> str:
        """Render primitives or groups and return SVG as string."""
        ...


# ===============================================================
# SVG Renderer
# ===============================================================

class SVGRenderEngine(RenderEngine):
    """Render primitives or groups into an SVG string."""

    # -----------------------------------------------------------
    # Public render entry point
    # -----------------------------------------------------------
    def render(
        self,
        drawable: Primitive | Group | Iterable[Primitive | Group],
        pretty_print: bool = False,
    ) -> str:
        """Render primitives or groups to an SVG XML string."""
        # Normalize input
        drawables = [drawable] if isinstance(drawable, (Primitive, Group)) else list(drawable)

        bounds = self._compute_bounds(drawables)
        if bounds:
            min_x, min_y, max_x, max_y = bounds
        else:
            min_x, min_y, max_x, max_y = -10, -10, 110, 110

        width, height = max_x - min_x, max_y - min_y

        svg = Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=str(width),
            height=str(height),
            viewBox=f"{min_x} {min_y} {width} {height}",
        )

        for d in drawables:
            self._draw_item(d, svg, inherited_style=Style())

        # Convert to string
        svg_bytes = tostring(svg, encoding="utf-8")
        if pretty_print:
            parsed = minidom.parseString(svg_bytes)
            return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
        return svg_bytes.decode("utf-8")

    # -----------------------------------------------------------
    # Draw dispatch
    # -----------------------------------------------------------
    def _draw_item(self, item: Primitive | Group, parent: Element, inherited_style: Style) -> None:
        style = item.style.merged(inherited_style)

        if isinstance(item, Line):
            self._draw_line(item, parent, style)
        elif isinstance(item, Circle):
            self._draw_circle(item, parent, style)
        elif isinstance(item, Rectangle):
            self._draw_rectangle(item, parent, style)
        elif isinstance(item, Polyline):
            self._draw_polyline(item, parent, style)
        elif isinstance(item, Arc):
            self._draw_arc(item, parent, style)
        elif isinstance(item, Text):
            self._draw_text(item, parent, style)
        elif isinstance(item, Group):
            self._draw_group(item, parent, style)

    # -----------------------------------------------------------
    # Individual drawing methods
    # -----------------------------------------------------------

    def _draw_line(self, item: Line, parent: Element, style: Style) -> None:
        attrs = {
            "x1": str(item.start[0]),
            "y1": str(item.start[1]),
            "x2": str(item.end[0]),
            "y2": str(item.end[1]),
            "stroke": style.stroke or "black",
            "stroke-width": str(style.stroke_width),
            "opacity": str(style.opacity),
        }
        if style.dash:
            attrs["stroke-dasharray"] = " ".join(map(str, style.dash))
        if style.linecap:
            attrs["stroke-linecap"] = style.linecap
        if style.linejoin:
            attrs["stroke-linejoin"] = style.linejoin
        SubElement(parent, "line", attrs)

    def _draw_circle(self, item: Circle, parent: Element, style: Style) -> None:
        SubElement(
            parent,
            "circle",
            {
                "cx": str(item.center[0]),
                "cy": str(item.center[1]),
                "r": str(item.radius),
                "stroke": style.stroke or "black",
                "stroke-width": str(style.stroke_width),
                "fill": style.fill or "none",
                "opacity": str(style.opacity),
            },
        )

    def _draw_rectangle(self, item: Rectangle, parent: Element, style: Style) -> None:
        SubElement(
            parent,
            "rect",
            {
                "x": str(item.pos[0]),
                "y": str(item.pos[1]),
                "width": str(item.size[0]),
                "height": str(item.size[1]),
                "stroke": style.stroke or "black",
                "stroke-width": str(style.stroke_width),
                "fill": style.fill or "none",
                "opacity": str(style.opacity),
            },
        )

    def _draw_polyline(self, item: Polyline, parent: Element, style: Style) -> None:
        points_str = " ".join(f"{x},{y}" for x, y in item.points)
        attrs = {
            "points": points_str,
            "stroke": style.stroke or "black",
            "stroke-width": str(style.stroke_width),
            "fill": style.fill or "none",
            "opacity": str(style.opacity),
        }
        if style.dash:
            attrs["stroke-dasharray"] = " ".join(map(str, style.dash))
        SubElement(parent, "polyline", attrs)

    def _draw_arc(self, item: Arc, parent: Element, style: Style) -> None:
        start_x = item.center[0] + item.radius * cos(radians(item.start_angle))
        start_y = item.center[1] + item.radius * sin(radians(item.start_angle))
        end_x = item.center[0] + item.radius * cos(radians(item.end_angle))
        end_y = item.center[1] + item.radius * sin(radians(item.end_angle))
        large_arc_flag = 1 if abs(item.end_angle - item.start_angle) > 180 else 0

        path_d = (
            f"M {start_x},{start_y} "
            f"A {item.radius},{item.radius} 0 {large_arc_flag},1 {end_x},{end_y}"
        )

        SubElement(
            parent,
            "path",
            {
                "d": path_d,
                "stroke": style.stroke or "black",
                "stroke-width": str(style.stroke_width),
                "fill": style.fill or "none",
                "opacity": str(style.opacity),
            },
        )

    def _draw_text(self, item: Text, parent: Element, style: Style) -> None:
        text_elem = SubElement(
            parent,
            "text",
            {
                "x": str(item.pos[0]),
                "y": str(item.pos[1]),
                "font-size": str(style.font_size or 10),
                "font-family": style.font_family or "sans-serif",
                "text-anchor": style.text_anchor or "start",
                "fill": style.fill or "black",
                "opacity": str(style.opacity),
            },
        )
        text_elem.text = item.content

    def _draw_group(self, item: Group, parent: Element, inherited_style: Style) -> None:
        group_elem = SubElement(parent, "g")
        for e in item.elements:
            self._draw_item(e, group_elem, inherited_style=item.style.merged(inherited_style))

    # -----------------------------------------------------------
    # Bounding box computation
    # -----------------------------------------------------------
    def _compute_bounds(
        self, elements: Iterable[Primitive | Group]
    ) -> Union[tuple[float, float, float, float], None]:
        xs, ys = [], []

        def collect(item: Primitive | Group):
            if isinstance(item, Line):
                xs.extend([item.start[0], item.end[0]])
                ys.extend([item.start[1], item.end[1]])
            elif isinstance(item, Circle):
                cx, cy, r = *item.center, item.radius
                xs.extend([cx - r, cx + r])
                ys.extend([cy - r, cy + r])
            elif isinstance(item, Rectangle):
                x, y = item.pos
                w, h = item.size
                xs.extend([x, x + w])
                ys.extend([y, y + h])
            elif isinstance(item, Polyline):
                for x, y in item.points:
                    xs.append(x)
                    ys.append(y)
            elif isinstance(item, Arc):
                cx, cy, r = *item.center, item.radius
                xs.extend([cx - r, cx + r])
                ys.extend([cy - r, cy + r])
            elif isinstance(item, Text):
                x, y = item.pos
                xs.append(x)
                ys.append(y)
            elif isinstance(item, Group):
                for e in item.elements:
                    collect(e)

        for el in elements:
            collect(el)

        if not xs or not ys:
            return None

        margin = 10
        return (
            min(xs) - margin,
            min(ys) - margin,
            max(xs) + margin,
            max(ys) + margin,
        )
