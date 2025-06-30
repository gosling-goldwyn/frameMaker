import os
import sys

import numpy as np
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.ImageHandler import ImageHandler, ReadError


@pytest.fixture
def image_handler():
    # テスト用の画像ファイルパス
    test_image_path = "tests/assets/test_image.png"
    return ImageHandler(fp=test_image_path)


def test_read_image_from_path(image_handler):
    """
    指定されたファイルパスから画像を正しく読み込めることを確認する。

    テスト対象機能: ImageHandlerの画像読み込み機能
    期待結果: ImageHandlerオブジェクトのimg属性がNoneではなく、numpy.ndarray型であること。
    """
    assert image_handler.img is not None
    assert isinstance(image_handler.img, np.ndarray)


def test_read_image_from_path_not_found():
    """
    存在しないファイルパスを指定した場合にReadErrorが送出されることを確認する。

    テスト対象機能: ImageHandlerの画像読み込み時のエラーハンドリング
    期待結果: ReadErrorが送出されること。
    """
    with pytest.raises(ReadError):
        ImageHandler(fp="tests/assets/not_found.png")
