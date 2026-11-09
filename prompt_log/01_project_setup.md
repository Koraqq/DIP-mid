# 01 專案規劃與環境建置（P1–P4）

---

## P1　2026-11-08 02:45　需求與目錄結構

### 原始 Prompt（逐字）

```
請先遵守以下的規則

1. 你是一位資深電腦視覺工程師兼軟體架構師，我需要你完成以下的要求，先不做任何動作，請先了解我們現在該怎麼做，並且要做什麼。
2. 環境：Python 3.12、Streamlit，開發一個互動式影像處理與人臉分析工具開發。
3. 影像載入與基礎解析：支援常見點陣圖格式（至少包含 PNG、JPG/JPEG、BMP）之檔案讀入與即時顯示，正確顯示影像基本中繼資訊（影像解析度、色彩維度、檔案大小等）。
4. 多色彩空間轉換與同步直方圖分析：提供介面切換檢視：原始影像（Original）、RGB 各分量獨立檢視（R/G/B 分離頻道通道圖）、YUV 色彩空間轉換（Y/U/V 亮度與色度分量圖）。

* 同步直方圖繪製：在切換各顯示模式時，需同步動態渲染對應通道的灰階/強度分布直方圖（Histogram），直方圖橫軸需為像素強度（0–255），縱軸為像素數量。

5. 自訂卷積核（Kernel Matrix）空間濾波與量化評估：

* 自訂濾波矩陣：提供使用者動態輸入一組任意數值之二維陣列（例如 3×33\times33×3 或 5×55\times55×5 卷積核，支援邊緣銳化、高斯平滑、浮雕等權重自訂），並可選擇正規化（Normalization）參數。
* 濾波計算與顯示：對輸入影像進行卷積濾波運算，並排或疊加比對濾波前後之視覺成果。
* 量化品質指標（PSNR）計算：以原圖與濾波後影像為基準，即時計算並數值化顯示峰值信噪比（Peak Signal-to-Noise Ratio, PSNR）（以 dB 為單位），並於說明文件中推導/註明計算公式。

6. 人臉偵測（Face Detection）模組：

* 整合經典特徵辨識演算法（如 Haar-Cascade、HOG）或輕量級深層學習檢測器（如 MediaPipe Face Detection、MTCNN、YOLO-Face）。
* 能在影像中標記出所有偵測到的人臉邊界框（Bounding Box），並回傳/標註偵測到的總人臉數量與推論信心度（Confidence Score）。

7. 並且本次作業需要附上版本控制儲存庫，現在請先提供專案目錄的結構就好。
```

### AI 產出摘要

- 依指示**不寫程式、不建立檔案**，只提供目錄結構。
- 設計原則：UI 層（Streamlit）與演算法層（NumPy/OpenCV）分離，演算法模組不 import streamlit，方便單元測試。
- 結構涵蓋 `io/`、`color/`、`analysis/`、`filtering/`、`detection/`、`ui/`、`tests/`、`docs/`。
- 提出 5 個待確認問題：人臉偵測器（MediaPipe 或 Haar）、卷積是否手刻、PSNR 通道處理方式、文件格式、Git 託管平台。

### 提示工程觀察

- 使用者先設定**角色**（資深電腦視覺工程師兼軟體架構師），並用「先不做任何動作」限制輸出範圍，避免一次產出大量未確認的程式。
- 需求以編號列出並附驗收條件（例如直方圖橫軸 0–255），讓後續測試有明確依據。

---

## P2　2026-11-08 03:43　評分表與繳交規範

### 原始 Prompt（逐字）

附圖：評分標準表（功能完整性與演算法正確性 35%、可執行成果與部署品質 20%、AI 協作歷程 Prompt Log 20%、技術報告說明書與排版 PDF 15%、介面設計與使用者體驗 UX 10%）。文字部分如下：

```
以下是必須遵守的繳交規範

1. 專案概述與環境建置
2. 可執行連結（Live Demo / Source Code）

* 提供線上即時執行展示連結（如 Hugging Face Spaces、Streamlit Cloud、Google Colab 等，需確認檢閱權限為 Public 開放）。
* 附上版本控制儲存庫（GitHub / GitLab）完整原始碼連結。

註：我應該會另外用 colab 來展示執行成果，這個部份我們可以最後做完再處理， 然後會將我們程式原始碼都推到github 上面。

3. 程式功能與操作說明書

* 各模組架構圖與資料流說明。
* 功能 1 至 4 之介面操作截圖、功能實測說明與測試案例分析（含邊界條件測試，如極端矩陣輸入、多人臉場景等）。
* PSNR 公式定義與濾波效果的客觀評估分析。

4. AI 協作與完整 Prompt 歷程（AI Audit Trail）

* 完整記錄開發過程中所使用的 AI 模型版本（如 GPT-4o、Claude 3.5 Sonnet 等）。
* 依時間序或模組呈現「原始 Prompt 提問 →\rightarrow→ AI 產出結果 →\rightarrow→ 除錯/調整/重構指令（Refinement）」，展現提示工程（Prompt Engineering）之邏輯推演與除錯過程。

5. 附圖為本次實作的評分表。
```

