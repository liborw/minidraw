import math
from minidraw.point import Point


def almost_equal(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) < tol


def test_hierarchy_and_abs():
    root = Point(10, 10)
    child = root.right_of(5).above(5)
    ax, ay = child.abs()
    assert almost_equal(ax, 15)
    assert almost_equal(ay, 5)  # above → smaller y


def test_ref_and_chain():
    origin = Point(0, 0)
    p1 = origin.right_of(10)
    p2 = p1.above(10)
    assert almost_equal(p2.abs()[0], 10)
    assert almost_equal(p2.abs()[1], -10)
    # moving origin should move p2
    origin.translate(5, 5)
    assert almost_equal(p2.abs()[0], 15)
    assert almost_equal(p2.abs()[1], -5)


def test_translate_local():
    p = Point(0, 0)
    p.translate(10, -5)
    assert almost_equal(p.x, 10)
    assert almost_equal(p.y, -5)


def test_rotate_around_origin():
    p = Point(10, 0)
    p.rotate(90, (0, 0))
    ax, ay = p.abs()
    assert almost_equal(ax, 0)
    assert almost_equal(ay, 10)


def test_rotate_around_point():
    center = Point(5, 0)
    p = Point(10, 0)
    p.rotate(180, center)
    ax, ay = p.abs()
    assert almost_equal(ax, 0)
    assert almost_equal(ay, 0)


def test_scale_relative_to_point():
    p = Point(10, 0)
    pivot = Point(0, 0)
    p.scale(2, 2, pivot)
    ax, ay = p.abs()
    assert almost_equal(ax, 20)
    assert almost_equal(ay, 0)


def test_scale_relative_to_tuple():
    p = Point(5, 5)
    p.scale(2, 2, (0, 0))
    ax, ay = p.abs()
    assert almost_equal(ax, 10)
    assert almost_equal(ay, 10)


def test_mirror_horizontal():
    p = Point(5, 5)
    p.mirror((0, 0), (10, 0))  # mirror across X axis
    ax, ay = p.abs()
    assert almost_equal(ax, 5)
    assert almost_equal(ay, -5)


def test_flip_lr_and_ud():
    p = Point(10, -10)
    p.flip_lr()
    assert almost_equal(p.x, -10)
    p.flip_ud()
    assert almost_equal(p.y, 10)


def test_detach_breaks_parent():
    root = Point(5, 5)
    child = root.right_of(5)
    assert child.parent is root
    child.detach()
    assert child.parent is None
    assert almost_equal(child.x, 10)
    assert almost_equal(child.y, 5)


def test_to_local_point_and_tuple():
    root = Point(10, 10)
    child = root.right_of(5)
    p = Point(20, 0)
    lx, ly = child.to_local(p)
    # absolute p = (20, 0), child.parent.abs() = (10,10)
    assert almost_equal(lx, 10)
    assert almost_equal(ly, -10)
