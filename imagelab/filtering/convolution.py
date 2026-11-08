"""2D 卷積（純 NumPy 向量化，不使用 cv2.filter2D）。

真正的卷積： out[i, j] = Σ_m Σ_n K[m, n] · x[i − m + c, j − n + c]，c = k // 2。
令 u = k−1−m、v = k−1−n，等價於「把核旋轉 180° 之後做相關（互相關）」：
    out[i, j] = Σ_u Σ_v K'[u, v] · P[i + u, j + v]，K' = K[::-1, ::-1]，P 為補邊後的影像。
迴圈只跑 k² 次（每次是整張影像的向量運算），不逐像素迴圈。
"""
from __future__ import annotations

import numpy as np

PADDING_MODES = {"zero": "constant", "reflect": "reflect", "replicate": "edge"}


def to_uint8(x: np.ndarray) -> np.ndarray:
    """四捨五入並截斷到 [0, 255]。"""
    return np.clip(np.rint(x), 0, 255).astype(np.uint8)


def convolve2d(channel: np.ndarray, kernel: np.ndarray, padding: str = "zero") -> np.ndarray:
    """單通道卷積，回傳與輸入同尺寸的 float64 陣列（尚未截斷）。"""
    if channel.ndim != 2:
        raise ValueError(f"需要 2D 通道，收到 {channel.shape}")
    if kernel.ndim != 2 or kernel.shape[0] != kernel.shape[1] or kernel.shape[0] % 2 == 0:
        raise ValueError(f"核必須是奇數方陣，收到 {kernel.shape}")
    if padding not in PADDING_MODES:
        raise ValueError(f"未知的邊界模式：{padding}")

    k = kernel.shape[0]
    r = k // 2
    h, w = channel.shape
    padded = np.pad(channel.astype(np.float64), r, mode=PADDING_MODES[padding])
    flipped = kernel[::-1, ::-1]

    out = np.zeros((h, w), dtype=np.float64)
    for u in range(k):
        for v in range(k):
            weight = flipped[u, v]
            if weight != 0.0:
                out += weight * padded[u:u + h, v:v + w]
    return out


def apply_filter(rgb: np.ndarray, kernel: np.ndarray, padding: str = "zero",
                 offset: float = 0.0) -> np.ndarray:
    """對 RGB 三通道各自卷積，加上偏移後截斷為 uint8。"""
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"需要 (H, W, 3) 影像，收到 {rgb.shape}")
    channels = [to_uint8(convolve2d(rgb[..., c], kernel, padding) + offset) for c in range(3)]
    return np.stack(channels, axis=-1)
