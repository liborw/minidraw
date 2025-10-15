from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Union
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from math import sin, cos, radians
from .primitives import Line, Circle, Rectangle, Polyline, Arc, Text, Group, Primitive


class RenderEngine(ABC):
    """Abstract base class for rendering primitive structures."""

    @abstractmethod
    def render(
        self,
        drawable: Primitive | Group | Iterable[Primitive | Group],
        pretty_print: bool = False,
    ) -> str:
        """Render primitives or groups and return SVG as string."""
        ...


# ------------------------------------------------------------
# SVG Renderer
# ------------------------------------------------------------

class SVGRenderEngine(RenderEngine):
    """Render primitives or groups into an SVG string."""

    def render(
        self,
        drawable: Primitive | Group | Iterable[Primitive | Group],
        pretty_print: bool = False,
    ) -> str:
        """Render primitives or groups to an SVG XML string."""
        # Normalize input
        drawables = [drawable] if isinstance(drawable, (Primitive, Group)) else list(drawable)

        # --- Compute bounds ---
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

        # Draw recursively
        for d in drawables:
            self._draw(d, svg, inherited_style={})

        # Convert to string
        svg_bytes = tostring(svg, encoding="utf-8")
        if pretty_print:
            parsed = minidom.parseString(svg_bytes)
            return parsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
        return svg_bytes.decode("utf-8")

    # --------------------------------------------------------
    # Internal recursive draw function
    # --------------------------------------------------------

    def _draw(self, item: Primitive | Group, parent: Element, inherited_style: dict):
        style = item.apply_style(inherited_style)

        def add_common_attributes(attrs: dict[str, str]) -> dict[str, str]:
            """Attach supported style attributes for SVG elements."""
            svg_style = {
                "stroke": style.get("stroke", "black"),
                "stroke-width": str(style.get("stroke-width", 1)),
                "fill": style.get("fill", "none"),
                "opacity": str(style.get("opacity", 1.0)),
            }
            if dash := style.get("stroke-dasharray"):
                svg_style["stroke-dasharray"] = (
                    " ".join(map(str, dash)) if isinstance(dash, (list, tuple)) else str(dash)
                )
            if cap := style.get("stroke-linecap"):
                svg_style["stroke-linecap"] = cap
            if join := style.get("stroke-linejoin"):
                svg_style["stroke-linejoin"] = join
            return {**attrs, **svg_style}

        if isinstance(item, Line):
            SubElement(
                parent,
                "line",
                add_common_attributes(
                    {
                        "x1": str(item.start[0]),
                        "y1": str(item.start[1]),
                        "x2": str(item.end[0]),
                        "y2": str(item.end[1]),
                    }
                ),
            )

        elif isinstance(item, Circle):
            SubElement(
                parent,
                "circle",
                add_common_attributes(
                    {
                        "cx": str(item.center[0]),
                        "cy": str(item.center[1]),
                        "r": str(item.radius),
                    }
                ),
            )

        elif isinstance(item, Rectangle):
            SubElement(
                parent,
                "rect",
                add_common_attributes(
                    {
                        "x": str(item.pos[0]),
                        "y": str(item.pos[1]),
                        "width": str(item.size[0]),
                        "height": str(item.size[1]),
                    }
                ),
            )

        elif isinstance(item, Polyline):
            points_str = " ".join(f"{x},{y}" for x, y in item.points)
            SubElement(
                parent,
                "polyline",
                add_common_attributes({"points": points_str}),
            )

        elif isinstance(item, Arc):
            start_x = item.center[0] + item.radius * cos(radians(item.start_angle))
            start_y = item.center[1] + item.radius * sin(radians(item.start_angle))
            end_x = item.center[0] + item.radius * cos(radians(item.end_angle))
            end_y = item.center[1] + item.radius * sin(radians(item.end_angle))
            large_arc_flag = 1 if abs(item.end_angle - item.start_angle) > 180 else 0
            path_d = (
                f"M {start_x},{start_y} "
                f"A {item.radius},{item.radius} 0 {large_arc_flag},1 {end_x},{end_y}"
            )
            SubElement(parent, "path", add_common_attributes({"d": path_d}))

        elif isinstance(item, Text):
            text_elem = SubElement(
                parent,
                "text",
                add_common_attributes(
                    {
                        "x": str(item.pos[0]),
                        "y": str(item.pos[1]),
                        "font-size": str(style.get("font-size", 10)),
                        "font-family": style.get("font-family", "sans-serif"),
                        "font-weight": style.get("font-weight", "normal"),
                        "font-style": style.get("font-style", "normal"),
                        "text-anchor": style.get("text-anchor", "start"),
                        "dominant-baseline": style.get("dominant-baseline", "baseline"),
                        "fill": style.get("fill", "black"),
                    }
                ),
            )
            text_elem.text = item.content

        elif isinstance(item, Group):
            group_elem = SubElement(parent, "g")
            for e in item.elements:
                self._draw(e, group_elem, item.style)

    # --------------------------------------------------------
    # Bounding Box Computation
    # --------------------------------------------------------

    def _compute_bounds(
        self, elements: Iterable[Primitive | Group]
    ) -> Union[tuple[float, float, float, float], None]:
        """Compute bounding box from all primitives."""
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
