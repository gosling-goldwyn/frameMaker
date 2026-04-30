import base64
import io
import os

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from src.constants import MAX_FRAME_RATIO, MIN_FRAME_RATIO
from src.WebviewInterface import API

# 環境変数をロード
load_dotenv(dotenv_path="./.env")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# APIインスタンスを作成
api = API()

# Streamlitアプリの設定
st.set_page_config(
    page_title="Frame Maker",
    layout="wide",
    initial_sidebar_state="expanded",
)

# タイトルを表示
st.title("Frame Maker")

# ファイルアップロード
uploaded_file = st.sidebar.file_uploader(
    "画像をアップロードしてください", type=["jpg", "jpeg", "png"]
)


# サイドバーでオプションを選択
st.sidebar.header("オプション設定")
frame_ratio = st.sidebar.slider(
    "Frame Ratio",
    min_value=MIN_FRAME_RATIO,
    max_value=MAX_FRAME_RATIO,
    value=MIN_FRAME_RATIO,
    step=0.001,
    format="%.3f",
    help="等倍 1.000 / 4:3 1.333 / 白銀比 1.414 / 3:2 1.500 / 黄金比 1.618 / √3 1.732",
)
st.sidebar.caption(
    "指標: 等倍 1.000, 4:3 1.333, 白銀比 1.414, 3:2 1.500, "
    "黄金比 1.618, √3 1.732"
)
radius = st.sidebar.slider(
    "Radius", min_value=0, value=0, max_value=200, help="画像の角を丸くします"
)
maincolor = st.sidebar.checkbox("MainColor", help="画像の最下部に特徴色をつけます")

# 背景色の選択肢
st.sidebar.subheader("背景色")
bgcolor_options = {"White": "#FFFFFF", "Black": "#000000"}

if uploaded_file:
    img = Image.open(uploaded_file)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    img_data_url = f"data:image/jpeg;base64,{img_base64}"
    main_colors = api.getMainColorRGBValue(img_data_url)
    for _, color in enumerate(main_colors):
        bgcolor_options[f"#{color}"] = f"#{color}"

selected_bgcolor_name = st.sidebar.radio("背景色を選択", list(bgcolor_options.keys()))
bgcolor_to_pass = bgcolor_options[selected_bgcolor_name]

col = st.columns(2)
if uploaded_file:
    # アップロードされた画像を表示
    col[0].image(
        uploaded_file,
        caption="アップロードされた画像",
        use_container_width=True,
    )

    # 画像をBase64形式に変換
    img = Image.open(uploaded_file)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    img_data_url = f"data:image/jpeg;base64,{img_base64}"

    # 実行ボタン
    if col[0].button("Run"):
        with st.spinner("処理中..."):
            # APIを呼び出して画像を処理
            result_data_url = api.runFrameMakerFromWebview(
                img_data_url,
                frame_ratio,
                bgcolor_to_pass,
                True if radius > 0 else False,
                maincolor,
                radius,
            )
            if result_data_url:
                # 処理結果を表示
                col[1].image(
                    result_data_url, caption="処理後の画像", use_container_width=True
                )
                col[1].success("処理が完了しました！")
            else:
                col[1].error("エラーが発生しました。")

    # 保存ボタン
    if col[0].button("Save"):
        with col[0].spinner("保存中..."):
            api.saveImage(img_data_url)
            col[0].success("画像が保存されました！")

# デバッグモードの表示
if DEBUG:
    st.sidebar.warning("デバッグモードが有効です")
