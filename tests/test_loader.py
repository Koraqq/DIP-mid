import numpy as np
import pytest
from PIL import Image

from imagelab.io.loader import ImageLoadError, load_image
from imagelab.io.metadata import get_metadata
from tests.conftest import encode


@pytest.mark.parametrize("fmt", ["PNG", "BMP"])
def test_lossless_formats_roundtrip(random_rgb, fmt):
    out = load_image(encode(random_rgb, fmt))
    assert out.dtype == np.uint8 and out.shape == random_rgb.shape
    assert np.array_equal(out, random_rgb)


def test_jpeg_loads_as_rgb(random_rgb):
    out = load_image(encode(random_rgb, "JPEG"))
    assert out.shape == random_rgb.shape


def test_grayscale_png_becomes_three_channels():
    gray = np.full((10, 12), 100, dtype=np.uint8)
    out = load_image(encode(gray, "PNG"))
    assert out.shape == (10, 12, 3) and (out == 100).all()


def test_rgba_composited_on_white():
    rgba = np.zeros((4, 4, 4), dtype=np.uint8)  # 全透明
    out = load_image(encode(rgba, "PNG"))
    assert (out == 255).all()


def test_empty_and_garbage_raise_friendly_error():
    with pytest.raises(ImageLoadError):
        load_image(b"")
    with pytest.raises(ImageLoadError):
        load_image(b"this is not an image")


def test_unsupported_format_rejected(random_rgb):
    with pytest.raises(ImageLoadError, match="不支援"):
        load_image(encode(random_rgb, "GIF", mode="P"))


def test_too_large_rejected(monkeypatch, random_rgb):
    monkeypatch.setattr("imagelab.io.loader.MAX_PIXELS", 100)
    with pytest.raises(ImageLoadError, match="過大"):
        load_image(encode(random_rgb, "PNG"))


def test_metadata(random_rgb):
    data = encode(random_rgb, "PNG")
    meta = get_metadata(data, "x.png")
    assert (meta.width, meta.height) == (48, 32)
    assert meta.format == "PNG" and meta.channels == 3
    assert meta.file_size_bytes == len(data)
    assert meta.resolution == "48 × 32"
