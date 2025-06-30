import os
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.FrameMaker import FrameMaker
from src.ImageHandler import ImageHandler


@pytest.fixture
def sample_image_handler():
    # 100x100の白い画像を生成
    img_array = np.ones((100, 100, 3), dtype=np.uint8) * 255
    img_pil = Image.fromarray(img_array)
    return ImageHandler(fp="", webimg=img_pil)


@pytest.fixture
def sample_image_handler_tall():
    # 50x100の白い画像を生成 (height=100, width=50)
    img_array = np.ones((100, 50, 3), dtype=np.uint8) * 255
    img_pil = Image.fromarray(img_array)
    return ImageHandler(fp="", webimg=img_pil)


@pytest.fixture
def sample_image_handler_wide():
    # 100x50の白い画像を生成 (height=50, width=100)
    img_array = np.ones((50, 100, 3), dtype=np.uint8) * 255
    img_pil = Image.fromarray(img_array)
    return ImageHandler(fp="", webimg=img_pil)


@pytest.fixture
def sample_image_handler_colored():
    # 100x100のカラー画像を生成
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    # 左上を赤
    img_array[0:50, 0:50] = [255, 0, 0]
    # 右上を緑
    img_array[0:50, 50:100] = [0, 255, 0]
    # 左下を青
    img_array[50:100, 0:50] = [0, 0, 255]
    # 右下を黄
    img_array[50:100, 50:100] = [255, 255, 0]
    img_pil = Image.fromarray(img_array)
    return ImageHandler(fp="", webimg=img_pil)


def test_frame_maker_golden_ratio_white_frame(sample_image_handler_tall):
    """
    縦長の画像に対して、黄金比に基づいた白いフレームが正しく適用されることを確認する。

    テスト対象機能: FrameMakerのgolden=True, black=Falseオプション
    期待結果: 出力画像の縦横サイズが期待される黄金比に基づいたサイズであり、フレーム部分が白であること。
    """
    fm = FrameMaker(
        sample_image_handler_tall, golden=True, black=False, rounded=False, mc=False
    )
    result_img = fm.run()

    # src/FrameMaker.pyのロジックに基づくと、
    # target_side_length = int(max(original_height, original_width) * golden_ratio)
    expected_side_length = int(
        max(sample_image_handler_tall.height, sample_image_handler_tall.width) * 1.618
    )

    assert result_img.shape[0] == expected_side_length
    assert result_img.shape[1] == expected_side_length

    # フレーム部分が白であることを確認（例：角のピクセル）
    assert np.all(result_img[0, 0] == 255)  # 左上
    assert np.all(result_img[-1, -1] == 255)  # 右下


def test_frame_maker_golden_ratio_black_frame(sample_image_handler_wide):
    """
    横長の画像に対して、黄金比に基づいた黒いフレームが正しく適用されることを確認する。

    テスト対象機能: FrameMakerのgolden=True, black=Trueオプション
    期待結果: 出力画像の縦横サイズが期待される黄金比に基づいたサイズであり、フレーム部分が黒であること。
    """
    fm = FrameMaker(
        sample_image_handler_wide, golden=True, black=True, rounded=False, mc=False
    )
    result_img = fm.run()

    # src/FrameMaker.pyのロジックに基づくと、
    # target_side_length = int(max(original_height, original_width) * golden_ratio)
    expected_side_length = int(
        max(sample_image_handler_wide.height, sample_image_handler_wide.width) * 1.618
    )

    assert result_img.shape[0] == expected_side_length
    assert result_img.shape[1] == expected_side_length

    # フレーム部分が黒であることを確認（例：角のピクセル）
    assert np.all(result_img[0, 0] == 0)  # 左上
    assert np.all(result_img[-1, -1] == 0)  # 右下


def test_frame_maker_no_golden_ratio_white_frame(sample_image_handler):
    """
    正方形の画像に対して、黄金比を適用しない白いフレームが正しく適用されることを確認する。

    テスト対象機能: FrameMakerのgolden=False, black=Falseオプション
    期待結果: 出力画像の縦横サイズが元の画像の最大辺の長さであり、フレーム部分が白であること。
    """
    fm = FrameMaker(
        sample_image_handler, golden=False, black=False, rounded=False, mc=False
    )
    result_img = fm.run()

    # src/FrameMaker.pyのロジックに基づくと、
    # target_side_length = max(original_height, original_width)
    expected_side_length = max(sample_image_handler.height, sample_image_handler.width)

    assert result_img.shape[0] == expected_side_length
    assert result_img.shape[1] == expected_side_length

    # フレーム部分が白であることを確認
    assert np.all(result_img[0, 0] == 255)