### AI 產出摘要

- 指出評分表中 Prompt Log（20%）、報告 PDF（15%）、部署（20%）合計 55%，專案不能只有程式碼，因此把 `prompt_log/`、`docs/report/`、`validation/`、`README`、部署檔案加入目錄結構。
- 製作「評分項目 ↔ 對應交付物 ↔ 關鍵風險」對照表。
- 列出 UX 防呆案例清單：非方陣、偶數尺寸、非數值、正規化除以零、PSNR 的 MSE = 0、影像過大與格式不支援、無人臉。
- 提醒 Prompt Log 要「從現在開始」記錄，並說明格式。
- 建議進行順序，並再問 5 個確認問題。

### 提示工程觀察

- 使用者把**評分標準直接貼給模型**，讓規劃從「做出功能」轉成「對應配分的交付物」，這是這輪最大的方向修正。
- 使用者同時說明「Colab 最後再做」，用明確的優先順序控制範圍。

---

## P3　2026-11-08 03:55　回答確認問題與環境第一步

### 原始 Prompt（逐字）

```
1. 先做一種就好，此專案要求即可。
2. 做你覺得最好的那個方法即可。
3. 兩者都顯示。
4. 報告請最後做完後再總整理並且實作。
5. 今天deadline XD。

請問我第一步是要uv python install嗎？
```

### AI 產出摘要

- 回答：不一定需要 `uv python install`；真正第一步是安裝 uv 並 `uv init --python 3.12`，缺版本時 uv 會自動下載。給出完整指令（建立專案、`uv add` 依賴、匯出 `requirements.txt`）。
- 依使用者回答做決定：
  - 人臉偵測只做一種 → **改為 OpenCV Haar-Cascade**（先前建議 MediaPipe，理由是 MediaPipe 在 Python 3.12 與雲端環境的相容性風險較高，且今天是截止日，優先低風險）。
  - 卷積 → 純 NumPy 向量化手刻，並用 OpenCV 對照驗證。
  - PSNR → 逐通道平均與亮度 Y 兩者都顯示。
- 因為今天截止，給出時間分配建議，並提醒先保存 Prompt Log。

### 問題

- 這裡 AI 做了一個**沒有驗證的假設**：認為 OpenCV 內建 Haar 模型檔，所以「不需額外套件」。此假設以 OpenCV 4.x 為前提，沒有先確認使用者會安裝到哪個版本。這在 P4 被證實是錯的（見下）。

---

## P4　2026-11-08 04:01　授權檢視專案資料夾

### 原始 Prompt（逐字）

```
好的
C:\Users\eason\Desktop\DIP-mid 這邊的目錄，是讓你確保我有完成或者任何有錯誤的地方，剛剛我已經完成了以上的要求，請跟我說下一步。
```

### AI 產出摘要

- 先請求資料夾存取權限，再讀取 `pyproject.toml`、`.python-version`、`requirements.txt`、Git 狀態與已安裝的 `cv2` 套件內容。
- 確認 Python 3.12.13、依賴都已安裝、Git 已初始化但無 commit、缺少 `.gitignore`。
- **發現問題**：使用者安裝到的是 `opencv-python-headless 5.0.0.93`。檢查型別檔與資料夾後發現：這個版本沒有 `CascadeClassifier`、沒有 `HOGDescriptor`，`cv2/data/` 內也沒有任何 `haarcascade_*.xml`。AI 在回覆中承認是自己先前的疏漏。

### Refinement（修正指令）

AI 提供的修正（分支改名與第一個 commit 於 P4–P5 之間完成；OpenCV 降版於 P5–P6 之間完成）：

```bash
uv add "opencv-python-headless<5"
uv run python -c "import cv2; ... Haar OK ..."
uv export --no-dev --no-hashes -o requirements.txt
git branch -M main
```

並提供 `.gitignore` 內容與第一個 commit 的指令。

### 最終結果

- P5 檢查時：分支已是 `main`、已有第一個 commit，但 **OpenCV 仍是 5.0.0.93、`.gitignore` 不存在**（降版尚未完成）。AI 先自行補上 `.gitignore`，並繼續實作不依賴 Haar 的模組，再次提醒降版。
- P6 檢查時確認：OpenCV 已是 **4.14.0.94**，`cv2/data/` 有完整的 Haar XML，`pyproject.toml` 已寫入 `opencv-python-headless<5`，`requirements.txt` 已重新匯出。

### 提示工程觀察

- 使用者**讓 AI 直接檢查專案資料夾**，而不是自己描述狀況，這讓 AI 能在寫任何程式前先發現環境錯誤，避免做出無法執行的人臉偵測模組。
- 這是整個專案中最重要的一次「先驗證環境，再寫程式」。
