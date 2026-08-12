// ======================================
// HTML ELEMENTS
// ======================================

const pdfInput = document.getElementById("pdfFile");
const csvInput = document.getElementById("csvFile");

const uploadPdfBtn = document.getElementById("uploadPdfBtn");
const uploadCsvBtn = document.getElementById("uploadCsvBtn");

const statusMessage = document.getElementById("statusMessage");

// ======================================
// RESET STATUS
// ======================================

function resetStatus() {

    setTimeout(() => {

        statusMessage.style.color = "green";
        statusMessage.textContent = "Ready...";

    }, 5000);

}

// ======================================
// PDF UPLOAD
// ======================================

uploadPdfBtn.addEventListener("click", async () => {

    if (!pdfInput.files.length) {

        statusMessage.style.color = "red";
        statusMessage.textContent = "Please select a PDF file.";

        resetStatus();

        return;

    }

    uploadPdfBtn.disabled = true;
    uploadPdfBtn.textContent = "Uploading...";

    statusMessage.style.color = "blue";
    statusMessage.textContent = "Uploading PDF...";

    try {

        const result = await uploadPdf(pdfInput.files[0]);

        console.log("PDF Upload Success:", result);

        // Clear selected file only after successful upload
        pdfInput.value = "";

        statusMessage.style.color = "green";
        statusMessage.textContent = result.message;

        resetStatus();

    }

    catch (error) {

        console.error(error);

        statusMessage.style.color = "red";
        statusMessage.textContent = error.message;

        resetStatus();

    }

    finally {

        uploadPdfBtn.disabled = false;
        uploadPdfBtn.textContent = "Upload PDF";

    }

});


// ======================================
// CSV UPLOAD
// ======================================

uploadCsvBtn.addEventListener("click", async () => {

    if (!csvInput.files.length) {

        statusMessage.style.color = "red";
        statusMessage.textContent = "Please select a CSV file.";

        resetStatus();

        return;

    }

    uploadCsvBtn.disabled = true;
    uploadCsvBtn.textContent = "Uploading...";

    statusMessage.style.color = "blue";
    statusMessage.textContent = "Uploading CSV...";

    try {

        const result = await uploadCsv(csvInput.files[0]);

        console.log("CSV Upload Success:", result);

        // Clear selected file only after successful upload
        csvInput.value = "";

        statusMessage.style.color = "green";
        statusMessage.textContent = result.message;

        resetStatus();

    }

    catch (error) {

        console.error(error);

        statusMessage.style.color = "red";
        statusMessage.textContent = error.message;

        resetStatus();

    }

    finally {

        uploadCsvBtn.disabled = false;
        uploadCsvBtn.textContent = "Upload CSV";

    }

});