import os
import sys

import numpy as np
import pytest
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from src.constants import GOLDEN_RATIO, MAX_FRAME_RATIO, MIN_FRAME_RATIO, SILVER_RATIO
from src.FrameMaker import FrameMaker
from src.ImageHandler import ImageHandler
from src.WebviewInterface import (
    API,
    pillow_image_to_base64_string,
    resolve_frame_ratio,
    validate_frame_ratio,
)


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
        sample_image_handler_tall,
        golden=True,
        bgcolor="#FFFFFF",
        rounded=False,
        mc=False,
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
        sample_image_handler_wide,
        golden=True,
        bgcolor="#000000",
        rounded=False,
        mc=False,
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


def test_frame_maker_silver_ratio_frame(sample_image_handler_wide):
    """
    横長の画像に対して、白銀比に基づいたフレームが正しく適用されることを確認する。
    """
    fm = FrameMaker(
        sample_image_handler_wide,
        golden=True,
        bgcolor="#FFFFFF",
        rounded=False,
        mc=False,
        golden_ratio=SILVER_RATIO,
    )
    result_img = fm.run()

    expected_side_length = int(
        max(sample_image_handler_wide.height, sample_image_handler_wide.width)
        * SILVER_RATIO
    )

    assert result_img.shape[0] == expected_side_length
    assert result_img.shape[1] == expected_side_length


def test_frame_maker_custom_ratio_frame(sample_image_handler_wide):
    """
    任意比率に基づいたフレームが正しく適用されることを確認する。
    """
    custom_ratio = 1.333
    fm = FrameMaker(
        sample_image_handler_wide,
        golden=True,
        bgcolor="#FFFFFF",
        rounded=False,
        mc=False,
        golden_ratio=custom_ratio,
    )
    result_img = fm.run()

    expected_side_length = int(
        max(sample_image_handler_wide.height, sample_image_handler_wide.width)
        * custom_ratio
    )

    assert result_img.shape[0] == expected_side_length
    assert result_img.shape[1] == expected_side_length


def test_resolve_frame_ratio_modes():
    assert resolve_frame_ratio("none") == (False, GOLDEN_RATIO)
    assert resolve_frame_ratio("golden") == (True, GOLDEN_RATIO)
    assert resolve_frame_ratio("silver") == (True, SILVER_RATIO)
    assert resolve_frame_ratio(1.0) == (True, 1.0)
    assert resolve_frame_ratio("1.333") == (True, 1.333)
    assert resolve_frame_ratio(1.414) == (True, 1.414)
    assert resolve_frame_ratio(1.618) == (True, 1.618)
    assert resolve_frame_ratio(1.732) == (True, 1.732)
    assert resolve_frame_ratio(True) == (True, GOLDEN_RATIO)
    assert resolve_frame_ratio(False) == (False, GOLDEN_RATIO)


def test_validate_frame_ratio_rejects_out_of_range_values():
    assert validate_frame_ratio(MIN_FRAME_RATIO) == MIN_FRAME_RATIO
    assert validate_frame_ratio(MAX_FRAME_RATIO) == MAX_FRAME_RATIO

    with pytest.raises(ValueError):
        validate_frame_ratio(0.999)

    with pytest.raises(ValueError):
        validate_frame_ratio(1.733)

    with pytest.raises(ValueError):
        resolve_frame_ratio("invalid")


class FakeSaveWindow:
    def __init__(self, save_path):
        self.save_path = save_path

    def create_file_dialog(self, *args, **kwargs):
        return (str(self.save_path),)


class FakeCancelWindow:
    def create_file_dialog(self, *args, **kwargs):
        return None


def test_api_does_not_expose_public_window_attribute():
    api = API()
    api.set_window(FakeCancelWindow())

    assert not hasattr(api, "window")


def test_save_frame_maker_from_webview_with_dialog(tmp_path, sample_image_handler):
    save_target = tmp_path / "selected-output.jpg"
    img = Image.fromarray((sample_image_handler.org_img[:, :, ::-1] * 255).astype(np.uint8))
    inputdata = "data:image/jpeg;base64," + pillow_image_to_base64_string(img)
    api = API()
    api.set_window(FakeSaveWindow(save_target))

    save_path = api.saveFrameMakerFromWebview(
        inputdata,
        1.0,
        "#FFFFFF",
        False,
        False,
    )

    assert save_path
    assert save_path == str(save_target)
    assert os.path.exists(save_target)


