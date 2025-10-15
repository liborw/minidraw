from minidraw import Drawing

# Create a new drawing
d = Drawing()

# --- Sun ---
sun = d.circle(
    center=(0, 0),
    radius=20,
    style={
        "fill": "gold",
        "stroke": "orange",
        "stroke-width": 2,
        "opacity": 0.95,
    },
)
d.text((0, 30), "Sun", style={"font-size": 8, "text-anchor": "middle"})

# --- Orbits ---
orbit_style = {
    "stroke": "gray",
    "stroke-width": 0.5,
    "stroke-dasharray": [2, 2],
    "opacity": 0.5,
    "fill": "none",
}
for r in [40, 70, 100]:
    d.circle((0, 0), r, style=orbit_style)

# --- Planets ---
planets = [
    {"name": "Mercury", "radius": 3, "dist": 40, "angle": 45, "color": "#b0b0b0"},
    {"name": "Venus", "radius": 5, "dist": 70, "angle": 120, "color": "#e0b060"},
    {"name": "Earth", "radius": 6, "dist": 100, "angle": 200, "color": "#4a90e2"},
]

for p in planets:
    from math import cos, sin, radians

    x = p["dist"] * cos(radians(p["angle"]))
    y = p["dist"] * sin(radians(p["angle"]))

    d.circle((x, y), p["radius"], style={"fill": p["color"], "stroke": "black"})
    d.text(
        (x, y + p["radius"] + 6),
        p["name"],
        style={
            "font-size": 6,
            "text-anchor": "middle",
            "fill": "black",
        },
    )


d.render_to_file("solar_system.svg")
