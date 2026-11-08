"""Haar-Cascade 人臉偵測（OpenCV 內建的 haarcascade_frontalface_default.xml）。

使用 detectMultiScale3(outputRejectLevels=True) 取得每個偵測框的層級權重作為信心度來源。
注意：需要 OpenCV 4.x（5.x 已移除 CascadeClassifier）。
"""
from __future__ import annotations

import os
import threading
from functools import lru_cache

import cv2
import numpy as np

from imagelab.detection.base import Detection, DetectorError, normalize_confidence

CASCADE_FILE = "haarcascade_frontalface_default.xml"
MAX_DETECT_SIDE = 1280   # 超大圖先縮小再偵測，框再換算回原圖座標
_LOCK = threading.Lock()  # CascadeClassifier 不是執行緒安全的，多個使用者連線時需上鎖


@lru_cache(maxsize=1)
def _load_cascade(filename: str = CASCADE_FILE):
    if not hasattr(cv2, "CascadeClassifier"):
        raise DetectorError(
            f"目前的 OpenCV（{cv2.__version__}）不支援 Haar-Cascade，請安裝 opencv-python-headless<5。")
    path = os.path.join(cv2.data.haarcascades, filename)
    cascade = cv2.CascadeClassifier(path)
    if cascade.empty():
        raise DetectorError(f"找不到或無法載入模型檔：{path}")
    return cascade


def _validate(rgb: np.ndarray, scale_factor: float, min_neighbors: int, min_size: int) -> None:
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8:
        raise ValueError(f"需要 (H, W, 3) 的 uint8 RGB 影像，收到 {rgb.shape}、{rgb.dtype}")
    if not scale_factor > 1.0:
        raise ValueError(f"scaleFactor 必須大於 1.0，收到 {scale_factor}")
    if min_neighbors < 1:
        raise ValueError(f"minNeighbors 必須至少為 1，收到 {min_neighbors}")
    if min_size < 1:
        raise ValueError(f"最小人臉尺寸必須至少為 1 像素，收到 {min_size}")


def detect_faces(rgb: np.ndarray, scale_factor: float = 1.1, min_neighbors: int = 5,
                 min_size: int = 30) -> list[Detection]:
    """偵測人臉，回傳依信心度由高到低排序的 Detection 清單（原圖座標）。"""
    _validate(rgb, scale_factor, min_neighbors, min_size)
    cascade = _load_cascade()

    gray = cv2.equalizeHist(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
    h, w = gray.shape
    win_w, win_h = cascade.getOriginalWindowSize()
    if h < win_h or w < win_w:   # 影像比偵測視窗還小，不可能偵測到
        return []

    scale = 1.0
    if max(h, w) > MAX_DETECT_SIDE:
        scale = MAX_DETECT_SIDE / max(h, w)
        gray = cv2.resize(gray, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    min_px = max(1, round(min_size * scale))

    with _LOCK:
        rects, _levels, weights = cascade.detectMultiScale3(
            gray, scaleFactor=scale_factor, minNeighbors=min_neighbors,
            minSize=(min_px, min_px), outputRejectLevels=True)
    if len(rects) == 0:
        return []

    weights = np.asarray(weights, dtype=np.float64).reshape(-1)
    if len(weights) != len(rects):
        weights = np.zeros(len(rects))

    detections = []
    for (x, y, bw, bh), wt in zip(np.asarray(rects).reshape(-1, 4), weights):
        x1, y1 = max(0, round(x / scale)), max(0, round(y / scale))
        x2, y2 = min(w, round((x + bw) / scale)), min(h, round((y + bh) / scale))
        if x2 <= x1 or y2 <= y1:
            continue
        detections.append(Detection(x1, y1, x2 - x1, y2 - y1, float(wt),
                                    normalize_confidence(float(wt))))
    detections.sort(key=lambda d: d.confidence, reverse=True)
    return detections
