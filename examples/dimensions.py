# examples/dimensions_example.py
from minidraw import Drawing, Line, Style
from minidraw.shapes.dimensions import LengthDimension, DimensionStyle


def main():
    # --- Drawing setup ---
    d = Drawing()

    # Base style for geometry
    base_style = Style(stroke="#666", stroke_width=0.6)

    # --- Reference geometry ---
    # Each line exposes .start and .end points we can reference directly.
    base_line = Line((0, 0), (100, 0), style=base_style)
    vertical_line = Line((120, 0), (120, 60), style=base_style)
    angled_line = Line((0, 0), (80, 50), style=base_style)

    # Add base geometry to drawing
    d.add(base_line, vertical_line, angled_line)

    # --- Shared dimension style ---
    dim_style = DimensionStyle(
        units="mm",
        offset=10,              # perpendicular offset from feature
        connection_offset=2,    # small gap before extension starts
        text_offset=4,          # distance of text from dimension line
        arrow_size=4,
        extension=2,
    )

    # --- Create dimensions using point references ---
    dim_h = LengthDimension(base_line.start, base_line.end, dim_style=dim_style)
    dim_v = LengthDimension(vertical_line.start, vertical_line.end, dim_style=dim_style)
    dim_a = LengthDimension(angled_line.start, angled_line.end, dim_style=dim_style)

    # --- Custom labeled dimension (also by reference) ---
    dim_c = LengthDimension(base_line.start, base_line.end.right_of(40), label="Hole spacing", dim_style=dim_style)

    # --- Add dimension elements lazily ---
    for dim in [dim_h, dim_v, dim_a, dim_c]:
        for el in dim.elements():
            d.add(el)

    # --- Render ---
    d.render_to_file("fig/dimensions.svg")
    print("✅ Saved to dimensions.svg")


if __name__ == "__main__":
    main()
