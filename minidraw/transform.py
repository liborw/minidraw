from math import cos, sin, radians

def rotate_point(p: tuple[float, float], angle_deg: float, center: tuple[float, float]) -> tuple[float, float]:
    x, y = p
    cx, cy = center
    angle = radians(angle_deg)
    dx, dy = x - cx, y - cy
    return (
        cx + dx * cos(angle) - dy * sin(angle),
        cy + dx * sin(angle) + dy * cos(angle),
    )

def scale_point(p: tuple[float, float], scale_x: float, scale_y: float, center: tuple[float, float]) -> tuple[float, float]:
    x, y = p
    cx, cy = center
    return (cx + (x - cx) * scale_x, cy + (y - cy) * scale_y)
