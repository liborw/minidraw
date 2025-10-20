from minidraw import Drawing, Group, Style, Circle, Text, Line, Point
import math


def solar_system_demo() -> Drawing:
    # Base drawing
    d = Drawing()

    # --- Define Sun ---
    center = Point(200, 200, name="sun_center")

    sun = Circle(center, radius=30, style=Style(fill="#FDB813", stroke="#E59400"))
    label_sun = Text(center.above(50), "Sun", style=Style(font_size=12, fill="black", text_anchor="middle"))

    solar_group = Group(style=Style(stroke="#888", stroke_width=1))
    solar_group.add(sun, label_sun)

    # --- Planets definition (name, orbit_radius, color, angle_deg) ---
    planets = [
        ("Mercury", 50, "#bbb", 30),
        ("Venus", 80, "#d9a066", 120),
        ("Earth", 120, "#4fa3f7", 220),
        ("Mars", 160, "#d14b00", 310),
    ]

    # --- Add planets with orbits ---
    for name, orbit_r, color, angle in planets:
        # Orbit circle
        orbit = Circle(center, radius=orbit_r, style=Style(stroke="#aaa", fill="none", dash=[3, 3]))

        # Base position (right of Sun) then rotate around Sun
        planet_pos = center.right_of(orbit_r, name=name)
        planet_pos.rotate(angle)

        # Planet itself
        planet = Circle(planet_pos, radius=8, style=Style(fill=color, stroke="#333"))

        # Label above planet
        label = Text(planet_pos.above(15), name, style=Style(font_size=10, fill="black", text_anchor="middle", stroke="none"))

        solar_group.add(orbit, planet, label)
    d.add(solar_group)
    return d


if __name__ == "__main__":
    drawing = solar_system_demo()
    drawing.render_to_file("solar_system.svg")
    print("✅ Solar system saved to solar_system.svg")
