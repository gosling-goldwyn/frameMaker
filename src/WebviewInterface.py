import base64
import io
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from src.Error import ReadError
from src.FrameMaker import FrameMaker
from src.ImageHandler import ImageHandler
from src.colorpick import getMainColorRGBValue
from src.constants import GOLDEN_RATIO, SIDE_MARGIN_RATIO, DEFAULT_RADIUS


def pillow_image_to_base64_string(img: Image) -> str:
    """
    PIL Image オブジェクトを Base64 エンコードされた JPEG 文字列に変換します。

    Args:
        img (PIL.Image.Image): 変換する PIL Image オブジェクト。

    Returns:
        str: Base64 エンコードされた JPEG 文字列。
    """
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def base64_string_to_pillow_image(base64_str: str) -> Image.Image:
    """
    Base64 エンコードされた文字列を PIL Image オブジェクトに変換します。

    Args:
        base64_str (str): Base64 エンコードされた画像データ文字列。

    Returns:
        PIL.Image.Image: 変換された PIL Image オブジェクト。
    """
    return Image.open(
        io.BytesIO(base64.decodebytes(bytes(base64_str.split(",")[1], "utf-8"))))


def get_save_path(base_filename: str, directory: str = ".") -> str:
    """
    指定されたディレクトリ内に、重複しないファイルパスを生成します。
    ファイル名が既に存在する場合は、連番を付加します。

    Args:
        base_filename (str): ベースとなるファイル名 (例: "output.jpg")。
        directory (str, optional): ファイルを保存するディレクトリ。デフォルトはカレントディレクトリ。

    Returns:
        str: 重複しないファイルパス。
    """
    # ファイル名のベースと拡張子を分ける
    base, ext = os.path.splitext(os.path.join(directory, base_filename))
    counter = 1
    filename = f"{base}{ext}"

    # ファイルが存在する場合、連番を付ける
    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    return filename


class API:
    """
    WebView と Python バックエンド間のインターフェースを提供するクラス。
    画像処理機能へのアクセスを提供します。
    """

    def runFrameMaker(
        self,
        inputpath: str,
        outputpath: str,
        golden: bool,
        black: bool,
        rounded: bool,
        maincolor: bool,
    ) -> None:
        """
        指定されたファイルパスの画像にフレーム処理を適用し、結果を保存します。

        Args:
            inputpath (str): 入力画像ファイルのパス。
            outputpath (str): 出力画像を保存するパス。
            golden (bool): 黄金比フレームを適用するかどうか。
            black (bool): 黒いフレームを適用するかどうか。
            rounded (bool): 角丸フレームを適用するかどうか。
            maincolor (bool): メインカラーバーを追加するかどうか。
        """
        try:
            handler = ImageHandler(fp=inputpath.replace("blob:", ""))
            fm = FrameMaker(
                handler, golden, black, rounded, maincolor, golden_ratio=GOLDEN_RATIO, side_margin_ratio=SIDE_MARGIN_RATIO
            )
            result = fm.run()
        except ReadError:
            print("Read Error: File doesn't exist (unsupported japanese characters)")
        else:
            handler.save_image(outputpath, result)

    def runFrameMakerFromWebview(
        self,
        inputdata: str,
        golden: bool,
        bgcolor: str,
        rounded: bool,
        maincolor: bool,
        radius: int = DEFAULT_RADIUS,
    ) -> str:
        """
        Base64 エンコードされた画像データにフレーム処理を適用し、結果を Base64 文字列で返します。

        Args:
            inputdata (str): Base64 エンコードされた入力画像データ。
            golden (bool): 黄金比フレームを適用するかどうか。
            black (bool): 黒いフレームを適用するかどうか。
            rounded (bool): 角丸フレームを適用するかどうか。
            maincolor (bool): メインカラーバーを追加するかどうか。
            radius (int, optional): 角丸の半径。デフォルトは constants.DEFAULT_RADIUS。

        Returns:
            str: Base64 エンコードされた処理済み画像データ。
        """
        try:
            webimg = base64_string_to_pillow_image(inputdata)
            handler = ImageHandler(fp="", webimg=webimg)
            fm = FrameMaker(
                handler, golden, bgcolor, rounded, maincolor, radius=radius, golden_ratio=GOLDEN_RATIO, side_margin_ratio=SIDE_MARGIN_RATIO
            )
            result = fm.run()
        except ReadError:
            print("Read Error: File doesn't exist (unsupported japanese characters)")
            return ""
        else:
            result = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(result)
            data_url = "data:image/jpeg;base64," + pillow_image_to_base64_string(
                pil_image
            )
            return data_url

    def saveImage(self, inputdata: str) -> None:
        """
        Base64 エンコードされた画像データをファイルとして保存します。

        Args:
            inputdata (str): Base64 エンコードされた画像データ。
        """
        webimg = base64_string_to_pillow_image(inputdata)
        # Use pathlib for cross-platform path handling
        downloads_path = Path.home() / "Downloads"
        downloads_path.mkdir(parents=True, exist_ok=True) # Ensure directory exists
        save_path = get_save_path("output.jpg", str(downloads_path))
        webimg.save(save_path, "JPEG", quality=95)

    def getMainColorRGBValue(
        self,
        inputdata: str,
    ) -> list[str]:
        """
        Base64 エンコードされた画像データから主要な色の RGB 値を取得します。

        Args:
            inputdata (str): Base64 エンコードされた入力画像データ。
        Returns:
            list[str]: 主要な色の RGB 値のリスト (例: ["RRGGBB", ...])。
        """
        try:
            webimg = base64_string_to_pillow_image(inputdata)
            handler = ImageHandler(fp="", webimg=webimg)
            # FrameMakerのインスタンスは不要。直接colorpickの関数を呼び出す
            result = getMainColorRGBValue(handler.org_img)
            return result
        except ReadError:
            # Consider logging this error instead of printing
            print("Read Error: File doesn't exist (unsupported japanese characters)")
            return ""
