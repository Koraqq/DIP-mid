"""解析使用者輸入的卷積核文字。

格式：一列一行，數字以空白或逗號分隔；也可用分號 ; 分列。
支援全形逗號「，」與全形/Unicode 負號。所有錯誤都會指出是哪一列哪一格。
"""
from __future__ import annotations

import math
import re

import numpy as np

from imagelab.validation.errors import KernelError

MAX_KERNEL_SIZE = 15

_TRANSLATE = str.maketrans({"，": ",", "；": ";", "−": "-", "－": "-", "＋": "+", "　": " "})
_TOKEN_SPLIT = re.compile(r"[,\s]+")


def parse_kernel(text: str | None) -> np.ndarray:
    """文字 -> float64 的 k×k 陣列（k 為奇數）；不合法時拋出 KernelError。"""
    if text is None or not text.strip():
        raise KernelError("請輸入卷積核矩陣（一列一行，數字以空白或逗號分隔）。")

    lines = text.translate(_TRANSLATE).replace(";", "\n").splitlines()
    rows: list[list[float]] = []
    for line in (ln.strip() for ln in lines):
        if not line:
            continue
        row_no = len(rows) + 1
        row: list[float] = []
        for col_no, token in enumerate((t for t in _TOKEN_SPLIT.split(line) if t), start=1):
            try:
                value = float(token)
            except ValueError:
                raise KernelError(f"第 {row_no} 列第 {col_no} 格「{token}」不是有效的數字。") from None
            if not math.isfinite(value):
                raise KernelError(f"第 {row_no} 列第 {col_no} 格「{token}」不是有限數值（NaN 或無限大）。")
            row.append(value)
        rows.append(row)

    first = len(rows[0])
    for idx, row in enumerate(rows, start=1):
        if len(row) != first:
            raise KernelError(
                f"每一列的數字個數必須相同：第 1 列有 {first} 個，第 {idx} 列有 {len(row)} 個。"
            )
    height, width = len(rows), first
    if height != width:
        raise KernelError(f"卷積核必須是方陣，目前是 {height}×{width}。")
    if height % 2 == 0:
        raise KernelError(f"卷積核尺寸必須是奇數（如 3×3、5×5，才有中心點），目前是 {height}×{height}。")
    if height > MAX_KERNEL_SIZE:
        raise KernelError(f"卷積核過大（{height}×{height}），上限為 {MAX_KERNEL_SIZE}×{MAX_KERNEL_SIZE}。")
    return np.array(rows, dtype=np.float64)
