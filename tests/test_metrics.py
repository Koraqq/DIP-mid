import math

import numpy as np
import pytest

from imagelab.filtering.metrics import mse, psnr, psnr_from_mse, psnr_report


def test_identical_images_give_infinite_psnr(random_rgb):
    assert mse(random_rgb, random_rgb) == 0.0
    assert math.isinf(psnr(random_rgb, random_rgb))


def test_known_value_mse_one():
    a = np.zeros((4, 4), dtype=np.uint8)
    b = np.ones((4, 4), dtype=np.uint8)
    assert mse(a, b) == 1.0
    assert abs(psnr(a, b) - 20 * math.log10(255)) < 1e-9      # ≈ 48.1308 dB


def test_known_value_mse_hundred():
    assert abs(psnr_from_mse(100.0) - 28.1307) < 1e-3


def test_no_uint8_wraparound():
    a = np.zeros((3, 3), dtype=np.uint8)
    b = np.full((3, 3), 255, dtype=np.uint8)
    assert mse(a, b) == 255.0 ** 2     # 若在 uint8 相減，0 − 255 會變成 1
    assert abs(psnr(a, b)) < 1e-9      # 最差情況 0 dB


def test_symmetric(rng):
    a = rng.integers(0, 256, (10, 10), dtype=np.uint8)
    b = rng.integers(0, 256, (10, 10), dtype=np.uint8)
    assert psnr(a, b) == psnr(b, a)


def test_more_noise_means_lower_psnr(rng, random_rgb):
    def noisy(sigma):
        n = rng.normal(0, sigma, random_rgb.shape)
        return np.clip(random_rgb + n, 0, 255).astype(np.uint8)

    assert psnr(random_rgb, noisy(5)) > psnr(random_rgb, noisy(25))


def test_shape_mismatch_rejected():
    with pytest.raises(ValueError):
        mse(np.zeros((3, 3), dtype=np.uint8), np.zeros((3, 4), dtype=np.uint8))
    with pytest.raises(ValueError):
        psnr_report(np.zeros((3, 3, 3), dtype=np.uint8), np.zeros((3, 4, 3), dtype=np.uint8))


def test_report_fields(random_rgb):
    other = np.clip(random_rgb.astype(int) + 10, 0, 255).astype(np.uint8)
    rep = psnr_report(random_rgb, other)
    assert set(rep.psnr) == {"R", "G", "B", "Y"} and set(rep.mse) == {"R", "G", "B", "Y"}
    expected = np.mean([rep.psnr["R"], rep.psnr["G"], rep.psnr["B"]])
    assert abs(rep.psnr_mean - expected) < 1e-12


def test_report_identical_is_infinite(random_rgb):
    rep = psnr_report(random_rgb, random_rgb)
    assert all(math.isinf(v) for v in rep.psnr.values()) and math.isinf(rep.psnr_mean)
