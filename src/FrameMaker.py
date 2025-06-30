import numpy as np
from PIL import Image, ImageDraw

from src.colorpick import getMainColorKmeans
from src.ImageHandler import ImageHandler


class FrameMaker:
    def __init__(
        self,
        hdl: ImageHandler,
        golden: bool,
        black: bool,
        rounded: bool,
        mc: bool,
        radius=40,
        golden_ratio=1.618,
        side_margin_ratio=0.309,
    ):
        self.img = hdl.img
        self.org_img = hdl.org_img

        self.height, self.width, self.color = hdl.img.shape

        self.golden = golden
        self.black = black
        self.rounded = rounded
        self.radius = radius
        self.mc = mc
        self.transpose = False
        self.is_square = self.height == self.width
        self.fp = hdl.fp
        self.is_width_base = False
        self.golden_ratio = golden_ratio
        self.side_margin_ratio = side_margin_ratio
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
        # 処理用の画像とサイズを一時変数にコピー
        current_img = self.img.copy()
        current_height, current_width, current_color = self.height, self.width, self.color

        if self.rounded:
            current_img = (
                np.where(self.roundmask == 0, 0, current_img)
                if self.black
                else np.where(self.roundmask == 1, 1, current_img)
            )

        # 縦長なら転置して横長にする
        transposed_for_processing = False
        if current_height > current_width:
            current_img = current_img.transpose(1, 0, 2)
            current_height, current_width, current_color = current_img.shape
            transposed_for_processing = True

        # 新しい画像の辺の長さを計算
        # 出力画像は常に正方形になるようにする
        if self.golden:
            # 黄金比を適用する場合、元の画像の長い辺を基準に黄金比を適用
            target_side_length = int(max(self.height, self.width) * self.golden_ratio)
        else:
            # 黄金比を適用しない場合、元の画像の長い辺を基準にする
            target_side_length = max(self.height, self.width)

        # 新しい画像のサイズが元の画像を収めるのに十分であることを保証
        target_side_length = max(target_side_length, current_height, current_width)

        # 白枠をつけるか黒枠をつけるか
        new_img = (
            np.zeros([target_side_length, target_side_length, current_color], dtype="float64")
            if self.black
            else np.ones([target_side_length, target_side_length, current_color], dtype="float64")
        )

        # 画像を枠の中に配置する起点の計算
        # current_imgの現在の形状（転置されている可能性のある形状）に基づいて中央に配置
        sh = (target_side_length - current_height) // 2
        sw = (target_side_length - current_width) // 2

        new_img[sh : sh + current_height, sw : sw + current_width] = current_img

        if self.mc:
            # メインカラーバーの計算は元の画像サイズを基準にする
            pickwidth = int(self.width // 5)
            pickheight = int((self.height * self.side_margin_ratio) // 30)
            picker = getMainColorKmeans(self.org_img, pickwidth, pickheight)

            # カラーバーを新しい正方形画像の下部に中央揃えで配置
            sw_for_color_bar = (target_side_length - pickwidth * 5) // 2
            new_img[target_side_length - pickheight : target_side_length, sw_for_color_bar : sw_for_color_bar + pickwidth * 5] = (
                picker / 255
            )

        if transposed_for_processing:
            new_img = new_img.transpose(1, 0, 2)

        return (new_img * 255).astype(int)