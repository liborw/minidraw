"""
pose.py — Hierarchical 2D affine pose system.

This module defines a single class, `Pose`, which represents a 2D position,
orientation, and scale — optionally defined relative to another pose.

Each `Pose` stores a local transformation (translation, rotation, and scale)
relative to its parent. The *world* position is computed lazily by recursively
composing transforms from root to leaf.

Transformations are applied in the following **local order**:

    1. Translation is applied first.
    2. Rotation is applied around the local origin or a specified pivot point.
    3. Scaling or mirroring are applied last (also in local space).

This means that `translate()`, `rotate()`, and `scale()` always modify the pose
in its own coordinate frame — not the parent’s — and the order in which they are
called affects the result.

For example:

    >>> import math
    >>> root = Pose()
    >>> arm = root.ref().translate(10.0, 0.0)
    >>> hand = arm.right_of(5.0)
    >>> _ = arm.rotate(math.pi / 2.0, around=(0.0, 0.0))
    >>> tuple(round(v, 3) for v in arm.world())
    (0.0, 10.0, 1.571)
    >>> tuple(round(v, 3) for v in hand.world())
    (0.0, 15.0, 1.571)

Here, `arm` is translated first (to 10 units along X) and then rotated 90°
around its local origin (0, 0). Its child `hand` remains 5 units along the
rotated X axis, producing the final world position `(5.0, 10.0)`.
"""

import math
from typing import Optional, Tuple


