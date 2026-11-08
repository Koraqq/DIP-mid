"""分頁 3：自訂卷積核空間濾波 + PSNR 量化評估。"""
from __future__ import annotations

import math

import numpy as np
import streamlit as st

from imagelab.filtering.kernels import CUSTOM_LABEL, PRESETS, matrix_to_text, normalize_kernel
from imagelab.filtering.metrics import psnr_report
from imagelab.ui.state import cached_filter
from imagelab.validation.errors import KernelError
from imagelab.validation.guards import check_kernel_fits_image, kernel_warnings
from imagelab.validation.matrix_parser import parse_kernel

PADDING_LABELS = {"zero": "補零（zero）", "reflect": "鏡射（reflect）",
                  "replicate": "複製邊緣（replicate）"}
DEFAULT_PRESET = "Gaussian 高斯平滑 3×3"


def _apply_preset() -> None:
    preset = PRESETS.get(st.session_state["preset_name"])
    if preset is None:  # 選「自訂」時保留使用者目前輸入
        return
    st.session_state["kernel_text"] = matrix_to_text(preset.matrix)
    st.session_state["normalize"] = preset.normalize
    st.session_state["offset128"] = preset.offset > 0


def _ensure_defaults() -> None:
    if "kernel_text" not in st.session_state:
        st.session_state["preset_name"] = DEFAULT_PRESET
        st.session_state.setdefault("padding", "reflect")
        st.session_state.setdefault("show_diff", True)
        _apply_preset()


def _fmt_db(value: float) -> str:
    return "∞" if math.isinf(value) else f"{value:.2f} dB"


def render(rgb: np.ndarray) -> None:
    _ensure_defaults()
    left, right = st.columns([1, 2])
    kernel = None

    with left:
        st.subheader("濾波設定")
        st.selectbox("預設範本", [*PRESETS, CUSTOM_LABEL], key="preset_name",
                     on_change=_apply_preset)
        note = PRESETS.get(st.session_state["preset_name"])
        if note and note.note:
            st.caption(note.note)
        st.text_area("卷積核矩陣（奇數方陣；一列一行，數字以空白或逗號分隔，也可用 ; 分列）",
                     key="kernel_text", height=180)
        st.checkbox("正規化（除以核元素總和）", key="normalize",
                    help="使輸出平均亮度與輸入相同。總和為 0 的核會自動略過，避免除以零。")
        st.selectbox("邊界處理", list(PADDING_LABELS), format_func=PADDING_LABELS.get,
                     key="padding")
        st.checkbox("輸出加 128 偏移（邊緣、浮雕類建議開啟）", key="offset128")
        st.checkbox("顯示差異圖（×4 放大）", key="show_diff")

        try:
            kernel = parse_kernel(st.session_state["kernel_text"])
            check_kernel_fits_image(kernel, rgb.shape)
        except KernelError as exc:
            st.error(str(exc))
            kernel = None

        if kernel is not None:
            offset = 128.0 if st.session_state["offset128"] else 0.0
            norm = normalize_kernel(kernel, st.session_state["normalize"])
            if norm.message:
                st.warning(norm.message)
            for msg in kernel_warnings(kernel, st.session_state["normalize"], offset):
                st.warning(msg)
            k = norm.kernel.shape[0]
            st.caption(f"實際使用的核（{k}×{k}{'，已正規化' if norm.applied else ''}）")
            st.table([[f"{v:.4g}" for v in row] for row in norm.kernel])

    with right:
        if kernel is None:
            st.info("請先修正左側的核矩陣，修正後會自動重新計算。")
            return

        filtered = cached_filter(rgb, norm.kernel, st.session_state["padding"], offset)
        cols = st.columns(3 if st.session_state["show_diff"] else 2)
        cols[0].image(rgb, caption="濾波前（原圖）", width="stretch")
        cols[1].image(filtered, caption="濾波後", width="stretch")
        if st.session_state["show_diff"]:
            diff = np.clip(np.abs(rgb.astype(np.int16) - filtered.astype(np.int16)) * 4, 0, 255)
            cols[2].image(diff.astype(np.uint8), caption="差異圖 |原圖 − 濾波後| ×4",
                          width="stretch")

        report = psnr_report(rgb, filtered)
        st.subheader("PSNR 量化評估")
        c1, c2, c3 = st.columns(3)
        c1.metric("PSNR（亮度 Y）", _fmt_db(report.psnr["Y"]))
        c2.metric("PSNR（R/G/B 通道平均）", _fmt_db(report.psnr_mean))
        c3.metric("MSE（亮度 Y）", f"{report.mse['Y']:.2f}")
        if math.isinf(report.psnr["Y"]):
            st.caption("濾波前後亮度完全相同（MSE = 0），PSNR 定義為 ∞。")
        else:
            st.caption("PSNR 越高代表濾波後越接近原圖；模糊、銳化越強 PSNR 越低（約 30 dB 以下可明顯看出差異）。")

        with st.expander("各通道 PSNR / MSE 與公式"):
            names = ["R", "G", "B", "Y"]
            st.table({"通道": names,
                      "MSE": [f"{report.mse[n]:.3f}" for n in names],
                      "PSNR (dB)": [_fmt_db(report.psnr[n]) for n in names]})
            st.latex(r"\mathrm{MSE}=\frac{1}{MN}\sum_{i=1}^{M}\sum_{j=1}^{N}"
                     r"\bigl[I(i,j)-K(i,j)\bigr]^{2}")
            st.latex(r"\mathrm{PSNR}=10\log_{10}\!\left(\frac{\mathrm{MAX}^{2}}{\mathrm{MSE}}\right)"
                     r"=20\log_{10}\mathrm{MAX}-10\log_{10}\mathrm{MSE},\qquad \mathrm{MAX}=255")
