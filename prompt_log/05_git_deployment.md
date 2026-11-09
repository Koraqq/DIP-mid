# 05 README、GitHub 與 Streamlit Cloud 部署（P9–P14）

---

## P9　2026-11-08 21:46　README 與部署

### 原始 Prompt（逐字）

```
好 來吧
```

### AI 產出摘要

- 檢查資料夾：三個 commit 皆已完成、工作區乾淨、尚未設定遠端，`assets/samples/` 與 `docs/images/` 仍無內容。
- 撰寫 `README.md`：連結表、功能表、uv 與 pip 兩種安裝方式、測試、專案結構、公式、輸入防呆表、Streamlit Cloud 部署步驟（含 Python 3.12 設定）、已知限制、AI 協作聲明。
- 修改 `pyproject.toml` 的預設描述；提醒 `git rm main.py`。
- 提供推上 GitHub 與部署的步驟。

---

## P10　2026-11-09 15:07　`git remote add` 失敗

### 原始 Prompt（逐字）

```
(dip-mid) PS C:\Users\eason\Desktop\DIP-mid> git remote add origin https://github.com/koraqq/DIP-mid.git    
error: remote origin already exists.
```

### AI 產出摘要與問題

- AI 檢查專案的 `.git` 設定，發現 `origin` 指向 `https://github.com/<你的帳號>/DIP-mid.git`。
- **原因（AI 自己的疏失）**：先前 AI 在回覆中的指令使用了 `<你的帳號>` 占位符，使用者原樣貼上執行，導致 origin 指向一個無效網址。
- Refinement：改用 `git remote set-url origin ...` 修改既有 origin，而不是再新增。

---

## P11　2026-11-09 15:08　`Repository not found`

### 原始 Prompt（逐字）

```
解決以下的問題

(dip-mid) PS C:\Users\eason\Desktop\DIP-mid> git remote set-url origin https://github.com/koraqq/DIP-mid.git
(dip-mid) PS C:\Users\eason\Desktop\DIP-mid> git remote -v
origin  https://github.com/koraqq/DIP-mid.git (fetch)
origin  https://github.com/koraqq/DIP-mid.git (push)
(dip-mid) PS C:\Users\eason\Desktop\DIP-mid> git push -u origin main
remote: Repository not found.
fatal: repository 'https://github.com/koraqq/DIP-mid.git/' not found
```

### AI 產出摘要與限制

- AI 想從外部確認儲存庫是否存在，但網頁查詢被限流，從 AI 的環境用 git 與 GitHub API 也無法連線（網路被擋）。**AI 沒有假裝已驗證**，如實告知。
- 改提供判斷表：請使用者用瀏覽器開 `https://github.com/koraqq/DIP-mid`，依看到的結果（404、私有、空儲存庫）分辨三種原因（儲存庫未建立或帳號名稱錯、私有且帳號驗證錯誤、登入問題），並附上建立儲存庫的步驟（Public、不勾選 README/.gitignore/license）與清除 Windows 憑證的指令。

---

## P12　2026-11-09 15:11　清除憑證後推送

### 原始 Prompt（逐字）

```
(dip-mid) PS C:\Users\eason\Desktop\DIP-mid> git remote set-url origin https://github.com/koraqq/DIP-mid.git    
(dip-mid) PS C:\Users\eason\Desktop\DIP-mid> cmdkey /delete:git:https://github.com

CMDKEY: Credential deleted successfully.
(dip-mid) PS C:\Users\eason\Desktop\DIP-mid> git push -u origin main
branch 'main' set up to track 'origin/main'.
Everything up-to-date

這邊應該好了
```

### AI 產出摘要

- 輸出 `Everything up-to-date` 不是第一次推送到全新儲存庫的典型結果，AI 先檢查本地記錄：`HEAD` 與 `origin/main` 都是 `92271a8`，沒有未推送的 commit。
- AI **如實說明不確定**遠端內容是這次推上去的，還是更早就在那裡，並要求使用者用瀏覽器確認：儲存庫為 **Public**、檔案完整、最新 commit 正確。
- 提供 Streamlit Cloud 的部署步驟，強調 **Advanced settings 要選 Python 3.12**。

---

## P13　2026-11-09 15:58　部署完成

### 原始 Prompt（逐字）

```
https://dip-mid-tb8vrujcpzjqkwkc5onscz.streamlit.app/
好了
```

### AI 產出摘要

- 將部署網址與 GitHub 連結填入 `README.md`（Colab 連結保留占位符）；順手修掉 GitHub 連結的反引號，使其可點擊。
- 嘗試開啟部署網址被網站的 robots 規則拒絕，AI 如實說明**無法自行驗收線上版**，提供驗收清單請使用者用無痕視窗檢查：是否不登入就能開、中文直方圖標題是否正常（雲端是否裝到 `fonts-noto-cjk`）、PSNR 是否與本機一致、第四分頁是否出錯。

---

## P14　2026-11-09 16:00　開始整理 Prompt Log

### 原始 Prompt（逐字）

附圖：線上展示畫面截圖（標題「Image Lab：影像處理與人臉分析」、側邊欄上傳區、「請從左側上傳一張 PNG / JPG / BMP 影像開始。」提示，頁面右上角有 Fork 與 GitHub 圖示）。文字如下：

```
OK了 那就開始 Prompt Log
```

### 結果

截圖顯示線上版已能正常載入首頁。

### 使用者驗證（待補）

〔請在此補上：線上版四個分頁的實測結果，尤其是中文字型與第四分頁人臉偵測。〕

### 提示工程觀察

- 這一段的 Prompt 多為**終端機輸出直接貼上**，AI 能從錯誤訊息直接定位原因（占位符、憑證、可見性），比文字描述更有效。
- 兩次出現的 AI 疏失（OpenCV 版本假設、占位符被當成真實網址）有共同點：**提供了未經確認就被直接使用的預設值**，修正方式都是「先檢查實際狀態再下指令」。
