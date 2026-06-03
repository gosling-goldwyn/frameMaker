async function toBase64DataUri(file) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    await new Promise(resolve => reader.onload = () => resolve());
    return reader.result;
}

const state = {
    inputDataUrl: "",
    objectUrl: "",
    mainColors: [],
    imageWidth: 0,
    imageHeight: 0,
    originalFileName: "output",
};

const SIDE_MARGIN_RATIO = 0.309;
const SERVER_SAVE_NOTE = "サーバーに画像が保存されることはありません。";
const DESKTOP_SAVE_STATUS = `保存時に保存先を選択します。${SERVER_SAVE_NOTE}`;
const MOBILE_SAVE_STATUS = `カメラロールに保存するには、Save後に画像を開いて長押しし、保存を選択してください。OSダイアログの保存はファイルに保存されます。${SERVER_SAVE_NOTE}`;

function hasPywebviewApi() {
    return Boolean(window.pywebview && window.pywebview.api);
}

function isMobileSaveContext() {
    if (navigator.userAgentData && navigator.userAgentData.mobile) {
        return true;
    }

    const userAgent = navigator.userAgent || "";
    const platform = navigator.platform || "";
    return /iPhone|iPad|iPod|Android|Mobile/i.test(userAgent)
        || (platform === "MacIntel" && navigator.maxTouchPoints > 1);
}

function getInitialSaveStatus() {
    return isMobileSaveContext() ? MOBILE_SAVE_STATUS : DESKTOP_SAVE_STATUS;
}

function resetSaveStatus() {
    document.getElementById("save-status").innerText = getInitialSaveStatus();
}

async function loadImageSize(src) {
    const image = new Image();
    image.src = src;
    await new Promise((resolve, reject) => {
        image.onload = () => resolve();
        image.onerror = () => reject(new Error("Failed to load preview image"));
    });
    return {
        width: image.naturalWidth,
        height: image.naturalHeight,
    };
}

function getPreviewImageSize(frameRatio) {
    if (!state.imageWidth || !state.imageHeight) {
        return {
            width: 100 / frameRatio,
            height: 100 / frameRatio,
        };
    }

    const imageRatio = state.imageWidth / state.imageHeight;
    if (state.imageWidth >= state.imageHeight) {
        const width = 100 / frameRatio;
        return {
            width,
            height: width / imageRatio,
        };
    }

    const height = 100 / frameRatio;
    return {
        width: height * imageRatio,
        height,
    };
}

function validateFrameRatio() {
    const ratioInput = document.getElementById("frame-ratio");
    const ratioValue = document.getElementById("frame-ratio-value");
    const ratioError = document.getElementById("frame-ratio-error");
    const saveButton = document.getElementById("saveButton");
    const ratio = Number(ratioInput.value);

    ratioValue.innerText = ratio.toFixed(3);

    if (Number.isNaN(ratio) || ratio < 1.0 || ratio > 1.732) {
        ratioError.innerText = "Frame Ratio は 1.000 から 1.732 の範囲で指定してください";
        saveButton.disabled = true;
        return;
    }

    ratioError.innerText = "";
    saveButton.disabled = !state.inputDataUrl;
}

function getCurrentOptions() {
    const radius = Number(document.getElementById("corner-radius").value);
    return {
        frameRatio: Number(document.getElementById("frame-ratio").value),
        bgcolor: document.querySelector('input[name="bgcolor"]:checked').value,
        rounded: radius > 0,
        maincolor: document.getElementById("maincolor").checked,
        radius,
    };
}

function hexToRgb(hex) {
    const normalized = hex.replace("#", "");
    return {
        r: parseInt(normalized.slice(0, 2), 16),
        g: parseInt(normalized.slice(2, 4), 16),
        b: parseInt(normalized.slice(4, 6), 16),
    };
}

function rgbToHex(r, g, b) {
    return [r, g, b]
        .map((value) => value.toString(16).padStart(2, "0"))
        .join("");
}

async function loadImageElement(src) {
    const image = new Image();
    image.src = src;
    await new Promise((resolve, reject) => {
        image.onload = () => resolve();
        image.onerror = () => reject(new Error("Failed to load image"));
    });
    return image;
}

function drawRoundedImage(ctx, image, x, y, width, height, radius) {
    const safeRadius = Math.min(radius, width / 2, height / 2);
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x + safeRadius, y);
    ctx.lineTo(x + width - safeRadius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + safeRadius);
    ctx.lineTo(x + width, y + height - safeRadius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - safeRadius, y + height);
    ctx.lineTo(x + safeRadius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - safeRadius);
    ctx.lineTo(x, y + safeRadius);
    ctx.quadraticCurveTo(x, y, x + safeRadius, y);
    ctx.clip();
    ctx.drawImage(image, x, y, width, height);
    ctx.restore();
}

