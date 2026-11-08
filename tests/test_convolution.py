import numpy as np
import pytest

from imagelab.filtering.convolution import PADDING_MODES, apply_filter, convolve2d, to_uint8
from imagelab.filtering.kernels import PRESETS, normalize_kernel


def naive_convolve(channel, kernel, padding):
    """逐像素、逐元素的教科書定義：out[i,j] = ΣΣ K[m,n]·x[i−m+c, j−n+c]。"""
    k = kernel.shape[0]
    r = k // 2
    p = np.pad(channel.astype(np.float64), r, mode=PADDING_MODES[padding])
    h, w = channel.shape
    out = np.zeros((h, w))
    for i in range(h):
        for j in range(w):
            acc = 0.0
            for m in range(k):
                for n in range(k):
                    acc += kernel[m, n] * p[i + k - 1 - m, j + k - 1 - n]
            out[i, j] = acc
    return out


@pytest.mark.parametrize("padding", ["zero", "reflect", "replicate"])
def test_matches_naive_definition_with_asymmetric_kernels(rng, padding):
    img = rng.integers(0, 256, size=(12, 15), dtype=np.uint8)
    for size in (3, 5):
        kernel = rng.normal(size=(size, size))  # 非對稱：能抓出核沒翻轉的錯誤
        got = convolve2d(img, kernel, padding)
        assert np.allclose(got, naive_convolve(img, kernel, padding), atol=1e-9)


def test_true_convolution_flips_kernel():
    img = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.uint8)
    kernel = np.zeros((3, 3))
    kernel[1, 2] = 1.0  # 中心右側為 1：卷積 => 影像向右平移一格
    got = convolve2d(img, kernel, "zero")
    assert np.array_equal(got, [[0, 1, 2], [0, 4, 5], [0, 7, 8]])


def test_identity_kernel_returns_input(random_rgb):
    identity = PRESETS["Identity 不變"].matrix
    assert np.array_equal(apply_filter(random_rgb, identity, "reflect"), random_rgb)


def test_shape_and_dtype_preserved(random_rgb):
    out = apply_filter(random_rgb, np.ones((5, 5)) / 25, "zero")
    assert out.shape == random_rgb.shape and out.dtype == np.uint8


@pytest.mark.parametrize("padding", ["zero", "reflect", "replicate"])
def test_matches_opencv_filter2d(rng, padding):
    cv2 = pytest.importorskip("cv2")
    border = {"zero": cv2.BORDER_CONSTANT, "reflect": cv2.BORDER_REFLECT_101,
              "replicate": cv2.BORDER_REPLICATE}[padding]
    img = rng.integers(0, 256, size=(20, 25)).astype(np.float64)
    for size in (3, 5):
        kernel = rng.normal(size=(size, size))
        ours = convolve2d(img.astype(np.uint8), kernel, padding)
        # cv2.filter2D 做的是相關，所以餵入翻轉後的核才等於卷積
        ref = cv2.filter2D(np.floor(img), cv2.CV_64F, kernel[::-1, ::-1], borderType=border)
        assert np.allclose(ours, ref, atol=1e-9)


def test_clipping_and_offset():
    img = np.full((5, 5, 3), 50, dtype=np.uint8)
    assert (apply_filter(img, np.array([[2.0]])) == 100).all()
    assert (apply_filter(img, np.array([[10.0]])) == 255).all()   # 上限截斷
    assert (apply_filter(img, np.array([[-1.0]])) == 0).all()     # 下限截斷
    assert (apply_filter(img, np.array([[-1.0]]), offset=128.0) == 78).all()


def test_channels_are_independent():
    img = np.zeros((6, 6, 3), dtype=np.uint8)
    img[..., 0] = 200
    out = apply_filter(img, np.ones((3, 3)) / 9, "replicate")
    assert (out[..., 0] == 200).all() and (out[..., 1:] == 0).all()


def test_normalized_box_keeps_flat_image_flat():
    img = np.full((8, 8, 3), 100, dtype=np.uint8)
    result = normalize_kernel(np.ones((3, 3)), True)
    assert result.applied and abs(result.kernel.sum() - 1.0) < 1e-12
    assert (apply_filter(img, result.kernel, "replicate") == 100).all()


def test_normalize_skips_zero_sum_kernel():
    sobel = PRESETS["Sobel X 垂直邊緣"].matrix
    result = normalize_kernel(sobel, True)
    assert not result.applied and np.array_equal(result.kernel, sobel)
    assert "除以零" in result.message


def test_normalize_disabled_is_noop():
    k = np.ones((3, 3))
    result = normalize_kernel(k, False)
    assert not result.applied and result.message is None and np.array_equal(result.kernel, k)


def test_invalid_kernels_rejected():
    img = np.zeros((6, 6), dtype=np.uint8)
    for bad in (np.ones((2, 2)), np.ones((3, 5)), np.ones(3)):
        with pytest.raises(ValueError):
            convolve2d(img, bad)
    with pytest.raises(ValueError):
        convolve2d(img, np.ones((3, 3)), padding="wrap")


def test_to_uint8_rounds_and_clips():
    assert list(to_uint8(np.array([-5.0, 0.4, 0.6, 254.5, 300.0]))) == [0, 0, 1, 254, 255]


def test_all_presets_are_valid_odd_squares():
    for name, preset in PRESETS.items():
        k = preset.matrix.shape[0]
        assert preset.matrix.shape == (k, k) and k % 2 == 1, name
