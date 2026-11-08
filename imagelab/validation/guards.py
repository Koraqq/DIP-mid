"""核與影像之間的檢查與提醒。"""
from __future__ import annotations

import numpy as np

from imagelab.validation.errors import KernelError

_EPS = 1e-12


def check_kernel_fits_image(kernel: np.ndarray, image_shape: tuple[int, ...]) -> None:
    k = kernel.shape[0]
    h, w = image_shape[:2]
    if k > min(h, w):
        raise KernelError(f"卷積核（{k}×{k}）比影像（{w}×{h}）還大，請縮小核或換一張較大的影像。")


def kernel_warnings(kernel: np.ndarray, normalize_enabled: bool, offset: float) -> list[str]:
    """不致命但值得提醒使用者的狀況。"""
    msgs: list[str] = []
    total = float(kernel.sum())
    if not np.any(kernel):
        msgs.append("核全為 0，濾波結果會是全黑影像。")
    elif abs(total) < _EPS and offset == 0:
        msgs.append("核總和為 0（邊緣偵測類），結果大多接近黑色；可勾選「加 128 偏移」觀察正負響應。")
    elif normalize_enabled and total < 0:
        msgs.append("核總和為負值，正規化會讓影像明暗反轉。")
    return msgs
