"""在影像上繪製邊界框、編號與信心度（標籤用 ASCII，因 OpenCV 無法繪製中文）。"""
from __future__ import annotations

import cv2
import numpy as np

from imagelab.detection.base import Detection

_FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_detections(rgb: np.ndarray, detections: list[Detection],
                    color: tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """回傳標註後的副本（不修改輸入）。線寬與字體大小隨影像尺寸縮放。"""
    out = np.ascontiguousarray(rgb.copy())
    longest = max(out.shape[:2])
    thickness = max(2, round(longest / 300))
    font_scale = max(0.5, longest / 1000)
    for i, d in enumerate(detections, start=1):
        cv2.rectangle(out, (d.x, d.y), (d.x + d.w, d.y + d.h), color, thickness)
        label = f"#{i} {d.confidence:.2f}"
        (tw, th), _ = cv2.getTextSize(label, _FONT, font_scale, 1)
        top = max(d.y - th - 8, 0)   # 框貼近影像上緣時，標籤仍留在影像內
        cv2.rectangle(out, (d.x, top), (d.x + tw + 6, top + th + 8), color, -1)
        cv2.putText(out, label, (d.x + 3, top + th + 2), _FONT, font_scale, (0, 0, 0), 1,
                    cv2.LINE_AA)
    return out
