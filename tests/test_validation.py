import numpy as np
import pytest

from imagelab.validation.errors import KernelError
from imagelab.validation.guards import check_kernel_fits_image, kernel_warnings
from imagelab.validation.matrix_parser import parse_kernel


def test_parse_basic_whitespace():
    k = parse_kernel("0 -1 0\n-1 5 -1\n0 -1 0")
    assert k.shape == (3, 3) and k[1, 1] == 5 and k[0, 1] == -1


def test_parse_commas_semicolons_and_blank_lines():
    k = parse_kernel("\n1,2,1; 2,4,2; 1,2,1\n\n")
    assert k.shape == (3, 3) and k.sum() == 16


def test_parse_fullwidth_characters():
    k = parse_kernel("０，−１，０\n−１，５，−１\n０，−１，０")
    assert k[1, 1] == 5 and k[0, 1] == -1


def test_parse_float_and_scientific():
    k = parse_kernel("0.5 1e-1 0\n0 1 0\n0 0 -2.5")
    assert abs(k[0, 1] - 0.1) < 1e-12 and k[2, 2] == -2.5


def test_one_by_one_allowed():
    assert parse_kernel("5").shape == (1, 1)


def test_empty_input():
    for text in ["", "   \n  ", None]:
        with pytest.raises(KernelError, match="請輸入"):
            parse_kernel(text)


def test_non_square_rejected():
    with pytest.raises(KernelError, match="方陣"):
        parse_kernel("1 2 3\n4 5 6")


def test_ragged_rows_rejected():
    with pytest.raises(KernelError, match="個數"):
        parse_kernel("1 2 3\n4 5\n6 7 8")


def test_even_size_rejected():
    with pytest.raises(KernelError, match="奇數"):
        parse_kernel("1 2\n3 4")
    with pytest.raises(KernelError, match="奇數"):
        parse_kernel("1 2 3 4\n1 2 3 4\n1 2 3 4\n1 2 3 4")


def test_bad_token_reports_position():
    with pytest.raises(KernelError, match="第 2 列第 3 格"):
        parse_kernel("1 2 3\n4 5 abc\n7 8 9")


def test_nan_and_inf_rejected():
    for bad in ["nan", "inf", "-inf", "1e999"]:
        with pytest.raises(KernelError, match="有限"):
            parse_kernel(f"1 {bad} 1\n1 1 1\n1 1 1")


def test_too_large_rejected():
    big = "\n".join(" ".join(["1"] * 17) for _ in range(17))
    with pytest.raises(KernelError, match="過大"):
        parse_kernel(big)


def test_kernel_larger_than_image_rejected():
    with pytest.raises(KernelError, match="還大"):
        check_kernel_fits_image(np.ones((5, 5)), (4, 10, 3))
    check_kernel_fits_image(np.ones((3, 3)), (3, 3, 3))  # 剛好相同尺寸可以


def test_warnings():
    assert any("全為 0" in m for m in kernel_warnings(np.zeros((3, 3)), False, 0.0))
    edge = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
    assert any("128" in m for m in kernel_warnings(edge, False, 0.0))
    assert kernel_warnings(edge, False, 128.0) == []
    neg = -np.ones((3, 3))
    assert any("反轉" in m for m in kernel_warnings(neg, True, 0.0))
    assert kernel_warnings(np.ones((3, 3)), True, 0.0) == []
