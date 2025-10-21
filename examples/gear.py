from minidraw import Drawing, Group, Circle, Polyline, Style, Point


def make_gear(center: Point, radius: float, teeth: int, tooth_depth: float = 10.0) -> Group:
    """
    Build a simple 2D gear profile centered at `center`.
    Each tooth is represented as two line segments (up and down) along the circle.
    """
    g = Group()

    # Outer and inner radii
    r_outer = radius + tooth_depth
    r_inner = radius - tooth_depth * 0.4

    # Points around the gear perimeter
    points = []
    for i in range(teeth * 2):
        angle = (i / (teeth * 2)) * 360.0
        r = r_outer if i % 2 == 0 else r_inner
        p = center.right_of(r).rotate(angle, center)
        points.append(p)

    # Close the loop
    gear_profile = Polyline(points, closed=True, style=Style(stroke="#333", fill="#bbb", stroke_width=2))
    g.add(gear_profile)

    # Add hub and outline
    g.add(Circle(center, radius * 0.15, style=Style(fill="#666", stroke="#000")))
    # g.add(Circle(center, radius, style=Style(stroke="#000", fill="none")))

    return g


def gear_pair_demo() -> Drawing:
    """Compose two meshed gears using local reference geometry."""
    d = Drawing()

    # Define centers
    center1 = Point(300, 300, name="gear_A")
    center2 = center1.right_of(180, name="gear_B")

    # Build gears
    gear1 = make_gear(center1, radius=80, teeth=20)
    gear2 = make_gear(center2, radius=60, teeth=15)

    # Counter-rotate the second gear (so the teeth interlock)
    gear2.rotate(180 / 15, center2)

    d.add(gear1, gear2)

    return d


if __name__ == "__main__":
    drawing = gear_pair_demo()
    drawing.render_to_file("fig/gear_pair.svg")
    print("✅ Gear pair saved to gear_pair.svg")
