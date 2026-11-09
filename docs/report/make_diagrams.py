"""產生報告用的系統架構圖與資料流圖（matplotlib）。

每段文字都會檢查是否超出所屬方框；超出會直接報錯，避免圖面文字被截斷。
執行：python make_diagrams.py
"""
from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch

OUT = pathlib.Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
_installed = {f.name for f in fm.fontManager.ttflist}
FONT = next((n for n in ("Noto Sans CJK TC", "Microsoft JhengHei", "Noto Sans CJK JP", "PingFang TC")
             if n in _installed), None)
if FONT is None:
    raise SystemExit("找不到中文字型，無法產生圖面。")
plt.rcParams["font.family"] = FONT
plt.rcParams["axes.unicode_minus"] = False


class Canvas:
    def __init__(self, w: float, h: float):
        self.fig, self.ax = plt.subplots(figsize=(w, h), dpi=200)
        self.fig.subplots_adjust(0, 0, 1, 1)
        self.ax.set_xlim(0, w)
        self.ax.set_ylim(0, h)
        self.ax.axis("off")
        self.pairs: list = []

    def container(self, x, y, w, h, title, fc, ec):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                                         fc=fc, ec=ec, lw=1.2, zorder=0))
        self.ax.text(x + 0.12, y + h - 0.07, title, ha="left", va="top", fontsize=8.5,
                     fontweight="bold", color="#222222", zorder=1)

    def box(self, x, y, w, h, text, fc="#ffffff", ec="#444444", fs=8.0, weight="normal"):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                           fc=fc, ec=ec, lw=1.0, zorder=2)
        self.ax.add_patch(p)
        t = self.ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                         fontweight=weight, zorder=3, linespacing=1.35)
        self.pairs.append((t, p, text))

    def arrow(self, x1, y1, x2, y2, label=None, lx=0.08, ly=0.0):
        self.ax.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=1,
                         arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#555555"))
        if label:
            self.ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, fontsize=7.5,
                         color="#555555", va="center", ha="left")

    def label(self, x, y, text, fs=8, color="#666666", ha="center"):
        self.ax.text(x, y, text, ha=ha, va="center", fontsize=fs, color=color, fontweight="bold")

    def save(self, name: str):
        self.fig.canvas.draw()
        r = self.fig.canvas.get_renderer()
        bad = []
        for t, p, s in self.pairs:
            tb, pb = t.get_window_extent(r), p.get_window_extent(r)
            if tb.x0 < pb.x0 + 4 or tb.x1 > pb.x1 - 4 or tb.y0 < pb.y0 + 3 or tb.y1 > pb.y1 - 3:
                bad.append(s.replace("\n", " / "))
        if bad:
            raise SystemExit(f"[{name}] 文字超出方框：" + "；".join(bad))
        self.fig.savefig(OUT / name, dpi=200)
        plt.close(self.fig)
        print("saved", name)


def architecture():
    c = Canvas(7.4, 5.3)
    c.container(0.1, 3.85, 7.2, 1.35, "Streamlit 介面層（app.py ＋ imagelab/ui/）", "#eaf2fb", "#4a86c5")
    for i, txt in enumerate(["sidebar.py\n影像上傳", "tab_overview.py\n影像資訊", "tab_color.py\n色彩空間／直方圖",
                             "tab_filter.py\n卷積濾波／PSNR", "tab_face.py\n人臉偵測"]):
        c.box(0.3 + i * 1.4, 3.95, 1.3, 0.75, txt)
    c.container(0.1, 1.65, 7.2, 1.9, "演算法層（純 NumPy / OpenCV，不依賴 Streamlit，可單獨測試）", "#eef7ee", "#5a9e5a")
    algo = ["io/\nloader.py\nmetadata.py", "color/\nchannels.py\nyuv.py", "analysis/\nhistogram.py",
            "filtering/\nkernels.py\nconvolution.py\nmetrics.py", "validation/\nmatrix_parser.py\nguards.py",
            "detection/\nhaar_detector.py\ndraw.py"]
    for i, txt in enumerate(algo):
        c.box(0.25 + i * 1.17, 1.75, 1.1, 1.15, txt, fs=7.2)
    c.container(0.1, 0.15, 7.2, 1.25, "外部函式庫", "#f8f3e8", "#b08d3c")
    for i, txt in enumerate(["NumPy 2.5\n向量化運算", "Pillow 13\n影像解碼", "OpenCV 4.14（headless）\nHaar-Cascade、繪圖",
                             "Matplotlib 3.11\n直方圖繪製"]):
        c.box(0.2 + i * 1.78, 0.25, 1.68, 0.62, txt, fs=7.2)
    c.arrow(3.7, 3.85, 3.7, 3.55, "呼叫")
    c.arrow(3.7, 1.65, 3.7, 1.4, "使用")
    c.save("diagram_architecture.png")


def dataflow():
    c = Canvas(7.4, 4.5)
    for x, txt in [(0.78, "輸入"), (2.47, "解碼"), (4.55, "處理（演算法層）"), (6.58, "輸出（介面層）")]:
        c.label(x, 4.3, txt)
    c.box(0.15, 1.95, 1.25, 0.9, "上傳檔案\nPNG／JPG／BMP\n（bytes）", fc="#fdf2e3")
    c.box(1.75, 1.95, 1.45, 0.9, "load_image()\n→ RGB uint8\nH×W×3（快取）", fc="#fdf2e3")
    c.arrow(1.4, 2.4, 1.75, 2.4)
    rows = [
        (3.55, "get_metadata()\n解析度／通道／檔案大小", "影像資訊表"),
        (2.55, "split_rgb／split_yuv\ncompute_histogram()", "分量圖＋直方圖\n（同步更新）"),
        (1.55, "parse_kernel() 防呆\nnormalize_kernel()\napply_filter() 卷積", "濾波前後對照\nPSNR（Y／RGB）"),
        (0.55, "detect_faces()\nHaar-Cascade", "邊界框＋人數\n＋信心度"),
    ]
    for y, proc, out in rows:
        c.box(3.55, y - 0.4, 2.0, 0.8, proc, fc="#eef7ee")
        c.box(5.85, y - 0.4, 1.45, 0.8, out, fc="#eaf2fb")
        c.arrow(3.2, 2.4, 3.55, y)
        c.arrow(5.55, y, 5.85, y)
    c.save("diagram_dataflow.png")


if __name__ == "__main__":
    architecture()
    dataflow()
