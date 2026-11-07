"""影像中繼資訊：解析度、色彩維度、檔案大小等。"""
from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image

_MODE_CHANNELS = {"1": 1, "L": 1, "P": 1, "I": 1, "F": 1, "LA": 2, "RGB": 3, "YCbCr": 3,
                  "RGBA": 4, "CMYK": 4}
_MODE_DESC = {"1": "二值", "L": "灰階", "P": "調色盤索引色", "LA": "灰階+透明",
              "RGB": "RGB 真彩色", "RGBA": "RGB+透明", "CMYK": "CMYK", "YCbCr": "YCbCr"}


@dataclass(frozen=True)
class ImageMetadata:
    filename: str
    format: str
    width: int
    height: int
    mode: str
    channels: int
    file_size_bytes: int

    @property
    def resolution(self) -> str:
        return f"{self.width} × {self.height}"

    @property
    def megapixels(self) -> float:
        return self.width * self.height / 1e6

    @property
    def mode_description(self) -> str:
        return _MODE_DESC.get(self.mode, self.mode)

    @property
    def file_size_text(self) -> str:
        size = float(self.file_size_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} GB"


def get_metadata(data: bytes, filename: str = "") -> ImageMetadata:
    """讀取原始檔案的中繼資訊（顯示的是檔案原始色彩模式，而非轉換後的 RGB）。"""
    img = Image.open(io.BytesIO(data))
    return ImageMetadata(
        filename=filename,
        format=img.format or "UNKNOWN",
        width=img.width,
        height=img.height,
        mode=img.mode,
        channels=_MODE_CHANNELS.get(img.mode, len(img.getbands())),
        file_size_bytes=len(data),
    )
