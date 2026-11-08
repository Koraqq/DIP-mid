"""人臉偵測共用的資料型別。"""
from __future__ import annotations

import math
from dataclasses import dataclass


class DetectorError(RuntimeError):
    """偵測器無法使用（例如找不到模型檔）；訊息可直接顯示給使用者。"""


@dataclass(frozen=True)
class Detection:
    x: int
    y: int
    w: int
    h: int
    weight: float       # Haar 最後一層的原始權重（levelWeights），無上限、沒有機率意義
    confidence: float   # 由 weight 正規化到 [0, 1) 的信心度

    @property
    def box(self) -> tuple[int, int, int, int]:
        """(x1, y1, x2, y2)"""
        return self.x, self.y, self.x + self.w, self.y + self.h


def normalize_confidence(weight: float) -> float:
    """把 Haar 層級權重壓到 [0, 1)：confidence = 1 − exp(−w / 2)。

    單調遞增：權重越大越可信；w ≤ 0 → 0；w = 2 → 0.63；w = 5 → 0.92。
    這是啟發式的正規化，不是校準過的機率，報告中需註明。
    """
    return 1.0 - math.exp(-max(float(weight), 0.0) / 2.0)
