async function toBase64DataUri(file) {
    let reader = new FileReader()
    reader.readAsDataURL(file)
    await new Promise(resolve => reader.onload = () => resolve())
    return reader.result
}

async function callPythonFunction() {
    const saveButton = document.getElementById('saveButton');
    saveButton.disabled = true;
    const spinner = document.getElementById('spinner');
    const output_image = document.getElementById('output-image');
    spinner.classList.remove('hidden');
    output_image.classList.add('hidden');

    const input = document.getElementById("inputpath").files[0];
    inputdata = await toBase64DataUri(input);
    const golden = document.getElementById("golden").checked;
    const bgcolor = document.querySelector('input[name="bgcolor"]:checked').value;
    const rounded = document.getElementById("rounded").checked;
    const maincolor = document.getElementById("maincolor").checked;

    await window.pywebview.api.runFrameMakerFromWebview(inputdata, golden, bgcolor, rounded, maincolor).then((response) => {
        output_image.src = response;
        output_image.classList.remove('hidden');
    });

    spinner.classList.add('hidden');
    saveButton.disabled = false;
    saveButton.innerText = "Save";

}

document.getElementById('inputpath').addEventListener('change', async (event) => {
    const input = event.target.files[0];
    if (!input) return;

    const inputdata = await toBase64DataUri(input);
    const colors = await window.pywebview.api.getMainColorRGBValue(inputdata);

    const colorOptions = document.getElementById('color-options');
    // Remove existing color options except for black and white
    const existingOptions = colorOptions.querySelectorAll('.dynamic-color');
    existingOptions.forEach(option => option.remove());

    colors.forEach((color, index) => {
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
});

async function saveImage() {
    const output_image = document.getElementById('output-image');
    const saveButton = document.getElementById('saveButton');
    await window.pywebview.api.saveImage(output_image.src)
    console.log("Image saved");
    saveButton.innerText = "Saved!";
}