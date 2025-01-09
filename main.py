import argparse
import numpy
import cv2
from numpy.core.fromnumeric import transpose
from colorpick import getMainColor

class ReadError(Exception):
    pass

class FrameMaker():
    def __init__(self, fp, golden, black):
        img = cv2.imread(fp, cv2.IMREAD_COLOR)

        # 読み込みに失敗すると例外
        if img is None:
            raise ReadError()

        self.img = img/255

        self.height, self.width, self.color = img.shape

        self.golden = golden
        self.black = black
        self.transpose = False
        self.isSquare = self.height == self.width
        self.fp = fp

    def run(self):

        # 縦長なら転置して横長にする
        if self.height > self.width:
            self.img = self.img.transpose(1, 0, 2)
            self.height, self.width, self.color = self.img.shape
            self.transpose = True

        # 新しい画像の辺の長さを計算(黄金比1.618に基づく)
        if self.height < self.width:
            if self.golden:
                new_width = int(self.height * 1.618)
            else:
                new_width = int(self.width)
        else:
            new_width = int(self.height * 1.618)

        # 白枠をつけるか黒枠をつけるか
        new_img = numpy.zeros([new_width, new_width, self.color], dtype="float64") \
            if self.black else numpy.ones([new_width, new_width, self.color], dtype="float64")

        # 画像を枠の中に配置する起点の計算
        if self.isSquare:
            sh = int(self.height*0.309)
            sw = int(self.width*0.309)
        elif self.golden:
            sh = int(self.height*0.309)
            sw = int((1.618*self.height-self.width)//2)
        else:
            sh = (self.width - self.height) // 2
            sw = 0

        new_img[sh:sh+self.height, sw:sw+self.width] = self.img

        if self.golden:
            pickWidth = int(self.width // 5)
            pickHeight = int((self.height*0.309)//5)
            picker = getMainColor(self.fp,pickWidth,pickHeight)
            new_img[new_width-pickHeight:new_width, sw:sw+pickWidth*5] = picker/255

        if self.transpose:
            new_img = new_img.transpose(1, 0, 2)

        return (new_img * 255).astype(numpy.int)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("input", help='input file name')
    PARSER.add_argument(
        "output", help='output file name (existed file is overriden)')
    PARSER.add_argument("-g", "--golden", action='store_true', default=False,
                        help='make blank spots the golden ratio in landscape or portrait image')
    PARSER.add_argument("-b", "--black", action='store_true',
                        default=False, help='turn the blank area from white to black')
    ARGS = PARSER.parse_args()
    try:
        FM = FrameMaker(ARGS.input, ARGS.golden, ARGS.black)
        RESULT = FM.run()
    except ReadError:
        print('Read Error: File doesn\'t exist (unsupported japanese characters)')
    else:
        cv2.imwrite(ARGS.output, RESULT, [cv2.IMWRITE_JPEG_QUALITY, 100])
