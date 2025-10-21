from minidraw import Drawing, Group, Circle, Line, Style, Point
import math


def make_petal(center: Point, radius: float, count: int = 6, depth: int = 2) -> Group:
    """Recursively build a flower with petals radiating from a center point."""
    g = Group()

    # Center circle
    g.add(Circle(center, radius, style=Style(fill="#fcbf49", stroke="#d88c00")))

    # Stop recursion
    if depth == 0:
        return g

    for i in range(count):
        angle = 360 / count * i

        # Petal center
        petal_center = center.right_of(radius * 1.5).rotate(angle, center.rel())

        # Petal shape
        petal = Circle(
            petal_center,
            radius * 0.5,
            style=Style(fill="#f77f00", stroke="#9e4700")
        )

        # Connect line
        line = Line(center, petal_center, style=Style(stroke="#b5651d", stroke_width=1))

        g.add(line, petal)

        # Recursive inner flower
        sub = make_petal(petal_center, radius * 0.4, count, depth - 1)
        g.add(sub)

    return g


def fractal_flower_demo() -> Drawing:
    """Compose a fractal flower demo with local transforms."""
    d = Drawing()
    center = Point(300, 300)
    flower = make_petal(center, 60, count=8, depth=3)
    d.add(flower)
    return d


if __name__ == "__main__":
    drawing = fractal_flower_demo()
    drawing.render_to_file("fig/fractal_flower.svg")
    print("✅ Fractal flower saved to fractal_flower.svg")

