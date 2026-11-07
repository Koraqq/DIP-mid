"""強度直方圖：橫軸像素強度 0–255，縱軸像素數量。

中文字型：匯入時自動偵測系統上的 CJK 字型並設為優先字型；
偵測不到時，圖表標題改用英文（title_en），避免出現方框。
"""
from __future__ import annotations

import matplotlib
import numpy as np
from matplotlib import font_manager
from matplotlib.figure import Figure

CHANNEL_COLORS = {"R": "#d62728", "G": "#2ca02c", "B": "#1f77b4",
                  "Y": "#444444", "U": "#8c564b", "V": "#9467bd", "Gray": "#444444"}

# 依常見度排序：Windows → macOS → Linux/雲端（fonts-noto-cjk）→ 其他
_CJK_CANDIDATES = [
    "Microsoft JhengHei", "Microsoft YaHei", "PingFang TC", "Heiti TC",
    "Noto Sans CJK TC", "Noto Sans TC", "Noto Sans CJK JP", "Noto Sans CJK SC",
    "Source Han Sans TC", "Taipei Sans TC Beta", "WenQuanYi Zen Hei",
    "WenQuanYi Micro Hei", "SimHei", "Arial Unicode MS",
]


def _detect_cjk_font() -> str | None:
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in _CJK_CANDIDATES:
        if name in installed:
            return name
    return None


CJK_FONT: str | None = _detect_cjk_font()
if CJK_FONT:
    matplotlib.rcParams["font.family"] = "sans-serif"
    matplotlib.rcParams["font.sans-serif"] = [CJK_FONT, *matplotlib.rcParams["font.sans-serif"]]
matplotlib.rcParams["axes.unicode_minus"] = False  # 避免負號變方框


def _ascii_only(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) < 128).strip()


def _resolve_title(title: str, title_en: str | None) -> str:
    if not title or CJK_FONT:
        return title
    return title_en if title_en is not None else _ascii_only(title)


def compute_histogram(channel: np.ndarray) -> np.ndarray:
    """回傳長度 256 的計數陣列，counts[i] = 強度為 i 的像素數。"""
    if channel.dtype != np.uint8:
        raise ValueError(f"直方圖需要 uint8 資料，收到 {channel.dtype}")
    return np.bincount(channel.ravel(), minlength=256)


def plot_histogram(series: list[tuple[str, np.ndarray]], title: str = "", overlay: bool = False,
                   figsize: tuple[float, float] = (4.2, 2.6),
                   title_en: str | None = None) -> Figure:
    """繪製一條或多條直方圖。

    series: [(標籤, counts), ...]；標籤 'R'/'G'/'B'/'Y'/'U'/'V'/'Gray' 會套用對應顏色。
    overlay=True 時多條疊在同一張圖（用於 RGB 疊圖）。
    title_en: 系統無中文字型時改用的英文標題。
    """
    fig = Figure(figsize=figsize, dpi=110)
    ax = fig.subplots()
    x = np.arange(256)
    for label, counts in series:
        color = CHANNEL_COLORS.get(label, "#555555")
        if overlay:
            ax.fill_between(x, counts, step="mid", alpha=0.35, color=color, label=label)
            ax.step(x, counts, where="mid", color=color, linewidth=0.8)
        else:
            ax.bar(x, counts, width=1.0, color=color, label=label)
    ax.set_xlim(0, 255)
    ax.set_xlabel("Pixel intensity (0–255)")
    ax.set_ylabel("Pixel count")
    ax.set_title(_resolve_title(title, title_en), fontsize=10)
    if overlay and len(series) > 1:
        ax.legend(fontsize=8, frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig
