# Test Specification for FM

## FM-001: Frame Maker Golden Ratio White Frame

**テスト関数名:** `test_frame_maker_golden_ratio_white_frame`

**概要:**
縦長の画像に対して、黄金比に基づいた白いフレームが正しく適用されることを確認する。

テスト対象機能: FrameMakerのgolden=True, black=Falseオプション
期待結果: 出力画像の縦横サイズが期待される黄金比に基づいたサイズであり、フレーム部分が白であること。

**前提条件:**
- `sample_image_handler_tall` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_frame_maker_golden_ratio_white_frame` 関数を実行する。

**期待結果:**
- `assert result_img.shape[0] == expected_side_length` が真であること。
- `assert result_img.shape[1] == expected_side_length` が真であること。
- `assert np.all(result_img[0, 0] == 255)` が真であること。
- `assert np.all(result_img[-1, -1] == 255)` が真であること。

---

## FM-002: Frame Maker Golden Ratio Black Frame

**テスト関数名:** `test_frame_maker_golden_ratio_black_frame`

**概要:**
横長の画像に対して、黄金比に基づいた黒いフレームが正しく適用されることを確認する。

テスト対象機能: FrameMakerのgolden=True, black=Trueオプション
期待結果: 出力画像の縦横サイズが期待される黄金比に基づいたサイズであり、フレーム部分が黒であること。

**前提条件:**
- `sample_image_handler_wide` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_frame_maker_golden_ratio_black_frame` 関数を実行する。

**期待結果:**
- `assert result_img.shape[0] == expected_side_length` が真であること。
- `assert result_img.shape[1] == expected_side_length` が真であること。
- `assert np.all(result_img[0, 0] == 0)` が真であること。
- `assert np.all(result_img[-1, -1] == 0)` が真であること。

---

## FM-003: Frame Maker No Golden Ratio White Frame

**テスト関数名:** `test_frame_maker_no_golden_ratio_white_frame`

**概要:**
正方形の画像に対して、黄金比を適用しない白いフレームが正しく適用されることを確認する。

テスト対象機能: FrameMakerのgolden=False, black=Falseオプション
期待結果: 出力画像の縦横サイズが元の画像の最大辺の長さであり、フレーム部分が白であること。

**前提条件:**
- `sample_image_handler` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_frame_maker_no_golden_ratio_white_frame` 関数を実行する。

**期待結果:**
- `assert result_img.shape[0] == expected_side_length` が真であること。
- `assert result_img.shape[1] == expected_side_length` が真であること。
- `assert np.all(result_img[0, 0] == 255)` が真であること。

---

## FM-004: Frame Maker No Golden Ratio Black Frame

**テスト関数名:** `test_frame_maker_no_golden_ratio_black_frame`

**概要:**
縦長の画像に対して、黄金比を適用しない黒いフレームが正しく適用されることを確認する。

テスト対象機能: FrameMakerのgolden=False, black=Trueオプション
期待結果: 出力画像の縦横サイズが元の画像の最大辺の長さであり、フレーム部分が黒であること。

**前提条件:**
- `sample_image_handler_tall` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_frame_maker_no_golden_ratio_black_frame` 関数を実行する。

**期待結果:**
- `assert result_img.shape[0] == expected_side_length` が真であること。
- `assert result_img.shape[1] == expected_side_length` が真であること。
- `assert np.all(result_img[0, 0] == 0)` が真であること。

---

## FM-005: Frame Maker Rounded White Frame

**テスト関数名:** `test_frame_maker_rounded_white_frame`

**概要:**
正方形の画像に対して、角丸の白いフレームが正しく適用されることを確認する。

テスト対象機能: FrameMakerのrounded=True, black=Falseオプション
期待結果: 出力画像のフレーム部分が白であり、角が丸められていること。

**前提条件:**
- `sample_image_handler` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_frame_maker_rounded_white_frame` 関数を実行する。

**期待結果:**
- `assert np.all(result_img[0, 0] == 255)` が真であること。

---

## FM-006: Frame Maker Rounded Black Frame

**テスト関数名:** `test_frame_maker_rounded_black_frame`

**概要:**
正方形の画像に対して、角丸の黒いフレームが正しく適用されることを確認する。

テスト対象機能: FrameMakerのrounded=True, black=Trueオプション
期待結果: 出力画像のフレーム部分が黒であり、角が丸められていること。

**前提条件:**
- `sample_image_handler` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_frame_maker_rounded_black_frame` 関数を実行する。

**期待結果:**
- `assert np.all(result_img[0, 0] == 0)` が真であること。

---

## FM-007: Frame Maker Main Color Bar

**テスト関数名:** `test_frame_maker_main_color_bar`

**概要:**
カラー画像に対して、メインカラーバーが正しく適用されることを確認する。

テスト対象機能: FrameMakerのmc=Trueオプション
期待結果: 出力画像にカラーバーが追加され、その領域が完全に白ではないこと。

**前提条件:**
- `sample_image_handler_colored` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_frame_maker_main_color_bar` 関数を実行する。

**期待結果:**
- `assert not np.all(color_bar_area == 255)` が真であること。

---

## FM-008: Frame Maker Rounded And Main Color Bar

**テスト関数名:** `test_frame_maker_rounded_and_main_color_bar`

**概要:**
カラー画像に対して、角丸とメインカラーバーが組み合わせて正しく適用されることを確認する。

テスト対象機能: FrameMakerのrounded=True, mc=Trueオプション
期待結果: 出力画像の角が丸められ、カラーバーが追加され、その領域が完全に白ではないこと。

**前提条件:**
- `sample_image_handler_colored` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_frame_maker_rounded_and_main_color_bar` 関数を実行する。

**期待結果:**
- `assert np.all(result_img[0, 0] == 255)` が真であること。
- `assert not np.all(color_bar_area == 255)` が真であること。

---

