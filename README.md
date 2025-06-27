# frameMaker

`frameMaker` は、画像に装飾的なフレームを追加するためのPythonツールです。コマンドラインインターフェース (CLI) またはグラフィカルユーザーインターフェース (GUI) を介して、様々なフレームスタイルを画像に適用できます。

## 特徴

- **CLIサポート**: コマンドラインから簡単に画像処理を実行できます。
- **GUIサポート**: PyWebview を利用した直感的なGUIで操作できます。
- **フレームスタイル**:
    - 黄金比に基づいたフレーム
    - 背景色の変更 (白/黒)
    - 角丸フレーム
    - 画像の主要色を抽出して表示

## インストール

### 必要なもの

- Python 3.13 以上
- uv (Pythonパッケージインストーラ)

### 手順

1.  リポジトリをクローンします。
    ```bash
    git clone https://github.com/gosling-goldwyn/frameMaker.git
    cd frameMaker
    ```

2.  仮想環境を作成し、依存関係をインストールします。
    ```bash
    uv venv
    uv sync
    ```

3.  仮想環境をアクティベートします。
    ```bash
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

## 使用方法

### コマンドラインインターフェース (CLI)

画像を処理するには、`main.py` を使用します。

```bash
python main.py <入力ファイル名> <出力ファイル名> [オプション]
```

**オプション:**

-   `-g`, `--golden`: 黄金比に基づいたフレームを作成します。
-   `-b`, `--black`: 空白領域を黒にします (デフォルトは白)。
-   `-r`, `--rounded`: フレームの角を丸くします。
-   `-m`, `--maincolor`: 画像の主要な5色をフレーム内に表示します。

**例:**

```bash
python main.py input.jpg output.jpg -g -r
```

### グラフィカルユーザーインターフェース (GUI)

PyWebview を使用してGUIを起動できます。

```bash
python run_pywebview.py
```

GUIが起動したら、指示に従って画像を処理してください。

## 開発

### テストの実行

```bash
pytest
```

### コードフォーマットとリンティング

Ruff を使用しています。

```bash
riff check .
riff format .
```

### 型チェック

Mypy を使用しています。

```bash
mypy .
```

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細については [LICENSE](LICENSE) ファイルを参照してください。