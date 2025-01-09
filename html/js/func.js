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
    const black = document.getElementById("black").checked;
    const rounded = document.getElementById("rounded").checked;
    const maincolor = document.getElementById("maincolor").checked;

    await window.pywebview.api.runFrameMakerFromWebview(inputdata, golden, black, rounded, maincolor).then((response) => {
        output_image.src = response;
        output_image.classList.remove('hidden');
    });

    spinner.classList.add('hidden');
    saveButton.disabled = false;
    saveButton.innerText = "Save";

}

async function saveImage() {
    const output_image = document.getElementById('output-image');
    const saveButton = document.getElementById('saveButton');
    await window.pywebview.api.saveImage(output_image.src)
    console.log("Image saved");
    saveButton.innerText = "Saved!";
}