def test_frame_maker_no_golden_ratio_black_frame(sample_image_handler_tall):
    """
    縦長の画像に対して、黄金比を適用しない黒いフレームが正しく適用されることを確認する。

    テスト対象機能: FrameMakerのgolden=False, black=Trueオプション
    期待結果: 出力画像の縦横サイズが元の画像の最大辺の長さであり、フレーム部分が黒であること。
    """
    fm = FrameMaker(
        sample_image_handler_tall, golden=False, black=True, rounded=False, mc=False
    )
    result_img = fm.run()

    # src/FrameMaker.pyのロジックに基づくと、
    # target_side_length = max(original_height, original_width)
    expected_side_length = max(
        sample_image_handler_tall.height, sample_image_handler_tall.width
    )

    assert result_img.shape[0] == expected_side_length
    assert result_img.shape[1] == expected_side_length

    # フレーム部分が黒であることを確認
    assert np.all(result_img[0, 0] == 0)


def test_frame_maker_rounded_white_frame(sample_image_handler):
    """
    正方形の画像に対して、角丸の白いフレームが正しく適用されることを確認する。

    テスト対象機能: FrameMakerのrounded=True, black=Falseオプション
    期待結果: 出力画像のフレーム部分が白であり、角が丸められていること。
    """
    fm = FrameMaker(
        sample_image_handler, golden=False, black=False, rounded=True, mc=False
    )
    result_img = fm.run()

    # フレーム部分が白であることを確認
    assert np.all(result_img[0, 0] == 255)


def test_frame_maker_rounded_black_frame(sample_image_handler):
    """
    正方形の画像に対して、角丸の黒いフレームが正しく適用されることを確認する。

    テスト対象機能: FrameMakerのrounded=True, black=Trueオプション
    期待結果: 出力画像のフレーム部分が黒であり、角が丸められていること。
    """
    fm = FrameMaker(
        sample_image_handler, golden=False, black=True, rounded=True, mc=False
    )
    result_img = fm.run()

    # フレーム部分が黒であることを確認
    assert np.all(result_img[0, 0] == 0)


def test_frame_maker_main_color_bar(sample_image_handler_colored):
    """
    カラー画像に対して、メインカラーバーが正しく適用されることを確認する。

    テスト対象機能: FrameMakerのmc=Trueオプション
    期待結果: 出力画像にカラーバーが追加され、その領域が完全に白ではないこと。
    """
    fm = FrameMaker(
        sample_image_handler_colored, golden=False, black=False, rounded=False, mc=True
    )
    result_img = fm.run()

    # カラーバーの高さの期待値を計算
    expected_pick_height = int((sample_image_handler_colored.height * 0.309) // 30)

    # カラーバーの領域が完全に白ではないことを確認
    color_bar_area = result_img[result_img.shape[0] - expected_pick_height :, :]
    assert not np.all(color_bar_area == 255)


def test_frame_maker_rounded_and_main_color_bar(sample_image_handler_colored):
    """
    カラー画像に対して、角丸とメインカラーバーが組み合わせて正しく適用されることを確認する。

    テスト対象機能: FrameMakerのrounded=True, mc=Trueオプション
    期待結果: 出力画像の角が丸められ、カラーバーが追加され、その領域が完全に白ではないこと。
    """
    fm = FrameMaker(
        sample_image_handler_colored, golden=False, black=False, rounded=True, mc=True
    )
    result_img = fm.run()

    # 角が白であることを確認（rounded_white_frameと同じロジック）
    assert np.all(result_img[0, 0] == 255)

    # カラーバーの高さの期待値を計算
    expected_pick_height = int((sample_image_handler_colored.height * 0.309) // 30)

    # カラーバーの領域が完全に白ではないことを確認
    color_bar_area = result_img[result_img.shape[0] - expected_pick_height :, :]
    assert not np.all(color_bar_area == 255)
