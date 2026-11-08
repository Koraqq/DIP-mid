"""影像品質指標：MSE 與 PSNR（公式推導見 docs/psnr.md）。

    MSE  = (1 / MN) Σ_i Σ_j [ I(i,j) − K(i,j) ]²
    PSNR = 10 · log10( MAX² / MSE ) = 20 · log10(MAX) − 10 · log10(MSE)，8-bit 時 MAX = 255
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from imagelab.color.yuv import rgb_to_gray

MAX_VALUE = 255.0


def mse(a: np.ndarray, b: np.ndarray) -> float:
    """均方誤差。先轉 float64 再相減，避免 uint8 相減溢位（例如 0 − 255 變 1）。"""
    if a.shape != b.shape:
        raise ValueError(f"兩張影像尺寸必須相同：{a.shape} vs {b.shape}")
    diff = a.astype(np.float64) - b.astype(np.float64)
    return float(np.mean(diff * diff))


def psnr_from_mse(mse_value: float, max_value: float = MAX_VALUE) -> float:
    """MSE 為 0（兩圖完全相同）時回傳 ∞。"""
    if mse_value <= 0:
        return math.inf
    return 10.0 * math.log10(max_value ** 2 / mse_value)


def psnr(a: np.ndarray, b: np.ndarray, max_value: float = MAX_VALUE) -> float:
    return psnr_from_mse(mse(a, b), max_value)


@dataclass(frozen=True)
class PsnrReport:
    mse: dict[str, float]    # 鍵：R、G、B、Y
    psnr: dict[str, float]   # 單位 dB，可能為 inf
    psnr_mean: float         # R、G、B 三個通道 PSNR（dB）的算術平均


def psnr_report(original: np.ndarray, filtered: np.ndarray) -> PsnrReport:
    """逐通道（R、G、B）與亮度 Y（BT.601）的 MSE / PSNR，並附三通道平均。"""
    if original.shape != filtered.shape or original.ndim != 3 or original.shape[2] != 3:
        raise ValueError(f"需要兩張相同尺寸的 RGB 影像：{original.shape} vs {filtered.shape}")
    mses: dict[str, float] = {}
    for idx, name in enumerate("RGB"):
        mses[name] = mse(original[..., idx], filtered[..., idx])
    mses["Y"] = mse(rgb_to_gray(original), rgb_to_gray(filtered))
    psnrs = {name: psnr_from_mse(value) for name, value in mses.items()}
    return PsnrReport(mse=mses, psnr=psnrs,
                      psnr_mean=float(np.mean([psnrs["R"], psnrs["G"], psnrs["B"]])))
