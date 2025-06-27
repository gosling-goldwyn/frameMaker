import base64
import io
import os

import cv2
import numpy as np
from PIL import Image

from src.Error import ReadError
from src.FrameMaker import FrameMaker
from src.ImageHandler import ImageHandler


def pillow_image_to_base64_string(img: Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def base64_string_to_pillow_image(base64_str):
    return Image.open(
        io.BytesIO(base64.decodebytes(bytes(base64_str.split(",")[1], "utf-8")))
    )


def get_save_path(base_filename, directory="."):
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
    def runFrameMaker(
        self,
        inputpath: str,
        outputpath: str,
        golden: bool,
        black: bool,
        rounded: bool,
        maincolor: bool,
    ) -> None:
        try:
            handler = ImageHandler(fp=inputpath.replace("blob:", ""))
            fm = FrameMaker(
                handler, golden, black, rounded, maincolor, golden_ratio=1.618, side_margin_ratio=0.309
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
        black: bool,
        rounded: bool,
        maincolor: bool,
        radius: int = 40,
    ) -> str:
        try:
            webimg = base64_string_to_pillow_image(inputdata)
            handler = ImageHandler(fp="", webimg=webimg)
            fm = FrameMaker(
                handler, golden, black, rounded, maincolor, radius=radius, golden_ratio=1.618, side_margin_ratio=0.309
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
        webimg = base64_string_to_pillow_image(inputdata)
        handler = ImageHandler(fp="", webimg=webimg)
        base_dir = os.getenv(
            "USERPROFILE",
            "NOT_DEFINED",
        )
        save_path = get_save_path("output.jpg", f"{base_dir}\\Downloads")
        print(webimg)
        print(save_path)
        handler.save_image(save_path, np.array(webimg))

    def getMainColorRGBValue(
        self,
        inputdata: str,
        golden: bool,
        black: bool,
        rounded: bool,
        maincolor: bool,
        radius: int = 40,
    ) -> list[str]:
        try:
            webimg = base64_string_to_pillow_image(inputdata)
            handler = ImageHandler(fp="", webimg=webimg)
            fm = FrameMaker(
                handler, golden, black, rounded, maincolor, radius=radius, golden_ratio=1.618, side_margin_ratio=0.309
            )
            result = fm.runGetMainColorRGBValue()
            return result
        except ReadError:
            print("Read Error: File doesn't exist (unsupported japanese characters)")
            return []