function extractMainColorsFromCanvas(image) {
    const sampleCanvas = document.createElement("canvas");
    const maxSampleSize = 80;
    const scale = Math.min(1, maxSampleSize / Math.max(image.naturalWidth, image.naturalHeight));
    sampleCanvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
    sampleCanvas.height = Math.max(1, Math.round(image.naturalHeight * scale));

    const sampleCtx = sampleCanvas.getContext("2d", { willReadFrequently: true });
    sampleCtx.drawImage(image, 0, 0, sampleCanvas.width, sampleCanvas.height);
    const pixels = sampleCtx.getImageData(0, 0, sampleCanvas.width, sampleCanvas.height).data;
    const buckets = new Map();

    for (let index = 0; index < pixels.length; index += 4) {
        const alpha = pixels[index + 3];
        if (alpha < 128) continue;

        const r = pixels[index];
        const g = pixels[index + 1];
        const b = pixels[index + 2];
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const saturation = max === 0 ? 0 : (max - min) / max;
        const brightness = max / 255;
        if (saturation < 0.1 || brightness < 0.1) continue;

        const key = `${Math.round(r / 32)},${Math.round(g / 32)},${Math.round(b / 32)}`;
        const bucket = buckets.get(key) || { r: 0, g: 0, b: 0, count: 0 };
        bucket.r += r;
        bucket.g += g;
        bucket.b += b;
        bucket.count += 1;
        buckets.set(key, bucket);
    }

    const colors = Array.from(buckets.values())
        .sort((a, b) => b.count - a.count)
        .slice(0, 5)
        .map((bucket) => rgbToHex(
            Math.round(bucket.r / bucket.count),
            Math.round(bucket.g / bucket.count),
            Math.round(bucket.b / bucket.count),
        ));

    while (colors.length < 5) {
        colors.push(colors[colors.length - 1] || "000000");
    }
    return colors;
}

async function getMainColors(inputDataUrl) {
    if (hasPywebviewApi() && window.pywebview.api.getMainColorRGBValue) {
        return await window.pywebview.api.getMainColorRGBValue(inputDataUrl);
    }

    const image = await loadImageElement(inputDataUrl);
    return extractMainColorsFromCanvas(image);
}

async function createOutputCanvas() {
    if (!state.inputDataUrl) {
        throw new Error("No image has been selected");
    }

    const { frameRatio, bgcolor, maincolor, radius } = getCurrentOptions();
    const image = await loadImageElement(state.inputDataUrl);
    const sourceWidth = image.naturalWidth;
    const sourceHeight = image.naturalHeight;
    const sideLength = Math.max(
        Math.floor(Math.max(sourceWidth, sourceHeight) * frameRatio),
        sourceWidth,
        sourceHeight,
    );

    const canvas = document.createElement("canvas");
    canvas.width = sideLength;
    canvas.height = sideLength;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = bgcolor;
    ctx.fillRect(0, 0, sideLength, sideLength);

    const x = Math.floor((sideLength - sourceWidth) / 2);
    const y = Math.floor((sideLength - sourceHeight) / 2);
    if (radius > 0) {
        drawRoundedImage(ctx, image, x, y, sourceWidth, sourceHeight, radius);
    } else {
        ctx.drawImage(image, x, y, sourceWidth, sourceHeight);
    }

    if (maincolor && state.mainColors.length > 0) {
        const pickWidth = Math.floor(sideLength / 5);
        const pickHeight = Math.max(1, Math.floor((sideLength * SIDE_MARGIN_RATIO) / 30));
        const startX = Math.floor((sideLength - pickWidth * 5) / 2);
        state.mainColors.slice(0, 5).forEach((color, index) => {
            ctx.fillStyle = `#${color}`;
            ctx.fillRect(
                startX + pickWidth * index,
                sideLength - pickHeight,
                pickWidth,
                pickHeight,
            );
        });
    }

    return canvas;
}

function canvasToBlob(canvas, type = "image/png") {
    return new Promise((resolve) => {
        canvas.toBlob((blob) => resolve(blob), type);
    });
}

async function downloadOutputImage() {
    const canvas = await createOutputCanvas();
    const blob = await canvasToBlob(canvas);
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    const baseName = state.originalFileName.replace(/\.[^.]+$/, "") || "output";
    link.href = url;
    link.download = `${baseName}-framed.png`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    return blob;
}

