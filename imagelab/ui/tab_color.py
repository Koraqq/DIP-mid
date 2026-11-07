"""分頁 2：色彩空間切換 + 同步直方圖。

影像與直方圖在同一次 render 內由同一份資料算出，因此切換模式時必定同步。
"""
from __future__ import annotations

import numpy as np
import streamlit as st

from imagelab.analysis.histogram import CJK_FONT, compute_histogram, plot_histogram
from imagelab.color.channels import split_rgb, tint_channel
from imagelab.color.yuv import rgb_to_gray, split_yuv

MODES = ["Original（原始）", "RGB 分量", "YUV 分量"]


def render(rgb: np.ndarray) -> None:
    if CJK_FONT is None:
        st.caption("⚠️ 系統未偵測到中文字型，圖表標題改以英文顯示。")
    mode = st.radio("顯示模式", MODES, horizontal=True, key="color_mode")

    if mode == MODES[0]:
        left, right = st.columns(2)
        with left:
            st.image(rgb, caption="原始影像", width="stretch")
        with right:
            gray = compute_histogram(rgb_to_gray(rgb))
            st.pyplot(plot_histogram([("Gray", gray)], title="灰階（亮度）直方圖",
                                     title_en="Gray (luma) histogram"), width="stretch")
            r, g, b = split_rgb(rgb)
            series = [("R", compute_histogram(r)), ("G", compute_histogram(g)),
                      ("B", compute_histogram(b))]
            st.pyplot(plot_histogram(series, title="RGB 疊圖直方圖", overlay=True,
                                     title_en="RGB overlay histogram"), width="stretch")

    elif mode == MODES[1]:
        style = st.radio("通道顯示方式", ["著色（紅/綠/藍）", "灰階"], horizontal=True,
                         key="rgb_style")
        channels = split_rgb(rgb)
        cols = st.columns(3)
        for i, (name, ch) in enumerate(zip("RGB", channels)):
            with cols[i]:
                shown = tint_channel(ch, i) if style.startswith("著色") else ch
                st.image(shown, caption=f"{name} 通道", width="stretch")
                st.pyplot(plot_histogram([(name, compute_histogram(ch))],
                                         title=f"{name} 通道直方圖",
                                         title_en=f"{name} channel histogram"), width="stretch")

    else:
        y, u, v = split_yuv(rgb)
        cols = st.columns(3)
        notes = {"Y": "Y 亮度", "U": "U（Cb）色度", "V": "V（Cr）色度"}
        for col, (name, comp) in zip(cols, zip("YUV", (y, u, v))):
            with col:
                st.image(comp, caption=notes[name], width="stretch")
                st.pyplot(plot_histogram([(name, compute_histogram(comp))],
                                         title=f"{name} 直方圖",
                                         title_en=f"{name} histogram"), width="stretch")
        st.caption("YUV 採 BT.601 全範圍轉換；U、V 以 128 為零點偏移，灰階顯示其數值大小。")
