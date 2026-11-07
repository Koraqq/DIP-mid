import io

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def rng():
    return np.random.default_rng(0)


@pytest.fixture
def random_rgb(rng):
    return rng.integers(0, 256, size=(32, 48, 3), dtype=np.uint8)


def encode(arr, fmt, mode=None):
    buf = io.BytesIO()
    img = Image.fromarray(arr) if mode is None else Image.fromarray(arr).convert(mode)
    img.save(buf, format=fmt)
    return buf.getvalue()
