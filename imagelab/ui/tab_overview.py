"""分頁 1：影像預覽與中繼資訊。"""
from __future__ import annotations

import numpy as np
import streamlit as st

from imagelab.io.metadata import ImageMetadata


def render(rgb: np.ndarray, meta: ImageMetadata) -> None:
    left, right = st.columns([3, 2])
    with left:
        st.image(rgb, caption=meta.filename, width="stretch")
    with right:
        st.subheader("影像中繼資訊")
        st.table(
            {
                "項目": ["檔名", "格式", "解析度（寬×高）", "像素總數", "原始色彩模式",
                         "色彩維度（通道數）", "檔案大小"],
                "數值": [meta.filename, meta.format, meta.resolution,
                         f"{meta.width * meta.height:,}（{meta.megapixels:.2f} MP）",
                         f"{meta.mode}（{meta.mode_description}）",
                         str(meta.channels), meta.file_size_text],
            }
        )
        st.caption("後續處理一律先轉為 8-bit RGB（透明背景合成為白色）。")
