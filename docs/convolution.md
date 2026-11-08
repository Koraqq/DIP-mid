# 2D 卷積推導與實作說明

## 1. 定義

核 $K$ 為 $k\times k$（$k$ 為奇數），中心偏移 $c=\lfloor k/2\rfloor$。**卷積**：

$$\mathrm{out}[i,j]=\sum_{m=0}^{k-1}\sum_{n=0}^{k-1}K[m,n]\;x[\,i-m+c,\;j-n+c\,]$$

## 2. 為什麼實作時要翻轉核

令補邊後的影像為 $P$（四邊各補 $c$ 格，$P[a,b]=x[a-c,b-c]$）。把 $x[i-m+c,\,j-n+c]$ 改寫成 $P$ 的座標：

$$x[i-m+c,\,j-n+c]=P[\,i-m+2c,\;j-n+2c\,]=P[\,i+(k-1-m),\;j+(k-1-n)\,]$$

令 $u=k-1-m$、$v=k-1-n$（即 $K'[u,v]=K[k-1-u,\,k-1-v]$，把核旋轉 180°）：

$$\mathrm{out}[i,j]=\sum_{u}\sum_{v}K'[u,v]\;P[i+u,\;j+v]$$

這就是用**旋轉後的核**在 $P$ 上做滑動視窗內積（相關）。程式只迴圈 $k^2$ 次，每次是整張影像的向量運算：`out += K'[u,v] * P[u:u+H, v:v+W]`。

**幾何直觀**：卷積 = 核旋轉 180° 後在影像上滑動，每個位置算「視窗與核的內積」。OpenCV 的 `filter2D` 做的是「不翻轉」的相關，所以測試中拿它對照時，要先把核翻轉。對稱核（高斯、均值、拉普拉斯）兩者結果相同；不對稱核（Sobel、浮雕）翻轉與否會改變方向。

**驗證用的小例子**：核只有中心右側為 1，卷積結果是影像**向右**平移一格（`tests/test_convolution.py::test_true_convolution_flips_kernel`）。

## 3. 邊界處理

| 模式 | 補邊值 | NumPy 對應 | OpenCV 對應 |
|---|---|---|---|
| zero | 0 | `constant` | `BORDER_CONSTANT` |
| reflect | 鏡射（不重複邊緣像素） | `reflect` | `BORDER_REFLECT_101` |
| replicate | 複製邊緣像素 | `edge` | `BORDER_REPLICATE` |

## 4. 正規化

除以核元素總和 $s=\sum K$：$K\leftarrow K/s$。對常數影像（亮度為 $a$）輸出為 $a\cdot\sum K/s=a$，所以**平均亮度保持不變**（直流增益為 1）。

- 模糊類核（均值、高斯）：總和為正，應正規化。
- 總和為 1 的銳化核：不需要。
- 總和為 0 的核（Sobel、Laplacian）：$s=0$ 無法相除，程式**略過正規化並提示**，這類核會濾除直流分量，輸出接近 0，所以提供「加 128 偏移」讓正負響應都能顯示。

## 5. 輸出轉換

卷積結果為 float，加上偏移後四捨五入並截斷到 $[0,255]$ 轉回 `uint8`。
