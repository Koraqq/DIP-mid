"""RGB 通道分離。"""
from __future__ import annotations

import numpy as np


def split_rgb(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """回傳 (R, G, B) 三個 2D uint8 陣列。"""
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"需要 (H, W, 3) 的 RGB 陣列，收到 {rgb.shape}")
    return rgb[..., 0], rgb[..., 1], rgb[..., 2]


def tint_channel(channel: np.ndarray, index: int) -> np.ndarray:
    """把單一通道以該色顯示（R 顯示為紅、G 為綠、B 為藍），其餘通道為 0。"""
    out = np.zeros((*channel.shape, 3), dtype=np.uint8)
    out[..., index] = channel
    return out
