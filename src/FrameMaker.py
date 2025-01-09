import cv2
import numpy as np
from PIL import Image, ImageDraw

from src.colorpick import getMainColorKmeans
from src.Error import ReadError

GOLDEN_RATIO = 1.618
SIDE_MARGIN_RATIO = 0.309  # (1-GOLDEN_RATIO)/2s


class FrameMaker:
    radius = 40

    def __init__(self, fp, golden, black, rounded, mc, webimg=None):
        if fp != "":
            img = cv2.imread(fp, cv2.IMREAD_COLOR)

            # 読み込みに失敗すると例外
            if img is None:
                raise ReadError()
        else:
            img = np.array(webimg)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        self.img = img / 255
        self.org_img = self.img

        self.height, self.width, self.color = img.shape

        self.golden = golden
        self.black = black
        self.rounded = rounded
        self.mc = mc
        self.transpose = False
        self.is_square = self.height == self.width
        self.fp = fp
        self.is_width_base = False
        if self.rounded:
            mask = Image.new(
                "RGB", (self.width, self.height), "Black" if self.black else "White"
            )
            pil_roundmask = ImageDraw.Draw(mask)
            pil_roundmask.rounded_rectangle(
                [(1, 1), (self.width - 1, self.height - 1)],
                radius=self.radius,
                fill="White" if self.black else "Black",
                outline="White" if self.black else "Black",
                width=1,
            )
            self.roundmask = np.array(mask) / 255

    def run(self) -> np.ndarray:
        if self.rounded:
            self.img = (
                np.where(self.roundmask == 0, 0, self.img)
                if self.black
                else np.where(self.roundmask == 1, 1, self.img)
            )
        # 縦長なら転置して横長にする
        if self.height > self.width:
            self.img = self.img.transpose(1, 0, 2)
            self.height, self.width, self.color = self.img.shape
            self.transpose = True
        elif int((1.618 * self.height - self.width) // 2) < 0:
            self.golden = False

        # 新しい画像の辺の長さを計算(黄金比1.618に基づく)
        if self.height < self.width:
            new_width = (
                int(self.height * GOLDEN_RATIO) if self.golden else int(self.width)
            )
        else:
            new_width = int(self.height * GOLDEN_RATIO)

        # 白枠をつけるか黒枠をつけるか
        new_img = (
            np.zeros([new_width, new_width, self.color], dtype="float64")
            if self.black
            else np.ones([new_width, new_width, self.color], dtype="float64")
        )

        # 画像を枠の中に配置する起点の計算
        if self.is_square:
            sh = int(self.height * SIDE_MARGIN_RATIO)
            sw = int(self.width * SIDE_MARGIN_RATIO)
        elif self.golden:
            sh = int(self.height * SIDE_MARGIN_RATIO)
            sw = int((GOLDEN_RATIO * self.height - self.width) // 2)
        else:
            sh = (self.width - self.height) // 2
            sw = 0

        new_img[sh : sh + self.height, sw : sw + self.width] = self.img

        if self.mc:
            pickwidth = int(self.width // 5)
            pickheight = int((self.height * SIDE_MARGIN_RATIO) // 30)
            picker = getMainColorKmeans(self.org_img, pickwidth, pickheight)
            new_img[new_width - pickheight : new_width, sw : sw + pickwidth * 5] = (
                picker / 255
            )

        if self.transpose:
            new_img = new_img.transpose(1, 0, 2)

        return (new_img * 255).astype(int)
