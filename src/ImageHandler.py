
import cv2
import numpy as np
from PIL import Image

from src.Error import ReadError


class ImageHandler:
    def __init__(self, fp: str, webimg=None):
        if fp:
            self.img = self._read_image_from_path(fp)
        elif webimg is not None:
            self.img = self._read_image_from_webview(webimg)
        else:
            raise ValueError("Either fp or webimg must be provided.")

        self.org_img = self.img.copy()
        self.height, self.width, self.color = self.img.shape
        self.fp = fp

    def _read_image_from_path(self, fp: str) -> np.ndarray:
        img = cv2.imread(fp, cv2.IMREAD_COLOR)
        if img is None:
            raise ReadError(f"Failed to read image from path: {fp}")
        return img / 255.0

    def _read_image_from_webview(self, webimg) -> np.ndarray:
        img = np.array(webimg)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img / 255.0

    def save_image(self, fp: str, img: np.ndarray) -> None:
        cv2.imwrite(fp, img, [cv2.IMWRITE_JPEG_QUALITY, 100])

    def get_image_data(self) -> tuple[np.ndarray, int, int, int]:
        return self.img, self.height, self.width, self.color

    def get_org_image(self) -> np.ndarray:
        return self.org_img
