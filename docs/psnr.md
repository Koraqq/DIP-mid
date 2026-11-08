# PSNR（峰值信噪比）公式推導與使用說明

## 1. 代數推導

設原圖為 $I$、比較圖為 $K$，尺寸 $M\times N$（單通道、8-bit）。

**步驟 1：均方誤差（MSE）**——每個像素差的平方，取平均：

$$\mathrm{MSE}=\frac{1}{MN}\sum_{i=1}^{M}\sum_{j=1}^{N}\bigl[I(i,j)-K(i,j)\bigr]^{2}$$

**步驟 2：峰值訊號功率**——8-bit 影像最大像素值 $\mathrm{MAX}=2^{8}-1=255$，峰值訊號功率為 $\mathrm{MAX}^2$。

**步驟 3：訊號與雜訊的功率比**——

$$\frac{\mathrm{MAX}^{2}}{\mathrm{MSE}}$$

**步驟 4：換成分貝**——功率比取 $10\log_{10}$：

$$\mathrm{PSNR}=10\log_{10}\!\left(\frac{\mathrm{MAX}^{2}}{\mathrm{MSE}}\right)=20\log_{10}\mathrm{MAX}-10\log_{10}\mathrm{MSE}$$

代入 $\mathrm{MAX}=255$：$20\log_{10}255\approx 48.13$，所以

$$\mathrm{PSNR}\approx 48.13-10\log_{10}\mathrm{MSE}\ \text{(dB)}$$

### 數值驗算

| MSE | PSNR |
|---|---|
| 1 | 48.13 dB |
| 100 | $10\log_{10}(65025/100)\approx 28.13$ dB |
| 65025（黑對白，最差） | 0 dB |
| 0（兩圖完全相同） | $\infty$ |

MSE 每變成 2 倍，PSNR 減少 $10\log_{10}2\approx 3.01$ dB；MSE 變 10 倍，減少 10 dB。

## 2. 幾何解釋

把一張影像看成 $\mathbb{R}^{MN}$ 空間中的一個向量 $\mathbf{x}$。MSE 就是兩個向量歐氏距離平方除以維度：

$$\mathrm{MSE}=\frac{\lVert \mathbf{x}_I-\mathbf{x}_K\rVert_2^{2}}{MN}$$

因此 PSNR 是「兩張圖在像素空間中的距離」經過 $-10\log_{10}(\cdot)$ 變換的結果：距離越近 PSNR 越高。它對所有像素一視同仁，只看數值差，**不考慮人眼感知與結構**，這是它的限制（例如整張圖平移 1 像素，視覺幾乎相同，PSNR 卻可能很低）。

## 3. 本專案的計算方式

- 比較對象：原圖 vs. 濾波後影像（皆為 8-bit，$\mathrm{MAX}=255$）。
- **逐通道**：分別對 R、G、B 計算 MSE 與 PSNR。
- **R/G/B 通道平均**：三個通道 PSNR（dB）的算術平均。
- **亮度 Y**：先將兩張 RGB 圖用 BT.601 轉成 Y（四捨五入為 uint8），再計算 PSNR。Y 較貼近人眼對明暗的感知。
- 先轉 `float64` 再相減，避免 `uint8` 相減溢位（例如 $0-255$ 會變成 $1$）。
- $\mathrm{MSE}=0$ 時定義 $\mathrm{PSNR}=\infty$，介面顯示「∞」。

## 4. 結果判讀（經驗值）

| PSNR | 一般解讀 |
|---|---|
| > 40 dB | 幾乎看不出差異 |
| 30–40 dB | 差異小，通常可接受 |
| 20–30 dB | 明顯差異（例如強烈模糊或銳化） |
| < 20 dB | 差異很大 |

此為經驗法則，實際視覺感受與影像內容有關。
