import glob
import os

import numpy as np
import pytest

from imagelab.detection.base import Detection, normalize_confidence
from imagelab.detection.draw import draw_detections

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "samples")


def _haar_or_skip():
    """Haar 偵測只在 OpenCV 4.x 可用；5.x 沒有 CascadeClassifier 時略過。"""
    cv2 = pytest.importorskip("cv2")
    if not hasattr(cv2, "CascadeClassifier"):
        pytest.skip("此 OpenCV 版本沒有 CascadeClassifier")
    from imagelab.detection.haar_detector import detect_faces
    return detect_faces


def test_confidence_is_monotonic_and_bounded():
    values = [normalize_confidence(w) for w in (-3, 0, 0.5, 2, 5, 20, 1000)]
    assert values[0] == values[1] == 0.0
    assert all(a <= b for a, b in zip(values, values[1:]))
    assert all(0.0 <= v < 1.0 or v == 1.0 for v in values)
    assert abs(normalize_confidence(2.0) - 0.6321) < 1e-3


def test_detection_box_property():
    assert Detection(10, 20, 30, 40, 1.0, 0.4).box == (10, 20, 40, 60)


def test_draw_does_not_modify_input_and_marks_box(random_rgb):
    before = random_rgb.copy()
    out = draw_detections(random_rgb, [Detection(5, 8, 20, 16, 3.0, 0.78)])
    assert np.array_equal(random_rgb, before)
    assert out.shape == random_rgb.shape and out.dtype == np.uint8
    assert not np.array_equal(out, random_rgb)


def test_draw_with_no_detections_is_identical_copy(random_rgb):
    out = draw_detections(random_rgb, [])
    assert np.array_equal(out, random_rgb) and out is not random_rgb


def test_draw_box_at_image_corner_does_not_crash(random_rgb):
    draw_detections(random_rgb, [Detection(0, 0, 10, 10, 1.0, 0.4)])


def test_parameter_validation(random_rgb):
    pytest.importorskip("cv2")
    from imagelab.detection.haar_detector import detect_faces
    with pytest.raises(ValueError, match="scaleFactor"):
        detect_faces(random_rgb, scale_factor=1.0)
    with pytest.raises(ValueError, match="minNeighbors"):
        detect_faces(random_rgb, min_neighbors=0)
    with pytest.raises(ValueError, match="尺寸"):
        detect_faces(random_rgb, min_size=0)
    with pytest.raises(ValueError, match="RGB"):
        detect_faces(random_rgb[..., 0])
    with pytest.raises(ValueError, match="RGB"):
        detect_faces(random_rgb.astype(np.float32))


def test_flat_image_has_no_faces():
    detect_faces = _haar_or_skip()
    assert detect_faces(np.full((200, 300, 3), 128, dtype=np.uint8)) == []


def test_tiny_image_returns_empty_without_crashing():
    detect_faces = _haar_or_skip()
    assert detect_faces(np.zeros((10, 10, 3), dtype=np.uint8)) == []
    assert detect_faces(np.zeros((1, 1, 3), dtype=np.uint8)) == []


def test_min_size_larger_than_image_returns_empty():
    detect_faces = _haar_or_skip()
    assert detect_faces(np.full((60, 60, 3), 90, dtype=np.uint8), min_size=500) == []


def test_real_sample_images_if_present():
    """assets/samples 內若放了含人臉的照片，至少應偵測到一張臉，且框與信心度合法。"""
    detect_faces = _haar_or_skip()
    from imagelab.io.loader import load_image
    files = [f for ext in ("jpg", "jpeg", "png", "bmp")
             for f in glob.glob(os.path.join(SAMPLE_DIR, f"face*.{ext}"))]
    if not files:
        pytest.skip("assets/samples 內沒有 face*.jpg|png 範例圖")
    for path in files:
        with open(path, "rb") as fh:
            rgb = load_image(fh.read())
        dets = detect_faces(rgb, min_neighbors=3)
        assert len(dets) >= 1, path
        h, w = rgb.shape[:2]
        for d in dets:
            assert 0 <= d.x < d.x + d.w <= w and 0 <= d.y < d.y + d.h <= h
            assert 0.0 <= d.confidence < 1.0
        assert [d.confidence for d in dets] == sorted((d.confidence for d in dets), reverse=True)
