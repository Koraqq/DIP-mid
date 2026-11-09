# Image Lab：互動式影像處理與人臉分析工具

數位影像處理（DIP）期中作業。使用 **Python 3.12 + Streamlit** 開發，涵蓋影像載入、色彩空間與直方圖、自訂卷積濾波與 PSNR 評估、人臉偵測四大功能。

## 連結

| 項目 | 連結 |
|---|---|
| 線上展示（Streamlit Cloud） | https://dip-mid-tb8vrujcpzjqkwkc5onscz.streamlit.app/ |
| Colab 展示 | `<COLAB_URL>` |
| 原始碼（GitHub） | https://github.com/koraqq/DIP-mid |

## 功能

| # | 功能 | 內容 |
|---|---|---|
| 1 | 影像載入與解析 | 支援 PNG、JPG/JPEG、BMP；顯示解析度、色彩維度、檔案大小、格式 |
| 2 | 色彩空間與同步直方圖 | Original / RGB 分量 / YUV（BT.601）分量；切換模式時直方圖（橫軸 0–255、縱軸像素數）同步更新 |
| 3 | 自訂卷積濾波與 PSNR | 自訂奇數方陣核（3×3、5×5…）、9 種預設範本、正規化、三種邊界處理；濾波前後並排與差異圖；PSNR（逐通道、通道平均、亮度 Y） |
| 4 | 人臉偵測 | OpenCV Haar-Cascade；繪製邊界框，顯示人臉總數與每張臉的信心度，可調 scaleFactor / minNeighbors / 最小尺寸 |

## 快速開始

需要 Python 3.12。**OpenCV 必須是 4.x**（5.x 已移除 Haar-Cascade），專案已鎖定版本。

### 方法 A：uv（建議）

```bash
git clone https://github.com/koraqq/DIP-mid
cd DIP-mid
uv sync
uv run streamlit run app.py
```

### 方法 B：pip

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

啟動後瀏覽器會開啟 http://localhost:8501，從左側上傳影像即可。

## 測試

```bash
uv run pytest -q        # 單元測試（含邊界條件）
uv run ruff check .     # 程式碼風格檢查
```

測試重點：卷積與 `cv2.filter2D` 逐元素對照（三種邊界模式、非對稱核）、PSNR 已知值與 `uint8` 溢位、YUV 往返誤差、矩陣輸入各種錯誤、人臉偵測的空白圖／極小圖／參數錯誤。

## 專案結構

```
DIP-mid/
├── app.py                    # Streamlit 進入點（四個分頁）
├── imagelab/
│   ├── io/                   # 影像載入（loader）、中繼資訊（metadata）
│   ├── color/                # RGB 分離（channels）、YUV 轉換（yuv）
│   ├── analysis/             # 直方圖計算與繪圖（含中文字型偵測）
│   ├── filtering/            # 預設核與正規化（kernels）、卷積（convolution）、PSNR（metrics）
│   ├── validation/           # 矩陣解析與防呆（matrix_parser、guards）
│   ├── detection/            # Haar 偵測（haar_detector）、繪製（draw）
│   └── ui/                   # Streamlit 介面（各分頁、側邊欄、快取）
├── tests/                    # pytest 測試
├── docs/                     # psnr.md、convolution.md、報告與截圖
├── prompt_log/               # AI 協作紀錄
├── assets/samples/           # 範例影像
├── requirements.txt          # 部署用（由 uv export 產生）
├── packages.txt              # 部署用系統套件（中文字型 fonts-noto-cjk）
└── pyproject.toml / uv.lock  # uv 專案設定與鎖定檔
```

演算法層（`imagelab/` 除 `ui/` 外）完全不依賴 Streamlit，可獨立測試。

## 技術重點

- **YUV**：BT.601 全範圍。`Y = 0.299R + 0.587G + 0.114B`，`U = −0.168736R − 0.331264G + 0.5B + 128`，`V = 0.5R − 0.418688G − 0.081312B + 128`。
- **卷積**：純 NumPy 向量化，核先旋轉 180° 再滑動內積（真正的卷積），只迴圈 k² 次；推導見 [docs/convolution.md](docs/convolution.md)。
- **PSNR**：`PSNR = 10·log10(MAX² / MSE)`，`MAX = 255`；兩圖完全相同時 MSE = 0，顯示 ∞。推導見 [docs/psnr.md](docs/psnr.md)。
- **信心度**：Haar-Cascade 最後一層權重 `w`（`detectMultiScale3`）經 `1 − e^(−w/2)` 正規化到 0–1，並同時顯示原始權重。這是啟發式正規化，不是機率。

## 輸入防呆與邊界條件

| 情境 | 行為 |
|---|---|
| 核非方陣、各列個數不同、偶數尺寸、超過 15×15 | 顯示明確錯誤訊息，不執行運算 |
| 核內有非數字、NaN、無限大 | 指出第幾列第幾格 |
| 核比影像還大、核全為 0 | 錯誤／警告 |
| 正規化但核總和為 0（Sobel、Laplacian） | 自動略過並提示，避免除以零 |
| 原圖與濾波後完全相同（MSE = 0） | PSNR 顯示 ∞ |
| 損毀檔、不支援格式、空檔案、超過 2500 萬像素 | 友善錯誤訊息 |
| 含透明通道的 PNG | 合成在白色背景上 |
| 影像比偵測視窗小、未偵測到人臉 | 顯示 0 張與調整參數的建議，不會當機 |

## 部署（Streamlit Community Cloud）

1. 將專案推上 GitHub（公開儲存庫）。
2. 到 https://share.streamlit.io → **Create app** → 選擇儲存庫、分支 `main`、Main file path 填 `app.py`。
3. **Advanced settings** 將 Python 版本選為 **3.12**。
4. Deploy。平台會自動讀取 `requirements.txt` 與 `packages.txt`（安裝中文字型）。
5. 部署完成後確認應用程式的分享設定為 **Public**，並把網址填回本文件開頭。

## 已知限制

- Haar-Cascade 以正臉為主；側臉、嚴重遮擋或失焦的臉可能偵測不到。
- PSNR 只比較像素差，不反映人眼感知與結構相似度。
- 影像上限 2500 萬像素。

## AI 協作聲明

本專案開發過程使用 Claude（Anthropic）協助規劃、實作與除錯。使用的模型版本與完整提問、產出、修正歷程記錄於 [prompt_log/](prompt_log/)。
