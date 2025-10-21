# shapes/dimensions.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Iterable
import math

from ..primitives import Line, Polyline, Text, Primitive
from ..point import Point, PointLike, to_point
from ..style import Style
from .shape import Shape


# ======================================================================
# DimensionStyle
# ======================================================================

@dataclass
class DimensionStyle:
    """Shared geometric and formatting style for all dimension annotations."""

    scale: float = 1.0
    units: Optional[str] = None
    offset: float = 10.0              # perpendicular distance from measured feature
    text_offset: float = 4.0          # label offset from dimension line
    arrow_size: float = 4.0           # arrowhead leg length
    extension: float = 2.0            # how far extension lines overshoot beyond dimension line
    gap: float = 1.0                  # (legacy) reserved for spacing, currently not used
    connection_offset: float = 1.0    # distance from measured point to start of extension line
    precision: int = 1
    text_format: Optional[str] = None
    label_style: Style = field(default_factory=lambda: Style(
        stroke="none", fill="#000", text_anchor="middle"))
    arrow_style: Style = field(default_factory=lambda: Style(
        stroke="#000", stroke_width=0.5))

    def format_label(self, length: float) -> str:
        """Return formatted dimension label string."""
        scaled = length * self.scale
        if self.text_format:
            return self.text_format.format(scaled)
        units = f" {self.units}" if self.units else ""
        return f"{scaled:.{self.precision}f}{units}"


# ======================================================================
# LengthDimension
# ======================================================================

class LengthDimension(Shape):
    """
    Procedural linear dimension between two points with offset,
    extension lines, arrowheads, and label.

    Example (schematic):
          10 mm
    |<------------->|
    |               |
    """

    def __init__(
        self,
        p1: PointLike,
        p2: PointLike,
        label: Optional[str] = None,
        *,
        dim_style: Optional[DimensionStyle] = None,
    ):
        self.p1 = to_point(p1)
        self.p2 = to_point(p2)
        self.label = label
        self.dim_style = dim_style or DimensionStyle()

    # ------------------------------------------------------------------
    # Generate all primitives procedurally
    # ------------------------------------------------------------------
    def elements(self) -> Iterable[Primitive]:
        s = self.dim_style

        # --- Geometry vectors ---
        dx, dy = self.p2.x - self.p1.x, self.p2.y - self.p1.y
        length = math.hypot(dx, dy)
        if length == 0:
            return []

        ux, uy = dx / length, dy / length         # unit vector along measured line
        nx, ny = uy, -ux                          # perpendicular vector (SVG coordinate fix)

        # --- Points for dimension geometry ---
        d1 = Point(self.p1.x + nx * s.offset, self.p1.y + ny * s.offset)
        d2 = Point(self.p2.x + nx * s.offset, self.p2.y + ny * s.offset)

        # --- Extension lines ---
        # Start points offset in the same direction as the arrow line (perpendicular),
        # creating a small gap between the measured geometry and the extension line.
        e1_start = Point(self.p1.x + nx * s.connection_offset, self.p1.y + ny * s.connection_offset)
        e1_end   = Point(d1.x + nx * s.extension, d1.y + ny * s.extension)

        e2_start = Point(self.p2.x + nx * s.connection_offset, self.p2.y + ny * s.connection_offset)
        e2_end   = Point(d2.x + nx * s.extension, d2.y + ny * s.extension)

        # --- Arrows ---
        arrow1 = self._make_arrow(d1, ux, uy, s.arrow_size)
        arrow2 = self._make_arrow(d2, -ux, -uy, s.arrow_size)

        # --- Label ---
        center = Point(
            (d1.x + d2.x) / 2 + nx * s.text_offset,
            (d1.y + d2.y) / 2 + ny * s.text_offset,
        )
        rotation_deg = math.degrees(math.atan2(uy, ux))
        label_text = Text(
            center,
            self.label or s.format_label(length),
            rotation=rotation_deg,
            style=s.label_style,
        )

        # --- Yield all primitives lazily ---
        yield Line(e1_start, e1_end, style=s.arrow_style)
        yield Line(e2_start, e2_end, style=s.arrow_style)
        yield Line(d1, d2, style=s.arrow_style)
        yield from [arrow1, arrow2, label_text]

    # ------------------------------------------------------------------
    # Arrow helper
    # ------------------------------------------------------------------
    def _make_arrow(self, pos: Point, ux: float, uy: float, size: float) -> Polyline:
        """Create a simple V-shaped inward-pointing arrowhead polyline."""
        angle = math.radians(30)
        left_dx = math.cos(angle) * ux - math.sin(angle) * uy
        left_dy = math.sin(angle) * ux + math.cos(angle) * uy
        right_dx = math.cos(-angle) * ux - math.sin(-angle) * uy
        right_dy = math.sin(-angle) * ux + math.cos(-angle) * uy

        left = Point(pos.x + left_dx * size, pos.y + left_dy * size)
        right = Point(pos.x + right_dx * size, pos.y + right_dy * size)
        return Polyline([left, pos, right], closed=False, style=self.dim_style.arrow_style)