def test_save_frame_maker_from_webview_with_radius(tmp_path, sample_image_handler):
    save_target = tmp_path / "selected-output.jpg"
    img = Image.fromarray((sample_image_handler.org_img[:, :, ::-1] * 255).astype(np.uint8))
    inputdata = "data:image/jpeg;base64," + pillow_image_to_base64_string(img)
    api = API()
    api.set_window(FakeSaveWindow(save_target))

    save_path = api.saveFrameMakerFromWebview(
        inputdata,
        1.0,
        "#FFFFFF",
        True,
        False,
        radius=80,
    )

    assert save_path == str(save_target)
    assert os.path.exists(save_target)


def test_save_frame_maker_from_webview_cancel(tmp_path, sample_image_handler):
    img = Image.fromarray((sample_image_handler.org_img[:, :, ::-1] * 255).astype(np.uint8))
    inputdata = "data:image/jpeg;base64," + pillow_image_to_base64_string(img)
    api = API()
    api.set_window(FakeCancelWindow())

    save_path = api.saveFrameMakerFromWebview(
        inputdata,
        1.0,
        "#FFFFFF",
        False,
        False,
    )

    assert save_path == "cancelled"
    assert not list(tmp_path.iterdir())


def test_save_frame_maker_from_webview_adds_jpg_extension(
    tmp_path, sample_image_handler
):
    save_target = tmp_path / "selected-output"
    img = Image.fromarray((sample_image_handler.org_img[:, :, ::-1] * 255).astype(np.uint8))
    inputdata = "data:image/jpeg;base64," + pillow_image_to_base64_string(img)
    api = API()
    api.set_window(FakeSaveWindow(save_target))

    save_path = api.saveFrameMakerFromWebview(
        inputdata,
        1.0,
        "#FFFFFF",
        False,
        False,
    )

    assert save_path == str(save_target.with_suffix(".jpg"))
    assert os.path.exists(save_target.with_suffix(".jpg"))


def test_save_frame_maker_from_webview_replaces_unsupported_extension(
    tmp_path, sample_image_handler
):
    save_target = tmp_path / "selected-output.gif"
    img = Image.fromarray((sample_image_handler.org_img[:, :, ::-1] * 255).astype(np.uint8))
    inputdata = "data:image/jpeg;base64," + pillow_image_to_base64_string(img)
    api = API()
    api.set_window(FakeSaveWindow(save_target))

    save_path = api.saveFrameMakerFromWebview(
        inputdata,
        1.0,
        "#FFFFFF",
        False,
        False,
    )

    assert save_path == str(save_target.with_suffix(".jpg"))
    assert os.path.exists(save_target.with_suffix(".jpg"))


def test_frame_maker_no_golden_ratio_white_frame(sample_image_handler):
    """
    正方形の画像に対して、黄金比を適用しない白いフレームが正しく適用されることを確認する。

    テスト対象機能: FrameMakerのgolden=False, black=Falseオプション
    期待結果: 出力画像の縦横サイズが元の画像の最大辺の長さであり、フレーム部分が白であること。
    """
    fm = FrameMaker(
        sample_image_handler, golden=False, bgcolor="#FFFFFF", rounded=False, mc=False
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
        sample_image_handler_tall,
        golden=False,
        bgcolor="#000000",
        rounded=False,
        mc=False,
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
        sample_image_handler, golden=False, bgcolor="#FFFFFF", rounded=True, mc=False
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
        sample_image_handler, golden=False, bgcolor="#000000", rounded=True, mc=False
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
        sample_image_handler_colored,
        golden=False,
        bgcolor="#FFFFFF",
        rounded=False,
        mc=True,
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
        sample_image_handler_colored,
        golden=False,
        bgcolor="#FFFFFF",
        rounded=True,
        mc=True,
    )
    result_img = fm.run()

    # 角が白であることを確認（rounded_white_frameと同じロジック）
    assert np.all(result_img[0, 0] == 255)

    # カラーバーの高さの期待値を計算
    expected_pick_height = int((sample_image_handler_colored.height * 0.309) // 30)

    # カラーバーの領域が完全に白ではないことを確認
    color_bar_area = result_img[result_img.shape[0] - expected_pick_height :, :]
    assert not np.all(color_bar_area == 255)


def test_frame_maker_custom_background_color(sample_image_handler):
    """
    カスタム背景色が正しく適用されることを確認する。

    テスト対象機能: FrameMakerのbgcolorオプション
    期待結果: 出力画像のフレーム部分が指定された色（赤）であること。
    """
    fm = FrameMaker(
        sample_image_handler, golden=True, bgcolor="#FF0000", rounded=False, mc=False
    )
    result_img = fm.run()

    # フレーム部分が赤であることを確認（例：角のピクセル）
    # OpenCVはBGR順なので、(0, 0, 255)が赤に対応
    assert np.all(result_img[0, 0] == [0, 0, 255])
