"""側邊欄：影像上傳。"""
from __future__ import annotations

import streamlit as st

from imagelab.io.loader import SUPPORTED_EXTENSIONS


def render_sidebar() -> tuple[bytes, str] | None:
    """回傳 (檔案 bytes, 檔名)；尚未上傳則回傳 None。"""
    with st.sidebar:
        st.header("影像輸入")
        uploaded = st.file_uploader(
            "上傳影像（PNG / JPG / BMP）",
            type=list(SUPPORTED_EXTENSIONS),
            help="依檔案內容判斷格式；單張上限 25 百萬像素。",
        )
        st.caption("四個功能分頁共用同一張影像。")
    if uploaded is None:
        return None
    return uploaded.getvalue(), uploaded.name
