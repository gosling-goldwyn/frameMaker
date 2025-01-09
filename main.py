import argparse

from src.WebviewInterface import API

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("input", help="input file name")
    PARSER.add_argument("output", help="output file name (existed file is overriden)")
    PARSER.add_argument(
        "-g",
        "--golden",
        action="store_true",
        default=False,
        help="make blank spots the golden ratio in landscape or portrait image",
    )
    PARSER.add_argument(
        "-b",
        "--black",
        action="store_true",
        default=False,
        help="turn the blank area from white to black",
    )
    PARSER.add_argument(
        "-r",
        "--rounded",
        action="store_true",
        default=False,
        help="turn the rectangle's edge from sharp to rounded",
    )
    PARSER.add_argument(
        "-m",
        "--maincolor",
        action="store_true",
        default=False,
        help="put the five main color in the image",
    )
    ARGS = PARSER.parse_args()
    API.runFrameMaker(
        ARGS.input, ARGS.output, ARGS.golden, ARGS.black, ARGS.rounded, ARGS.maincolor
    )
