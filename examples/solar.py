from minidraw import Drawing, Group, Style, Circle, Text, Line, Point


def solar_system_demo() -> Drawing:
    d = Drawing()

    # --- Define Sun ---
    center = Point(300, 300, name="sun_center")

    sun = Circle(center, radius=40, style=Style(fill="#FDB813", stroke="#E59400"))
    label_sun = Text(center.above(50), "Sun", style=Style(font_size=14, fill="black", text_anchor="middle"))

    solar_group = Group()
    solar_group.add(sun, label_sun)

    # --- Planets (name, orbit radius, planet radius, color, angle_deg) ---
    planets = [
        ("Mercury", 70, 5, "#b1b1b1", 20),
        ("Venus", 110, 8, "#d9a066", 100),
        ("Earth", 160, 9, "#4fa3f7", 210),
        ("Mars", 210, 7, "#d14b00", 320),
        ("Jupiter", 280, 20, "#e0a96d", 60),
        ("Saturn", 350, 17, "#e6c97f", 150),
        ("Uranus", 420, 13, "#7fd3e6", 250),
        ("Neptune", 480, 13, "#4768f7", 330),
        ("Pluto", 540, 4, "#d2c3b1", 30),
    ]

    # --- Add planets and orbits ---
    for name, orbit_r, planet_r, color, angle in planets:
        # Orbit circle
        orbit = Circle(center, radius=orbit_r, style=Style(stroke="#aaa", fill="none", dash=[3, 3], opacity=0.5))

        # Create a local point relative to the Sun, then rotate around it
        planet_pos = center.right_of(orbit_r)
        planet_pos.rotate(angle)  # ✅ rotate around the parent point (not abs())

        # Planet itself
        planet = Circle(planet_pos, radius=planet_r, style=Style(fill=color, stroke="#333"))

        # Label above planet
        label = Text(planet_pos.above(planet_r + 10), name, style=Style(font_size=10, fill="black", text_anchor="middle"))

        solar_group.add(orbit, planet, label)

    d.add(solar_group)
    return d


if __name__ == "__main__":
    drawing = solar_system_demo()
    drawing.render_to_file("fig/solar_system.svg")
    print("✅ Solar system saved to solar_system.svg")
