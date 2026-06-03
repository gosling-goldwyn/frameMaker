import re
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, expect

TEST_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "test_image.png"
RATIOS = ("1.000", "1.333", "1.414", "1.618", "1.732")
DESKTOP_SAVE_STATUS = "保存時に保存先を選択します"
MOBILE_SAVE_STATUS = (
    "カメラロールに保存するには、Save後に画像を開いて長押しし、保存を選択してください。"
    "OSダイアログの保存はファイルに保存されます。"
)


def upload_test_image(page: Page) -> None:
    page.get_by_test_id("input-file").set_input_files(str(TEST_IMAGE))
    expect(page.get_by_test_id("save-button")).to_be_enabled(timeout=15_000)
    expect(page.get_by_test_id("preview-image")).to_have_attribute("src", re.compile(r"^blob:"))


@pytest.mark.web
def test_save_status_defaults_to_desktop_copy(page: Page) -> None:
    expect(page.get_by_test_id("save-status")).to_have_text(DESKTOP_SAVE_STATUS)


@pytest.mark.web
def test_save_status_uses_mobile_copy_for_mobile_user_agent(
    browser: Browser,
    static_server_url: str,
) -> None:
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
            "Mobile/15E148 Safari/604.1"
        ),
        viewport={"width": 390, "height": 844},
    )
    page = context.new_page()
    try:
        page.goto(static_server_url + "/index.html")
        expect(page.get_by_test_id("save-status")).to_have_text(MOBILE_SAVE_STATUS)
    finally:
        context.close()


def output_canvas_info(page: Page) -> dict:
    return page.evaluate(
        """async () => {
            const canvas = await window.frameMakerWeb.createOutputCanvas();
            const ctx = canvas.getContext("2d");
            const topLeft = Array.from(ctx.getImageData(0, 0, 1, 1).data);
            const bottomCenter = Array.from(
                ctx.getImageData(Math.floor(canvas.width / 2), canvas.height - 1, 1, 1).data
            );
            const blob = await window.frameMakerWeb.canvasToBlob(canvas);
            return {
                width: canvas.width,
                height: canvas.height,
                topLeft,
                bottomCenter,
                blobType: blob.type,
                blobSize: blob.size,
            };
        }"""
    )


@pytest.mark.web
def test_smoke_app_is_visible_without_pywebview(page: Page) -> None:
    assert page.evaluate("() => window.pywebview") is None

    expect(page.get_by_test_id("app-title")).to_have_text("Frame Maker")
    expect(page.get_by_test_id("input-file")).to_be_visible()
    expect(page.get_by_test_id("preview-frame")).to_be_visible()
    expect(page.get_by_test_id("save-button")).to_be_visible()
    expect(page.get_by_test_id("save-button")).to_be_disabled()


@pytest.mark.web
def test_upload_updates_preview_and_enables_save(page: Page) -> None:
    preview_image = page.get_by_test_id("preview-image")
    default_src = preview_image.get_attribute("src")

    upload_test_image(page)

    assert preview_image.get_attribute("src") != default_src


@pytest.mark.web
@pytest.mark.parametrize("ratio", RATIOS)
def test_frame_ratio_presets_update_preview_and_output_canvas(page: Page, ratio: str) -> None:
    upload_test_image(page)

    page.get_by_test_id(f"ratio-preset-{ratio.replace('.', '-')}").click()
    expect(page.get_by_test_id("frame-ratio-value")).to_have_text(ratio)

    natural_size = page.evaluate(
        """() => {
            const image = document.getElementById("preview-image");
            return { width: image.naturalWidth, height: image.naturalHeight };
        }"""
    )
    expected_side = max(
        int(max(natural_size["width"], natural_size["height"]) * float(ratio)),
        natural_size["width"],
        natural_size["height"],
    )
    canvas = output_canvas_info(page)

    assert canvas["width"] == expected_side
    assert canvas["height"] == expected_side


@pytest.mark.web
def test_background_and_radius_are_reflected_in_canvas_pixels(page: Page) -> None:
    upload_test_image(page)

    page.get_by_test_id("ratio-preset-1-333").click()
    page.get_by_test_id("bg-black").check()
    black_canvas = output_canvas_info(page)
    assert black_canvas["topLeft"][:3] == [0, 0, 0]

    page.get_by_test_id("bg-white").check()
    page.get_by_test_id("corner-radius-slider").fill("80")
    expect(page.get_by_test_id("corner-radius-value")).to_have_text("80 px")
    white_canvas = output_canvas_info(page)
    assert white_canvas["topLeft"][:3] == [255, 255, 255]

    page.get_by_test_id("bg-maincolor-0").check()
    main_color_canvas = output_canvas_info(page)
    assert main_color_canvas["topLeft"][:3] != [255, 255, 255]


@pytest.mark.web
def test_maincolor_generates_swatches_and_draws_color_bar(page: Page) -> None:
    upload_test_image(page)

    expect(page.locator(".dynamic-color input")).to_have_count(5)
    page.get_by_test_id("maincolor-toggle").check()
    expect(page.get_by_test_id("maincolor-preview")).to_have_class(re.compile("active"))
    expect(page.get_by_test_id("maincolor-preview").locator("div")).to_have_count(5)

    canvas = output_canvas_info(page)
    assert canvas["bottomCenter"][:3] != [255, 255, 255]


@pytest.mark.web
def test_save_downloads_non_empty_png(page: Page) -> None:
    upload_test_image(page)

    blob_info = output_canvas_info(page)
    assert blob_info["blobType"] == "image/png"
    assert blob_info["blobSize"] > 0

    with page.expect_download() as download_info:
        page.get_by_test_id("save-button").click()

    download = download_info.value
    assert download.suggested_filename.endswith("-framed.png")
    assert download.path().stat().st_size > 0


@pytest.mark.web
def test_mobile_layout_keeps_preview_usable_and_save_clickable(page: Page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    upload_test_image(page)

    preview_box = page.get_by_test_id("preview-frame").bounding_box()
    assert preview_box is not None
    assert preview_box["width"] >= 320

    page.get_by_test_id("save-button").scroll_into_view_if_needed()
    save_box = page.get_by_test_id("save-button").bounding_box()
    footer_box = page.locator("footer").bounding_box()
    assert save_box is not None
    assert footer_box is not None
    assert save_box["y"] + save_box["height"] <= footer_box["y"]

    save_center = {
        "x": save_box["x"] + save_box["width"] / 2,
        "y": save_box["y"] + save_box["height"] / 2,
    }
    assert page.evaluate(
        """({ x, y }) => {
            const element = document.elementFromPoint(x, y);
            return Boolean(element && element.closest("#saveButton"));
        }""",
        save_center,
    )

    with page.expect_download() as download_info:
        page.get_by_test_id("save-button").click()

    download = download_info.value
    assert download.suggested_filename.endswith("-framed.png")
    assert download.path().stat().st_size > 0
