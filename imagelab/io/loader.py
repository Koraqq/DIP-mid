"""影像載入：PNG / JPG / JPEG / BMP bytes -> RGB uint8 ndarray (H, W, 3)。"""
from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

SUPPORTED_EXTENSIONS = ("png", "jpg", "jpeg", "bmp")
SUPPORTED_FORMATS = {"PNG", "JPEG", "BMP"}
MAX_PIXELS = 25_000_000  # 防呆：避免超大圖耗盡記憶體


class ImageLoadError(ValueError):
    """影像無法載入時拋出，訊息可直接顯示給使用者。"""


def load_image(data: bytes) -> np.ndarray:
    """將檔案 bytes 解碼為 RGB uint8 陣列。

    - 依檔案內容（非副檔名）判斷格式，僅接受 PNG / JPEG / BMP
    - 套用 EXIF 方向，避免手機照片被轉 90 度
    - 含透明通道的圖會合成在白色背景上
    """
    if not data:
        raise ImageLoadError("檔案是空的。")
    try:
        img = Image.open(io.BytesIO(data))
        fmt = img.format
        if fmt not in SUPPORTED_FORMATS:
            raise ImageLoadError(f"不支援的影像格式：{fmt}。請使用 PNG、JPG 或 BMP。")
        w, h = img.size
        if w * h > MAX_PIXELS:
            raise ImageLoadError(
                f"影像過大（{w}×{h}，超過 {MAX_PIXELS:,} 像素），請先縮小後再上傳。"
            )
        img = ImageOps.exif_transpose(img)
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            rgba = img.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            img = Image.alpha_composite(background, rgba)
        return np.asarray(img.convert("RGB"), dtype=np.uint8).copy()
    except ImageLoadError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageLoadError(f"無法解析影像檔案，可能已損毀或格式不正確。（{exc}）") from exc
