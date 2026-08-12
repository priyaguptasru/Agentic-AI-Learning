// ======================================
// BACKEND URL
// ======================================

const BASE_URL = "http://127.0.0.1:8000";


// ======================================
// PDF Upload API
// ======================================

async function uploadPdf(file) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
        `${BASE_URL}/ingest/pdf`,
        {
            method: "POST",
            body: formData
        }
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.message || data.detail
        );

    }

    return data;
}


// ======================================
// CSV Upload API
// ======================================

async function uploadCsv(file) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
        `${BASE_URL}/ingest/csv`,
        {
            method: "POST",
            body: formData
        }
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.message || data.detail
        );

    }

    return data;
}


// ======================================
// GET ALL DOCUMENTS
// ======================================

async function getDocuments() {

    const response = await fetch(
        `${BASE_URL}/documents/`
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.message || data.detail
        );

    }

    return data;
}


// ======================================
// GET DOCUMENT DETAILS
// ======================================

async function getDocument(documentId) {

    const response = await fetch(
        `${BASE_URL}/documents/${documentId}`
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.message || data.detail
        );

    }

    return data;

}


// ======================================
// GET DOCUMENT CONTENT
// ======================================

async function getDocumentContent(documentId) {

    const response = await fetch(
        `${BASE_URL}/documents/${documentId}/content`
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.message || data.detail
        );

    }

    return data;
}


// ======================================
// GET ALL CSV FILES
// ======================================

async function getCsvFiles() {

    const response = await fetch(
        `${BASE_URL}/csv/files`
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.message || data.detail
        );

    }

    return data;

}


// ======================================
// GET SINGLE CSV FILE
// ======================================

async function getCsvFile(fileId) {

    const response = await fetch(
        `${BASE_URL}/csv/files/${fileId}`
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.message || data.detail
        );

    }

    return data;

}


// ======================================
// GET CSV RECORDS
// ======================================

async function getCsvRecords(fileId) {

    const response = await fetch(
        `${BASE_URL}/csv/files/${fileId}/records`
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.message || data.detail
        );

    }

    return data;

}