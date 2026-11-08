"""快取：同一份上傳檔只解碼一次，切換分頁/模式時不重算。"""
from __future__ import annotations

import numpy as np
import streamlit as st

from imagelab.io.loader import load_image
from imagelab.io.metadata import ImageMetadata, get_metadata


@st.cache_data(show_spinner=False, max_entries=8)
def cached_load(data: bytes, filename: str) -> tuple[np.ndarray, ImageMetadata]:
    return load_image(data), get_metadata(data, filename)


@st.cache_data(show_spinner="濾波運算中…", max_entries=16)
def cached_filter(rgb: np.ndarray, kernel: np.ndarray, padding: str, offset: float) -> np.ndarray:
    from imagelab.filtering.convolution import apply_filter

    return apply_filter(rgb, kernel, padding, offset)


@st.cache_data(show_spinner="人臉偵測中…", max_entries=16)
def cached_detect(rgb: np.ndarray, scale_factor: float, min_neighbors: int, min_size: int):
    from imagelab.detection.haar_detector import detect_faces

    return detect_faces(rgb, scale_factor, min_neighbors, min_size)
