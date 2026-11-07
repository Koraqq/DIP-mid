"""RGB <-> YUV（BT.601 全範圍，即 JPEG/JFIF 使用的 YCbCr，U=Cb、V=Cr）。

    Y =  0.299    R + 0.587    G + 0.114    B
    U = -0.168736 R - 0.331264 G + 0.5      B + 128
    V =  0.5      R - 0.418688 G - 0.081312 B + 128

反轉換：
    R = Y + 1.402    (V - 128)
    G = Y - 0.344136 (U - 128) - 0.714136 (V - 128)
    B = Y + 1.772    (U - 128)
"""
from __future__ import annotations

import numpy as np

_RGB2YUV = np.array(
    [[0.299, 0.587, 0.114],
     [-0.168736, -0.331264, 0.5],
     [0.5, -0.418688, -0.081312]],
    dtype=np.float64,
)
_OFFSET = np.array([0.0, 128.0, 128.0])


def _to_uint8(x: np.ndarray) -> np.ndarray:
    return np.clip(np.rint(x), 0, 255).astype(np.uint8)


def rgb_to_yuv(rgb: np.ndarray) -> np.ndarray:
    """(H, W, 3) uint8 RGB -> (H, W, 3) uint8 YUV。"""
    yuv = rgb.astype(np.float64) @ _RGB2YUV.T + _OFFSET
    return _to_uint8(yuv)


def yuv_to_rgb(yuv: np.ndarray) -> np.ndarray:
    """(H, W, 3) uint8 YUV -> (H, W, 3) uint8 RGB。"""
    y = yuv[..., 0].astype(np.float64)
    u = yuv[..., 1].astype(np.float64) - 128.0
    v = yuv[..., 2].astype(np.float64) - 128.0
    r = y + 1.402 * v
    g = y - 0.344136 * u - 0.714136 * v
    b = y + 1.772 * u
    return _to_uint8(np.stack([r, g, b], axis=-1))


def split_yuv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """RGB 影像 -> (Y, U, V) 三個 2D uint8 陣列。"""
    yuv = rgb_to_yuv(rgb)
    return yuv[..., 0], yuv[..., 1], yuv[..., 2]


def rgb_to_gray(rgb: np.ndarray) -> np.ndarray:
    """亮度 Y（即灰階圖），與 YUV 的 Y 分量相同。"""
    return split_yuv(rgb)[0]
