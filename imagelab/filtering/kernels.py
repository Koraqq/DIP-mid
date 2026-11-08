"""預設卷積核與正規化。"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

CUSTOM_LABEL = "自訂（手動輸入）"
_EPS = 1e-12


@dataclass(frozen=True)
class Preset:
    matrix: np.ndarray
    normalize: bool = False
    offset: float = 0.0
    note: str = ""


def _m(rows: list[list[float]]) -> np.ndarray:
    return np.array(rows, dtype=np.float64)


PRESETS: dict[str, Preset] = {
    "Identity 不變": Preset(_m([[0, 0, 0], [0, 1, 0], [0, 0, 0]]), note="輸出等於輸入，PSNR 為 ∞。"),
    "Box 均值模糊 3×3": Preset(_m([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), normalize=True),
    "Gaussian 高斯平滑 3×3": Preset(_m([[1, 2, 1], [2, 4, 2], [1, 2, 1]]), normalize=True),
    "Gaussian 高斯平滑 5×5": Preset(
        _m([[1, 4, 6, 4, 1], [4, 16, 24, 16, 4], [6, 24, 36, 24, 6],
            [4, 16, 24, 16, 4], [1, 4, 6, 4, 1]]), normalize=True),
    "Sharpen 銳化": Preset(_m([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]), note="核總和為 1，亮度不變。"),
    "Emboss 浮雕": Preset(_m([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]), note="核總和為 1。"),
    "Sobel X 垂直邊緣": Preset(_m([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]), offset=128.0,
                              note="核總和為 0，正規化會被略過。"),
    "Sobel Y 水平邊緣": Preset(_m([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]), offset=128.0,
                              note="核總和為 0，正規化會被略過。"),
    "Laplacian 拉普拉斯": Preset(_m([[0, 1, 0], [1, -4, 1], [0, 1, 0]]), offset=128.0,
                                note="核總和為 0，正規化會被略過。"),
}


def matrix_to_text(matrix: np.ndarray) -> str:
    return "\n".join(" ".join(f"{v:g}" for v in row) for row in matrix)


@dataclass(frozen=True)
class NormalizeResult:
    kernel: np.ndarray
    applied: bool
    message: str | None = None


def normalize_kernel(kernel: np.ndarray, enabled: bool) -> NormalizeResult:
    """除以核元素總和，使亮度（直流增益）保持為 1。

    總和為 0（如 Sobel、Laplacian、部分浮雕）時不能除，略過並回報訊息，避免除以零。
    """
    if not enabled:
        return NormalizeResult(kernel, False)
    total = float(kernel.sum())
    if abs(total) < _EPS:
        return NormalizeResult(kernel, False, "核元素總和為 0，已略過正規化（避免除以零）。")
    return NormalizeResult(kernel / total, True)
