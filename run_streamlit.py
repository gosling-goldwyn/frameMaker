import os
import io
import base64
import streamlit as st
from PIL import Image
import numpy as np
from src.WebviewInterface import API
from dotenv import load_dotenv
from src.colorpick import getMainColorRGBValue

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
golden = st.sidebar.checkbox("Golden", help="上下左右の余白を黄金比にします")
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
                golden,
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
