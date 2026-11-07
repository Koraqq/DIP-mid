import numpy as np
import pytest

from imagelab.analysis.histogram import compute_histogram, plot_histogram


def test_histogram_length_and_total(random_rgb):
    ch = random_rgb[..., 0]
    h = compute_histogram(ch)
    assert h.shape == (256,) and h.sum() == ch.size


def test_histogram_known_values():
    ch = np.array([[0, 0, 255], [255, 255, 7]], dtype=np.uint8)
    h = compute_histogram(ch)
    assert h[0] == 2 and h[255] == 3 and h[7] == 1


def test_rejects_non_uint8():
    with pytest.raises(ValueError):
        compute_histogram(np.zeros((2, 2), dtype=np.float32))


def test_plot_axes_labels(random_rgb):
    fig = plot_histogram([("R", compute_histogram(random_rgb[..., 0]))], title="t")
    ax = fig.axes[0]
    assert ax.get_xlim() == (0, 255) and "intensity" in ax.get_xlabel()


def test_title_falls_back_to_english_without_cjk_font(monkeypatch, random_rgb):
    monkeypatch.setattr("imagelab.analysis.histogram.CJK_FONT", None)
    fig = plot_histogram([("R", compute_histogram(random_rgb[..., 0]))],
                         title="R 通道直方圖", title_en="R channel histogram")
    assert fig.axes[0].get_title() == "R channel histogram"


def test_title_ascii_fallback_when_no_english_given(monkeypatch, random_rgb):
    monkeypatch.setattr("imagelab.analysis.histogram.CJK_FONT", None)
    fig = plot_histogram([("R", compute_histogram(random_rgb[..., 0]))], title="R 通道 histogram")
    assert "通" not in fig.axes[0].get_title()


def test_title_kept_when_cjk_font_available(monkeypatch, random_rgb):
    monkeypatch.setattr("imagelab.analysis.histogram.CJK_FONT", "Some CJK Font")
    fig = plot_histogram([("R", compute_histogram(random_rgb[..., 0]))],
                         title="R 通道直方圖", title_en="R channel histogram")
    assert fig.axes[0].get_title() == "R 通道直方圖"
