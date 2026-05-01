import base64
import io
import os
from numbers import Real
from pathlib import Path

import cv2
import numpy as np
import webview
from PIL import Image

from src.colorpick import getMainColorRGBValue
from src.constants import (
    DEFAULT_RADIUS,
    GOLDEN_RATIO,
    MAX_FRAME_RATIO,
    MIN_FRAME_RATIO,
    SIDE_MARGIN_RATIO,
    SILVER_RATIO,
)
from src.Error import ReadError
from src.FrameMaker import FrameMaker
from src.ImageHandler import ImageHandler


def validate_frame_ratio(frame_ratio: float) -> float:
    ratio = float(frame_ratio)
    if not MIN_FRAME_RATIO <= ratio <= MAX_FRAME_RATIO:
        raise ValueError(
            f"Frame ratio must be between {MIN_FRAME_RATIO} and {MAX_FRAME_RATIO}: "
            f"{ratio}"
        )
    return ratio


def resolve_frame_ratio(frame_mode) -> tuple[bool, float]:
    """
    フレーム比率モードを FrameMaker に渡す boolean と比率値に変換します。
    既存の boolean 入力は後方互換のため Golden として扱います。
    """
    if isinstance(frame_mode, Real) and not isinstance(frame_mode, bool):
        return True, validate_frame_ratio(frame_mode)

    if isinstance(frame_mode, str):
        mode = frame_mode.lower()
        if mode in ("none", "false", "off", ""):
            return False, GOLDEN_RATIO
        if mode == "golden":
            return True, GOLDEN_RATIO
        if mode == "silver":
            return True, SILVER_RATIO
        try:
            return True, validate_frame_ratio(float(mode))
        except ValueError as exc:
            raise ValueError(f"Unsupported frame ratio mode: {frame_mode}") from exc

    return bool(frame_mode), GOLDEN_RATIO


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

    def __init__(self):
        self._window = None

    def set_window(self, window) -> None:
        self._window = window

    def _choose_save_path(self) -> str | None:
        if self._window is None:
            downloads_path = Path.home() / "Downloads"
            downloads_path.mkdir(parents=True, exist_ok=True)
            return get_save_path("output.jpg", str(downloads_path))

        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename="output.jpg",
            file_types=(
                "JPEG Images (*.jpg;*.jpeg)",
                "PNG Images (*.png)",
                "All files (*.*)",
            ),
        )
        if not result:
            return None
        if isinstance(result, list | tuple):
            return result[0] if result else None
        return result

    @staticmethod
    def _normalize_save_path(save_path: str) -> str:
        path = Path(save_path)
        if path.suffix.lower() in (".jpg", ".jpeg", ".png"):
            return str(path)
        return str(path.with_suffix(".jpg"))

    def _save_frame_maker_to_path(
        self,
        inputdata: str,
        golden: bool | str,
        bgcolor: str,
        rounded: bool,
        maincolor: bool,
        save_path: str,
        radius: int = DEFAULT_RADIUS,
    ) -> str:
        webimg = base64_string_to_pillow_image(inputdata)
        handler = ImageHandler(fp="", webimg=webimg)
        use_ratio, frame_ratio = resolve_frame_ratio(golden)
        fm = FrameMaker(
            handler,
            use_ratio,
            bgcolor,
            rounded,
            maincolor,
            radius=radius,
            golden_ratio=frame_ratio,
            side_margin_ratio=SIDE_MARGIN_RATIO,
        )
        result = fm.run()
        normalized_path = self._normalize_save_path(save_path)
        Path(normalized_path).parent.mkdir(parents=True, exist_ok=True)
        handler.save_image(normalized_path, result)
        return normalized_path

    def runFrameMaker(
        self,
        inputpath: str,
        outputpath: str,
        golden: bool | str,
        black: bool,
        rounded: bool,
        maincolor: bool,
    ) -> None:
        """
        指定されたファイルパスの画像にフレーム処理を適用し、結果を保存します。

        Args:
            inputpath (str): 入力画像ファイルのパス。
            outputpath (str): 出力画像を保存するパス。
            golden (bool | str): 比率フレームを適用するか、比率モード。
            black (bool): 黒いフレームを適用するかどうか。
            rounded (bool): 角丸フレームを適用するかどうか。
            maincolor (bool): メインカラーバーを追加するかどうか。
        """
        try:
            handler = ImageHandler(fp=inputpath.replace("blob:", ""))
            use_ratio, frame_ratio = resolve_frame_ratio(golden)
            bgcolor = "#000000" if black else "#FFFFFF"
            fm = FrameMaker(
                handler,
                use_ratio,
                bgcolor,
                rounded,
                maincolor,
                golden_ratio=frame_ratio,
                side_margin_ratio=SIDE_MARGIN_RATIO,
            )
            result = fm.run()
        except ReadError:
            print("Read Error: File doesn't exist (unsupported japanese characters)")
        except ValueError as exc:
            print(exc)
        else:
            handler.save_image(outputpath, result)

    def runFrameMakerFromWebview(
        self,
        inputdata: str,
        golden: bool | str,
        bgcolor: str,
        rounded: bool,
        maincolor: bool,
        radius: int = DEFAULT_RADIUS,
    ) -> str:
        """
        Base64 エンコードされた画像データにフレーム処理を適用し、結果を Base64 文字列で返します。

        Args:
            inputdata (str): Base64 エンコードされた入力画像データ。
            golden (bool | str): 比率フレームを適用するか、比率モード。
            bgcolor (str): フレームの背景色。
            rounded (bool): 角丸フレームを適用するかどうか。
            maincolor (bool): メインカラーバーを追加するかどうか。
            radius (int, optional): 角丸の半径。デフォルトは constants.DEFAULT_RADIUS。

        Returns:
            str: Base64 エンコードされた処理済み画像データ。
        """
        try:
            webimg = base64_string_to_pillow_image(inputdata)
            handler = ImageHandler(fp="", webimg=webimg)
            use_ratio, frame_ratio = resolve_frame_ratio(golden)
            fm = FrameMaker(
                handler,
                use_ratio,
                bgcolor,
                rounded,
                maincolor,
                radius=radius,
                golden_ratio=frame_ratio,
                side_margin_ratio=SIDE_MARGIN_RATIO,
            )
            result = fm.run()
        except ReadError:
            print("Read Error: File doesn't exist (unsupported japanese characters)")
            return ""
        except ValueError as exc:
            print(exc)
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
        downloads_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        save_path = get_save_path("output.jpg", str(downloads_path))
        webimg.save(save_path, "JPEG", quality=95)

    def saveFrameMakerFromWebview(
        self,
        inputdata: str,
        golden: bool | str,
        bgcolor: str,
        rounded: bool,
        maincolor: bool,
        radius: int = DEFAULT_RADIUS,
    ) -> str:
        """
        Base64 エンコードされた画像データにフレーム処理を適用し、選択先に保存します。
        """
        try:
            save_path = self._choose_save_path()
            if not save_path:
                return "cancelled"
            return self._save_frame_maker_to_path(
                inputdata,
                golden,
                bgcolor,
                rounded,
                maincolor,
                save_path,
                radius=radius,
            )
        except (ReadError, ValueError) as exc:
            print(exc)
            return ""

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
