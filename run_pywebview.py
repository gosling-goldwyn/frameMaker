import logging
import os

import webview
from dotenv import load_dotenv

from src.WebviewInterface import API

load_dotenv(dotenv_path="./.env")
logging.getLogger("webview.http").setLevel(logging.ERROR)

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

api = API()
window = webview.create_window(
    "Frame Maker",
    "./html/index.html",
    width=1080,
    height=720,
    js_api=api,
    min_size=(600, 550),
)
api.set_window(window)
webview.start(http_server=True, debug=DEBUG)
