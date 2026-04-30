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
};

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
    return {
        frameRatio: Number(document.getElementById("frame-ratio").value),
        bgcolor: document.querySelector('input[name="bgcolor"]:checked').value,
        rounded: document.getElementById("rounded").checked,
        maincolor: document.getElementById("maincolor").checked,
    };
}

function renderPreview() {
    const { frameRatio, bgcolor, rounded, maincolor } = getCurrentOptions();
    const previewFrame = document.getElementById("preview-frame");
    const previewImage = document.getElementById("preview-image");
    const colorBar = document.getElementById("maincolor-preview");
    const saveButton = document.getElementById("saveButton");

    previewFrame.style.setProperty("--frame-bg", bgcolor);
    previewFrame.style.setProperty("--frame-ratio", frameRatio);
    previewFrame.style.setProperty("--image-size", `${100 / frameRatio}%`);
    previewFrame.style.setProperty("--image-radius", rounded ? "8%" : "0px");

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
    document.getElementById("save-status").innerText = "※画像はユーザーのダウンロードフォルダに保存されます";
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

["rounded", "maincolor"].forEach((id) => {
    document.getElementById(id).addEventListener("change", renderPreview);
});
document.getElementById("color-options").addEventListener("change", renderPreview);

async function saveImage() {
    if (!state.inputDataUrl) return;

    const saveButton = document.getElementById('saveButton');
    const spinner = document.getElementById('spinner');
    const status = document.getElementById("save-status");
    const { frameRatio, bgcolor, rounded, maincolor } = getCurrentOptions();

    saveButton.disabled = true;
    saveButton.innerText = "Saving...";
    spinner.classList.remove('hidden');

    const response = await window.pywebview.api.saveFrameMakerFromWebview(
        state.inputDataUrl,
        frameRatio,
        bgcolor,
        rounded,
        maincolor
    );

    spinner.classList.add('hidden');
    saveButton.disabled = false;
    if (response) {
        saveButton.innerText = "Saved!";
        status.innerText = `保存しました: ${response}`;
    } else {
        saveButton.innerText = "Save";
        status.innerText = "保存に失敗しました";
    }
}

validateFrameRatio();
renderPreview();