class Pose:
    """A 2D affine pose with hierarchical, invertible transformations.
    """

    __slots__ = ("dx", "dy", "dtheta", "sx", "sy", "parent", "name")

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        theta: float = 0.0,
        sx: float = 1.0,
        sy: float = 1.0,
        parent: Optional["Pose"] = None,
        name: Optional[str] = None
    ):
        self.dx = float(x)
        self.dy = float(y)
        self.dtheta = float(theta)
        self.sx = float(sx)
        self.sy = float(sy)
        self.parent = parent
        self.name = name

    # ----------------------------------------------------------------------
    # --- Basic helpers ----------------------------------------------------
    def ref(self) -> "Pose":
        """Return a new pose that references this one.

        >>> root = Pose()
        >>> p = root.ref().translate(10.0, 0.0)
        >>> isinstance(p.parent, Pose)
        True
        >>> root == p.parent
        True
        >>> p.world()
        (10.0, 0.0, 0.0)
        """
        return Pose(parent=self)

    def copy(self) -> "Pose":
        """Return a shallow copy of this pose.

        >>> p = Pose(10.0, 0.0)
        >>> c = p.copy()
        >>> (c.dx, c.dy) == (10.0, 0.0)
        True
        """
        return Pose(self.dx, self.dy, self.dtheta, self.sx, self.sy, self.parent)

    def detach(self) -> "Pose":
        """Create a new independent pose with same world transform.

        >>> p = Pose(10.0, 0.0)
        >>> d = p.detach()
        >>> d.world()
        (10.0, 0.0, 0.0)
        >>> d.parent is None
        True
        """
        x, y, theta = self.world()
        return Pose(x, y, theta, self.sx, self.sy, parent=None)

    # ----------------------------------------------------------------------
    # --- Local transformations (mutating) --------------------------------
    def translate(self, dx: float, dy: float) -> "Pose":
        """Translate locally by (dx, dy).

        >>> p = Pose().translate(3.0, 4.0)
        >>> p.world()
        (3.0, 4.0, 0.0)
        >>> p1 = p.ref().translate(2.0, 0.0)
        >>> p1.world()
        (5.0, 4.0, 0.0)
        >>> _ = p.translate(5.0, 0.0)
        >>> p1.world()
        (10.0, 4.0, 0.0)
        """
        self.dx += float(dx)
        self.dy += float(dy)
        return self

    def rotate(self, dtheta: float, around: Optional[Tuple[float, float]] = None) -> "Pose":
        """Rotate locally by `dtheta` radians, optionally around a local point.

        >>> p0 = Pose(10.0, 0.0)
        >>> p1 = p0.ref().translate(10.0, 0.0)
        >>> tuple(round(v, 3) for v in p1.world())
        (20.0, 0.0, 0.0)
        >>> _ = p0.rotate(math.pi / 2.0)
        >>> tuple(round(v, 3) for v in p0.world())
        (10.0, 0.0, 1.571)
        >>> tuple(round(v, 3) for v in p1.world())
        (10.0, 10.0, 1.571)
        """
        dtheta = float(dtheta)
        if around is None:
            self.dtheta += dtheta
            return self
        ax, ay = float(around[0]), float(around[1])
        self.dx -= ax
        self.dy -= ay
        c, s = math.cos(dtheta), math.sin(dtheta)
        new_dx = self.dx * c - self.dy * s
        new_dy = self.dx * s + self.dy * c
        self.dx, self.dy = new_dx + ax, new_dy + ay
        self.dtheta += dtheta
        return self

    def scale(
        self,
        sx: float,
        sy: Optional[float] = None,
        around: Optional[Tuple[float, float]] = None,
    ) -> "Pose":
        """Scale locally, optionally around a local point.

        >>> p = Pose(10.0, 0.0)
        >>> p = p.scale(0.5, around=(5.0, 0.0))
        >>> round(p.dx, 3)
        7.5
        """
        sx = float(sx)
        sy = float(sy if sy is not None else sx)
        if around is not None:
            ax, ay = float(around[0]), float(around[1])
            self.dx = ax + (self.dx - ax) * sx
            self.dy = ay + (self.dy - ay) * sy
        self.sx *= sx
        self.sy *= sy
        return self

    def mirror(
        self,
        axis: Tuple[float, float] = (1.0, 0.0),
        through: Optional[Tuple[float, float]] = None,
    ) -> "Pose":
        """Mirror across an arbitrary axis.

        >>> p = Pose(10.0, 0.0)
        >>> p = p.mirror(axis=(0.0, 1.0), through=(5.0, 0.0))  # vertical line x=5
        >>> round(p.dx, 3)
        0.0
        """
        nx, ny = float(axis[0]), float(axis[1])
        L = math.hypot(nx, ny)
        if L == 0.0:
            raise ValueError("mirror axis vector cannot be zero")
        nx, ny = nx / L, ny / L

        px, py = (float(through[0]), float(through[1])) if through else (0.0, 0.0)

        # Translate relative to line
        x, y = self.dx - px, self.dy - py

        # Project onto the axis direction
        dot = x * nx + y * ny

        # Compute perpendicular component
        perp_x = x - dot * nx
        perp_y = y - dot * ny

        # Reflect across the axis (invert perpendicular)
        x_ref = x - 2 * perp_x
        y_ref = y - 2 * perp_y

        # Translate back
        self.dx = x_ref + px
        self.dy = y_ref + py

        # Flip rotation angle
        angle_axis = math.atan2(ny, nx)
        self.dtheta = 2.0 * angle_axis - self.dtheta
        self.sx = -self.sx
        return self

    # ----------------------------------------------------------------------
    # --- Hierarchical helpers --------------------------------------------
    def offset(self, dx: float, dy: float, dtheta: float = 0.0) -> "Pose":
        """Create a new pose offset from this one.

        >>> root = Pose()
        >>> p = root.offset(5.0, 0.0)
        >>> round(p.world()[0], 3)
        5.0
        """
        return Pose(float(dx), float(dy), float(dtheta), parent=self)

    def right_of(self, distance: float) -> "Pose":
        """Return a new pose right of this one."""
        return self.ref().translate(float(distance), 0.0)

    def left_of(self, distance: float) -> "Pose":
        """Return a new pose left of this one."""
        return self.ref().translate(-float(distance), 0.0)

    def above(self, distance: float) -> "Pose":
        """Return a new pose above this one."""
        return self.ref().translate(0.0, float(distance))

    def below(self, distance: float) -> "Pose":
        """Return a new pose below this one."""
        return self.ref().translate(0.0, -float(distance))

    # ----------------------------------------------------------------------
    # --- Coordinate space conversion -------------------------------------
    def world(self) -> Tuple[float, float, float]:
        """Return (x, y, theta) in world coordinates.

        >>> p = Pose(10.0, 0.0).rotate(math.pi / 2.0)
        >>> tuple(round(v, 3) for v in p.world())
        (10.0, 0.0, 1.571)
        """
        if self.parent is None:
            return self.dx, self.dy, self.dtheta
        px, py, pθ = self.parent.world()
        lx = self.dx * self.parent.sx
        ly = self.dy * self.parent.sy
        x = px + lx * math.cos(pθ) - ly * math.sin(pθ)
        y = py + lx * math.sin(pθ) + ly * math.cos(pθ)
        θ = pθ + self.dtheta
        return float(x), float(y), float(θ)

    def apply(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """Transform a local point into world coordinates.

        >>> p = Pose(10.0, 0.0).rotate(math.pi / 4.0)
        >>> tuple(round(v, 3) for v in p.apply((5.0, 0.0)))
        (13.536, 3.536)
        """
        px, py, θ = self.world()
        x, y = float(point[0]), float(point[1])
        wx = px + x * math.cos(θ) - y * math.sin(θ)
        wy = py + x * math.sin(θ) + y * math.cos(θ)
        return float(wx), float(wy)

    def to_local(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """Transform a world point into this pose's local space.

        >>> p = Pose(10.0, 0.0).rotate(math.pi / 4.0)
        >>> w = p.apply((5.0, 0.0))
        >>> tuple(round(v, 3) for v in p.to_local(w))
        (5.0, 0.0)
        """
        wx, wy, θ = self.world()
        x, y = float(point[0]), float(point[1])
        dx = x - wx
        dy = y - wy
        c, s = math.cos(-θ), math.sin(-θ)
        lx = dx * c - dy * s
        ly = dx * s + dy * c
        return float(lx), float(ly)

    def to_matrix(self) -> list[list[float]]:
        """Return a 3×3 affine matrix for this pose.

        >>> p = Pose(10.0, 0.0).rotate(math.pi / 2.0)
        >>> m = p.to_matrix()
        >>> all(isinstance(row, list) for row in m)
        True
        """
        x, y, θ = self.world()
        c, s = math.cos(θ), math.sin(θ)
        return [
            [float(c * self.sx), float(-s * self.sy), float(x)],
            [float(s * self.sx), float(c * self.sy), float(y)],
            [0.0, 0.0, 1.0],
        ]

    # ----------------------------------------------------------------------
    def __repr__(self) -> str:
        x, y, θ = self.world()
        return f"Pose(world=({x:.3f}, {y:.3f}, {θ:.3f} rad), local=({self.dx:.3f}, {self.dy:.3f}, {self.dtheta:.3f}))"
