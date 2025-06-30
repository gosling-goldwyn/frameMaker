# Test Specification for IH

## IH-001: Read Image From Path

**テスト関数名:** `test_read_image_from_path`

**概要:**
指定されたファイルパスから画像を正しく読み込めることを確認する。

テスト対象機能: ImageHandlerの画像読み込み機能
期待結果: ImageHandlerオブジェクトのimg属性がNoneではなく、numpy.ndarray型であること。

**前提条件:**
- `image_handler` フィクスチャが提供するテストデータ/環境

**テスト手順:**
1. `test_read_image_from_path` 関数を実行する。

**期待結果:** (assert文が見つかりませんでした)

---

## IH-002: Read Image From Path Not Found

**テスト関数名:** `test_read_image_from_path_not_found`

**概要:**
存在しないファイルパスを指定した場合にReadErrorが送出されることを確認する。

テスト対象機能: ImageHandlerの画像読み込み時のエラーハンドリング
期待結果: ReadErrorが送出されること。

**テスト手順:**
1. `test_read_image_from_path_not_found` 関数を実行する。

**期待結果:** (assert文が見つかりませんでした)

---

