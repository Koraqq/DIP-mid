import numpy as np

from imagelab.color.channels import split_rgb, tint_channel
from imagelab.color.yuv import rgb_to_gray, rgb_to_yuv, split_yuv, yuv_to_rgb


def test_split_rgb(random_rgb):
    r, g, b = split_rgb(random_rgb)
    assert r.shape == random_rgb.shape[:2]
    assert np.array_equal(np.stack([r, g, b], -1), random_rgb)


def test_tint_only_keeps_one_channel(random_rgb):
    r, _, _ = split_rgb(random_rgb)
    t = tint_channel(r, 0)
    assert np.array_equal(t[..., 0], r) and (t[..., 1:] == 0).all()


def test_gray_pixels_have_neutral_chroma():
    gray = np.full((5, 5, 3), 90, dtype=np.uint8)
    y, u, v = split_yuv(gray)
    assert (y == 90).all() and (u == 128).all() and (v == 128).all()


def test_known_primaries():
    red = np.array([[[255, 0, 0]]], dtype=np.uint8)
    y, u, v = split_yuv(red)
    assert (int(y[0, 0]), int(u[0, 0]), int(v[0, 0])) == (76, 85, 255)


def test_roundtrip_error_small(random_rgb):
    back = yuv_to_rgb(rgb_to_yuv(random_rgb))
    assert np.abs(back.astype(int) - random_rgb.astype(int)).max() <= 3


def test_gray_equals_y(random_rgb):
    assert np.array_equal(rgb_to_gray(random_rgb), split_yuv(random_rgb)[0])
