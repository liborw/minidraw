from minidraw import Drawing, Group, Circle, Rectangle, Line, Text, Style

# ------------------------------------------------------------
# Logo parameters
# ------------------------------------------------------------
accent = "#ff6f00"
gray = "#333333"
light = "#cccccc"

# ------------------------------------------------------------
# Create drawing and group for symbol
# ------------------------------------------------------------
d = Drawing()
symbol = Group()

# Base construction square and circle
square = Rectangle((0, 0), (80, 80), style=Style(stroke=gray, stroke_width=2, fill="none"))
circle = Circle((40, 40), 36, style=Style(stroke=accent, stroke_width=2, fill="none"))

# Construction guides (light gray)
guide_h = Line((0, 40), (80, 40), style=Style(stroke=light, stroke_width=1))
guide_v = Line((40, 0), (40, 80), style=Style(stroke=light, stroke_width=1))

# Stylized "M" inside the shape
m_left = Line((20, 60), (35, 20), style=Style(stroke=accent, stroke_width=3))
m_right = Line((45, 20), (60, 60), style=Style(stroke=accent, stroke_width=3))
m_middle = Line((35, 20), (45, 20), style=Style(stroke=accent, stroke_width=3))

# Add elements to symbol
gsymbol_elements = [circle, guide_h, guide_v, m_left, m_middle, m_right]
symbol.add(*gsymbol_elements)

# Slight rotation for dynamic feel
symbol.rotate(-10, (40, 40))

# ------------------------------------------------------------
# Add text next to the symbol
# ------------------------------------------------------------
text = Text((40, 100), "minidraw", style=Style(stroke=gray, fill=gray, font_size=20, font_family="monospace", text_anchor="middle"))

# ------------------------------------------------------------
# Assemble final drawing
# ------------------------------------------------------------
d.add(square, symbol, text)

# Export to SVG
d.render_to_file("fig/logo.svg")
