import argparse

from src.constants import MAX_FRAME_RATIO, MIN_FRAME_RATIO
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
        "-s",
        "--silver",
        action="store_true",
        default=False,
        help="make blank spots the silver ratio in landscape or portrait image",
    )
    PARSER.add_argument(
        "--ratio",
        type=float,
        default=None,
        help="set a custom frame ratio from 1.0 to 1.732",
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
    ratio_options = [ARGS.golden, ARGS.silver, ARGS.ratio is not None]
    if sum(bool(option) for option in ratio_options) > 1:
        PARSER.error("--golden, --silver, and --ratio cannot be used together")
    if ARGS.ratio is not None and not MIN_FRAME_RATIO <= ARGS.ratio <= MAX_FRAME_RATIO:
        PARSER.error(f"--ratio must be between {MIN_FRAME_RATIO} and {MAX_FRAME_RATIO}")

    frame_mode = (
        ARGS.ratio
        if ARGS.ratio is not None
        else "silver"
        if ARGS.silver
        else "golden"
        if ARGS.golden
        else "none"
    )
    API().runFrameMaker(
        ARGS.input, ARGS.output, frame_mode, ARGS.black, ARGS.rounded, ARGS.maincolor
    )
