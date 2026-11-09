# AI 協作與 Prompt 歷程（AI Audit Trail）

本資料夾記錄「Image Lab」開發過程中與 AI 協作的完整歷程。

**完整對話連結（公開快照）**：https://claude.ai/share/c7f80221-4bbc-4509-ade9-f5ee6943d3d8　｜　離線備份：[raw_exports/claude_conversation_2026-11-08_to_11-09.pdf](raw_exports/claude_conversation_2026-11-08_to_11-09.pdf)

## 檔案索引

| 檔案 | 內容 | 對應 Prompt |
|---|---|---|
| [00_models_used.md](00_models_used.md) | 使用的 AI 模型、版本、時間範圍、工具 | — |
| [01_project_setup.md](01_project_setup.md) | 需求分析、專案目錄規劃、環境建置、OpenCV 版本問題 | P1–P4 |
| [02_io_and_color.md](02_io_and_color.md) | 影像載入、色彩空間、同步直方圖、中文字型問題 | P5–P6 |
| [03_filtering_psnr.md](03_filtering_psnr.md) | 卷積濾波、輸入防呆、PSNR | P6–P8 |
| [04_face_detection.md](04_face_detection.md) | Haar-Cascade 人臉偵測與信心度 | P8 |
| [05_git_deployment.md](05_git_deployment.md) | README、GitHub 推送、Streamlit Cloud 部署 | P9–P14 |
| [06_report_and_colab.md](06_report_and_colab.md) | 技術報告 PDF（進行中；Colab 已取消） | P15–P28 |
| [raw_exports/](raw_exports/) | 完整對話原文匯出（不可竄改的底稿） | 全部 |

## 每個階段的格式

```
原始 Prompt（逐字）→ AI 產出摘要 → 問題 / 錯誤 → Refinement（修正指令）→ 最終結果 → 提示工程觀察
```

## 時間軸（Asia/Taipei，UTC+8）

| 編號 | 時間 | 使用者 Prompt 重點 |
|---|---|---|
| P1 | 2026-11-08 02:45 | 角色設定 + 完整需求，要求先不動作、只給目錄結構 |
| P2 | 2026-11-08 03:43 | 附上評分表與繳交規範，要求對應調整規劃 |
| P3 | 2026-11-08 03:55 | 回答 5 個確認問題；詢問第一步 |
| P4 | 2026-11-08 04:01 | 授權檢視專案資料夾，要求確認進度 |
| P5 | 2026-11-08 04:04 | 「請檢查，並繼續下一步」 |
| P6 | 2026-11-08 04:19 | 附截圖，指出中文字體問題，要求評估進度與方向 |
| P7 | 2026-11-08 04:33 | 「請遵守規則，並且繼續實作」 |
| P8 | 2026-11-08 04:48 | 附截圖，「看進度，有問題就修正，無問題就繼續」 |
| P9 | 2026-11-08 21:46 | 「好 來吧」（README 與部署） |
| P10 | 2026-11-09 15:07 | 貼上 `git remote add` 錯誤 |
| P11 | 2026-11-09 15:08 | 貼上 `git push` 的 Repository not found |
| P12 | 2026-11-09 15:11 | 回報清除憑證後推送結果 |
| P13 | 2026-11-09 15:58 | 提供 Streamlit Cloud 部署網址 |
| P14 | 2026-11-09 16:00 | 附部署畫面截圖，要求開始整理 Prompt Log |
| P15 | 2026-11-09 17:19 | 補入截圖與結果，要求檢查缺漏並開始報告 |
| P16 | 2026-11-09 20:47 | 補入作者與 pytest 結果、取消 Colab、詢問防呆畫面做法 |
| P17 | 2026-11-09 21:59 | 完成防呆截圖、要求整理其他截圖檔名 |
| P18 | 2026-11-09 22:13 | 回答補件問題（濾波設定、無其他 AI 工具、人臉偵測截圖） |
| P19 | 2026-11-09 22:31 | 完成邊界處理對照與人臉偵測截圖 |
| P20–P22 | 2026-11-09 22:41–22:53 | 確認信心度與預設邊界處理、重拍 minNeighbors 低／高的截圖 |
| P23–P24 | 2026-11-09 23:01–23:05 | 回報 PDF 預覽問題、要求加入目錄頁 |
| P24b | 2026-11-09 23:10 | 補完 Prompt Log、詢問分享連結的作法 |
| P25 | 2026-11-09 23:19 | 建立分享連結與備份 PDF |
| P26 | 2026-11-09 23:26 | 同一連結、詢問是否完成（備份 PDF 仍不完整） |
| P27 | 2026-11-09 23:30 | 準備繳交（備份 PDF 驗證通過） |
| P27b | 2026-11-09 23:34 | Ctrl+Z 誤復原與最後檢查 |
| P28 | 2026-11-09 23:40 | 依繳交規範重整報告（章節、檔名、完整 Prompt 歷程、超連結） |

## AI 失誤與修正總表

| # | AI 的失誤或限制 | 如何發現 | 修正 |
|---|---|---|---|
| 1 | 先建議 MediaPipe，後改 Haar；且假設使用者會裝到 OpenCV 4.x，未先確認版本 | P4：AI 檢視專案資料夾，發現裝到 OpenCV 5.0.0.93，沒有 `CascadeClassifier` 與 Haar XML | 要求降版 `opencv-python-headless<5`，重新匯出 `requirements.txt`（P6 確認 4.14.0.94 完成） |
| 2 | 規劃的 `src/imagelab/` 版面，實作時改成根目錄 `imagelab/` | AI 自行判斷：雲端部署與 pytest 不需額外設定匯入路徑 | 在 P5 的回覆中明講差異與理由 |
| 3 | matplotlib 預設字型沒有中文，直方圖標題顯示方框 | P6：使用者截圖 | 自動偵測 CJK 字型、偵測不到時改英文標題、新增 `packages.txt`（`fonts-noto-cjk`） |
| 4 | AI 的執行環境（Linux VM）無法執行使用者的 Windows `.venv`、Streamlit，也沒有 pytest 與可用的 Haar | 驗證 P5、P7、P8 的程式時發現 | 用「最小 pytest 替身執行器」驗證演算法；明確告知哪些部分未驗證，要求使用者本機實跑 |
| 5 | OpenCV 5.0 的 Linux 環境沒有 Haar，人臉偵測無法在 AI 端實跑 | P8 | 改查使用者 venv（4.14）的型別檔確認 API；測試對 Haar 相關案例使用 `skip` |
| 6 | 回覆中的占位符 `<你的帳號>` 被使用者原樣貼進 `git remote`，導致 origin 指向無效網址 | P10 | 診斷後以 `git remote set-url` 修正（P11） |
| 7 | AI 無法連線 GitHub（網路被擋）、網頁查詢被限流與 robots 拒絕 | P11、P13 | 改提供「用瀏覽器分辨三種情況」的判斷表，由使用者確認；不假裝已驗證 |

> **說明**：本紀錄依對話內容整理；完整原文請見 `raw_exports/`。測試結果中標明「替身執行器」者，並非真正的 `pytest`，真正的 pytest 由使用者在本機執行。
