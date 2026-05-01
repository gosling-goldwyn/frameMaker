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
};

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
    document.getElementById("save-status").innerText = "保存時に保存先を選択します";
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

    const colors = await window.pywebview.api.getMainColorRGBValue(inputdata);
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

    const response = await window.pywebview.api.saveFrameMakerFromWebview(
        state.inputDataUrl,
        frameRatio,
        bgcolor,
        radius > 0,
        maincolor,
        radius
    );

    spinner.classList.add('hidden');
    saveButton.disabled = false;
    if (response === "cancelled") {
        saveButton.innerText = "Save";
        status.innerText = "保存をキャンセルしました";
    } else if (response) {
        saveButton.innerText = "Saved!";
        status.innerText = `保存しました: ${response}`;
    } else {
        saveButton.innerText = "Save";
        status.innerText = "保存に失敗しました";
    }
}

validateFrameRatio();
renderPreview();
