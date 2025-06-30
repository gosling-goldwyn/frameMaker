import os
import sys
import pytest
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.ImageHandler import ImageHandler, ReadError


@pytest.fixture
def image_handler():
    # テスト用の画像ファイルパス
    test_image_path = "tests/assets/test_image.png"
    return ImageHandler(fp=test_image_path)


def test_read_image_from_path(image_handler):
    assert image_handler.img is not None
    assert isinstance(image_handler.img, np.ndarray)


def test_read_image_from_path_not_found():
    with pytest.raises(ReadError):
        ImageHandler(fp="tests/assets/not_found.png")