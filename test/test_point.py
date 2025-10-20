import math
import pytest
from minidraw.point import Point


def test_basic_hierarchy_and_abs():
    o = Point(0, 0)
    a = o.right_of(10)
    b = a.above(5)
    c = b.left_of(3)

    assert o.abs() == (0, 0)
    assert a.abs() == (10, 0)
    assert b.abs() == (10, 5)
    assert c.abs() == (7, 5)


def test_translate_and_rotate_local():
    p = Point(10, 0)
    p.rotate(90)
    assert p.x == pytest.approx(0)
    assert p.y == pytest.approx(10)

    p.translate(5, -5)
    assert (p.x, p.y) == pytest.approx((5, 5))


def test_scale_and_mirror_local():
    p = Point(2, 3)
    p.scale(2)
    assert (p.x, p.y) == pytest.approx((4, 6))

    p.mirror((0, 0), (0, 1))
    assert (p.x, p.y) == pytest.approx((-4, 6))


def test_flips_lr_ud():
    p = Point(3, 4)
    p.flip_lr()
    assert (p.x, p.y) == pytest.approx((-3, 4))
    p.flip_ud()
    assert (p.x, p.y) == pytest.approx((-3, -4))


def test_ref_and_detach():
    root = Point(0, 0)
    child = root.right_of(10)
    grand = child.above(5)

    assert grand.abs() == pytest.approx((10, 5))
    grand.detach()
    assert grand.parent is None
    assert grand.abs() == pytest.approx((10, 5))


def test_relative_creations():
    root = Point(0, 0)
    p1 = root.right_of(5)
    p2 = root.left_of(5)
    p3 = root.above(3)
    p4 = root.below(2)

    assert p1.abs() == pytest.approx((5, 0))
    assert p2.abs() == pytest.approx((-5, 0))
    assert p3.abs() == pytest.approx((0, 3))
    assert p4.abs() == pytest.approx((0, -2))


def test_chained_transformations():
    p = Point(1, 0)
    p.rotate(90).scale(2).translate(1, 1)
    assert (p.x, p.y) == pytest.approx((1, 3))
