import math

from antsim.core.vector import Vec2, wrap_to_pi


def test_add_sub_scalar():
    assert Vec2(1, 2) + Vec2(3, 4) == Vec2(4, 6)
    assert Vec2(3, 4) - Vec2(1, 1) == Vec2(2, 3)
    assert Vec2(1, 2) * 2 == Vec2(2, 4)
    assert 2 * Vec2(1, 2) == Vec2(2, 4)


def test_length_and_normalize():
    assert Vec2(3, 4).length() == 5.0
    assert Vec2(0, 0).normalized() == Vec2(0, 0)
    normalized = Vec2(0, 5).normalized()
    assert math.isclose(normalized.x, 0.0)
    assert math.isclose(normalized.y, 1.0)


def test_from_angle_and_angle_roundtrip():
    for angle in (0.0, 1.0, -2.0, math.pi / 3):
        v = Vec2.from_angle(angle)
        assert math.isclose(v.angle(), angle, abs_tol=1e-9)
        assert math.isclose(v.length(), 1.0, abs_tol=1e-9)


def test_rotated_by_quarter_turn():
    rotated = Vec2(1, 0).rotated(math.pi / 2)
    assert math.isclose(rotated.x, 0.0, abs_tol=1e-9)
    assert math.isclose(rotated.y, 1.0, abs_tol=1e-9)


def test_wrap_to_pi():
    assert math.isclose(wrap_to_pi(3 * math.pi), math.pi)
    assert math.isclose(wrap_to_pi(-3 * math.pi), math.pi)
    assert math.isclose(wrap_to_pi(0.5), 0.5)
