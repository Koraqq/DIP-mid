"""快取：同一份上傳檔只解碼一次，切換分頁/模式時不重算。"""
from __future__ import annotations

import numpy as np
import streamlit as st

from imagelab.io.loader import load_image
from imagelab.io.metadata import ImageMetadata, get_metadata


@st.cache_data(show_spinner=False, max_entries=8)
def cached_load(data: bytes, filename: str) -> tuple[np.ndarray, ImageMetadata]:
    return load_image(data), get_metadata(data, filename)
