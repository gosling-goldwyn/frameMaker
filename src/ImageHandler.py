import cv2
import numpy as np

from src.Error import ReadError


class ImageHandler:
    """
    画像の読み込み、処理、保存を扱うクラス。
    ファイルパスまたは WebView からの画像データをサポートします。
    """

    def __init__(self, fp: str, webimg=None):
        """
        ImageHandler クラスのコンストラクタ。

        Args:
            fp (str): 画像ファイルのパス。webimg が指定されない場合に使用されます。
            webimg (PIL.Image.Image, optional): WebView からの PIL Image オブジェクト。
                                                fp が指定されない場合に使用されます。
        Raises:
            ValueError: fp または webimg のどちらも指定されない場合。
        """
        if fp:
            self.img = self._read_image_from_path(fp)
        elif webimg is not None:
            self.img = self._read_image_from_webview(webimg)
        else:
            raise ValueError("Either fp or webimg must be provided.")

        self.org_img = self.img.copy()
        self.height, self.width, _ = self.img.shape  # self.color は不要
        self.fp = fp

    def _read_image_from_path(self, fp: str) -> np.ndarray:
        """
        指定されたパスから画像を読み込み、NumPy 配列として返します。

        Args:
            fp (str): 画像ファイルのパス。

        Returns:
            np.ndarray: 読み込まれた画像データ (NumPy 配列、0-1 の範囲に正規化)。

        Raises:
            ReadError: 画像の読み込みに失敗した場合。
        """
        img = cv2.imread(fp, cv2.IMREAD_COLOR)
        if img is None:
            raise ReadError(f"Failed to read image from path: {fp}")
        return img / 255.0

    def _read_image_from_webview(self, webimg) -> np.ndarray:
        """
        WebView からの PIL Image オブジェクトを NumPy 配列に変換します。

        Args:
            webimg (PIL.Image.Image): WebView からの PIL Image オブジェクト。

        Returns:
            np.ndarray: 変換された画像データ (NumPy 配列、0-1 の範囲に正規化)。
        """
        img = np.array(webimg)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img / 255.0

    def save_image(self, fp: str, img: np.ndarray) -> None:
        """
        画像を指定されたパスに保存します。

        Args:
            fp (str): 画像を保存するパス。
            img (np.ndarray): 保存する画像データ (NumPy 配列)。
        """
        cv2.imwrite(fp, img, [cv2.IMWRITE_JPEG_QUALITY, 100])

    def get_image_data(self) -> tuple[np.ndarray, int, int, int]:
        """
        現在の画像データ、高さ、幅、色チャンネル数を返します。

        Returns:
            tuple[np.ndarray, int, int, int]: (画像データ, 高さ, 幅, 色チャンネル数)。
        """
        return self.img, self.height, self.width, self.color

    def get_org_image(self) -> np.ndarray:
        """
        元の画像データ (処理前の画像) を返します。

        Returns:
            np.ndarray: 元の画像データ (NumPy 配列)。
        """
        return self.org_img
