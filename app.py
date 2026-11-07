"""Image Lab：互動式影像處理與人臉分析工具（Streamlit 進入點）。"""
from __future__ import annotations

import streamlit as st

from imagelab.io.loader import ImageLoadError
from imagelab.ui import tab_color, tab_overview
from imagelab.ui.sidebar import render_sidebar
from imagelab.ui.state import cached_load

st.set_page_config(page_title="Image Lab", page_icon="🖼️", layout="wide")
st.title("🖼️ Image Lab：影像處理與人臉分析")

payload = render_sidebar()
if payload is None:
    st.info("請從左側上傳一張 PNG / JPG / BMP 影像開始。")
    st.stop()

data, filename = payload
try:
    rgb, meta = cached_load(data, filename)
except ImageLoadError as exc:
    st.error(str(exc))
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["影像資訊", "色彩空間與直方圖", "卷積濾波與 PSNR", "人臉偵測"])
with tab1:
    tab_overview.render(rgb, meta)
with tab2:
    tab_color.render(rgb)
with tab3:
    st.info("開發中：自訂卷積核、濾波前後比較與 PSNR。")
with tab4:
    st.info("開發中：人臉偵測。")