function renderPreview() {
    const { frameRatio, bgcolor, maincolor, radius } = getCurrentOptions();
    const previewFrame = document.getElementById("preview-frame");
    const previewImage = document.getElementById("preview-image");
    const colorBar = document.getElementById("maincolor-preview");
    const saveButton = document.getElementById("saveButton");
    const imageSize = getPreviewImageSize(frameRatio);

    previewFrame.style.setProperty("--frame-bg", bgcolor);
    previewFrame.style.setProperty("--frame-ratio", frameRatio);
    previewFrame.style.setProperty("--image-width", `${imageSize.width}%`);
    previewFrame.style.setProperty("--image-height", `${imageSize.height}%`);
    previewFrame.style.setProperty("--image-radius", `${radius}px`);
    document.getElementById("corner-radius-value").innerText = `${radius} px`;

    if (state.objectUrl) {
        previewImage.src = state.objectUrl;
    }

    colorBar.innerHTML = "";
    if (maincolor && state.mainColors.length > 0) {
        state.mainColors.slice(0, 5).forEach((color) => {
            const swatch = document.createElement("div");
            swatch.style.backgroundColor = `#${color}`;
            colorBar.appendChild(swatch);
        });
        colorBar.classList.add("active");
    } else {
        colorBar.classList.remove("active");
    }

    saveButton.disabled = !state.inputDataUrl;
    saveButton.innerText = "Save";
    resetSaveStatus();
}

document.getElementById("frame-ratio").addEventListener("input", validateFrameRatio);
document.getElementById("frame-ratio").addEventListener("input", renderPreview);
document.querySelectorAll("[data-ratio]").forEach((button) => {
    button.addEventListener("click", () => {
        const ratioInput = document.getElementById("frame-ratio");
        ratioInput.value = button.dataset.ratio;
        validateFrameRatio();
        renderPreview();
    });
});

document.getElementById('inputpath').addEventListener('change', async (event) => {
    const input = event.target.files[0];
    if (!input) return;

    state.originalFileName = input.name || "output";
    const inputdata = await toBase64DataUri(input);
    state.inputDataUrl = inputdata;
    if (state.objectUrl) {
        URL.revokeObjectURL(state.objectUrl);
    }
    state.objectUrl = URL.createObjectURL(input);
    const imageSize = await loadImageSize(state.objectUrl);
    state.imageWidth = imageSize.width;
    state.imageHeight = imageSize.height;
    renderPreview();

    const colors = await getMainColors(inputdata);
    state.mainColors = colors || [];

    const colorOptions = document.getElementById('color-options');
    // Remove existing color options except for black and white
    const existingOptions = colorOptions.querySelectorAll('.dynamic-color');
    existingOptions.forEach(option => option.remove());

    state.mainColors.forEach((color, index) => {
        const colorDiv = document.createElement('div');
        colorDiv.classList.add('flex', 'items-center', 'dynamic-color');

        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.id = `color-${index}`;
        radio.name = 'bgcolor';
        radio.value = `#${color}`;
        radio.classList.add('radio', 'radio-primary');
        radio.dataset.testid = `bg-maincolor-${index}`;

        const label = document.createElement('label');
        label.htmlFor = `color-${index}`;
        label.classList.add('ml-2');
        label.innerText = `#${color}`;
        label.style.color = `#${color}`;

        colorDiv.appendChild(radio);
        colorDiv.appendChild(label);
        colorOptions.appendChild(colorDiv);
    });

    renderPreview();
});

["corner-radius", "maincolor"].forEach((id) => {
    document.getElementById(id).addEventListener("change", renderPreview);
});
document.getElementById("corner-radius").addEventListener("input", renderPreview);
document.getElementById("color-options").addEventListener("change", renderPreview);

async function saveImage() {
    if (!state.inputDataUrl) return;

    const saveButton = document.getElementById('saveButton');
    const spinner = document.getElementById('spinner');
    const status = document.getElementById("save-status");
    const { frameRatio, bgcolor, maincolor, radius } = getCurrentOptions();

    saveButton.disabled = true;
    saveButton.innerText = "Saving...";
    spinner.classList.remove('hidden');

    let response = "";
    if (hasPywebviewApi() && window.pywebview.api.saveFrameMakerFromWebview) {
        response = await window.pywebview.api.saveFrameMakerFromWebview(
            state.inputDataUrl,
            frameRatio,
            bgcolor,
            radius > 0,
            maincolor,
            radius
        );
    } else {
        const blob = await downloadOutputImage();
        response = blob && blob.size > 0 ? "download" : "";
    }

    spinner.classList.add('hidden');
    saveButton.disabled = false;
    if (response === "cancelled") {
        saveButton.innerText = "Save";
        status.innerText = "保存をキャンセルしました";
    } else if (response === "download") {
        saveButton.innerText = "Saved!";
        status.innerText = "ダウンロードを開始しました";
    } else if (response) {
        saveButton.innerText = "Saved!";
        status.innerText = `保存しました: ${response}`;
    } else {
        saveButton.innerText = "Save";
        status.innerText = "保存に失敗しました";
    }
}

window.frameMakerWeb = {
    createOutputCanvas,
    canvasToBlob,
    getMainColors,
};

validateFrameRatio();
renderPreview();
