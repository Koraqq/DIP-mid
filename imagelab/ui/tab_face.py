"""分頁 4：人臉偵測（Haar-Cascade）。"""
from __future__ import annotations

import numpy as np
import streamlit as st

from imagelab.detection.base import DetectorError
from imagelab.detection.draw import draw_detections
from imagelab.ui.state import cached_detect

MAX_CROPS = 12


def render(rgb: np.ndarray) -> None:
    left, right = st.columns([1, 2])
    with left:
        st.subheader("偵測參數")
        scale_factor = st.slider("scaleFactor（影像金字塔縮放比）", 1.02, 1.5, 1.10, 0.01,
                                 help="越接近 1 搜尋越細、越慢，也可能偵測到更多；越大越快但可能漏臉。")
        min_neighbors = st.slider("minNeighbors（需要的鄰近候選框數）", 1, 12, 5,
                                  help="越大越嚴格（誤判少、可能漏臉）；越小越寬鬆（容易出現誤判）。")
        min_size = st.slider("最小人臉尺寸（像素）", 10, 300, 30, 5,
                             help="小於此尺寸的臉會被忽略。")
        show_crops = st.checkbox("顯示每張人臉的裁切圖", value=True)
        st.caption("模型：OpenCV Haar-Cascade（haarcascade_frontalface_default），適合正臉；"
                   "側臉、強烈遮擋、失焦的臉可能偵測不到。")

    try:
        detections = cached_detect(rgb, scale_factor, min_neighbors, min_size)
    except DetectorError as exc:
        with right:
            st.error(str(exc))
        return

    with right:
        c1, c2 = st.columns(2)
        c1.metric("偵測到的人臉數", len(detections))
        c2.metric("最高信心度", f"{detections[0].confidence:.2f}" if detections else "—")
        st.image(draw_detections(rgb, detections), caption="偵測結果（綠框：#編號 信心度）",
                 width="stretch")

        if not detections:
            st.info("沒有偵測到人臉。可以試試：降低 minNeighbors、縮小 scaleFactor、"
                    "調低最小人臉尺寸；或換一張人臉較大、較正面的影像。")
            return

        st.table({
            "#": list(range(1, len(detections) + 1)),
            "位置 (x, y)": [f"({d.x}, {d.y})" for d in detections],
            "大小 (w×h)": [f"{d.w}×{d.h}" for d in detections],
            "信心度": [f"{d.confidence:.3f}" for d in detections],
            "原始層級權重": [f"{d.weight:.3f}" for d in detections],
        })
        with st.expander("信心度如何計算？"):
            st.markdown(
                "Haar-Cascade 由多層（stage）分類器串接而成，`detectMultiScale3` 會回傳每個偵測框"
                "最後一層的**層級權重**，權重越大代表通過越多、越強的檢驗。"
                "此權重沒有上限、也不是機率，因此本工具用單調函數正規化到 0–1："
            )
            st.latex(r"\mathrm{confidence}=1-e^{-w/2}")
            st.caption("這是啟發式正規化，用於比較同一張影像中各個偵測框的相對可信度，不代表真實機率。")

        if show_crops:
            st.subheader("人臉裁切")
            shown = detections[:MAX_CROPS]
            cols = st.columns(min(len(shown), 6))
            for i, d in enumerate(shown):
                crop = rgb[d.y:d.y + d.h, d.x:d.x + d.w]
                cols[i % len(cols)].image(crop, caption=f"#{i + 1}  {d.confidence:.2f}",
                                          width="stretch")
            if len(detections) > MAX_CROPS:
                st.caption(f"僅顯示前 {MAX_CROPS} 張。")
