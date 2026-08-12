// ======================================
// HTML ELEMENTS
// ======================================

const searchInput = document.getElementById("searchInput");
const documentList = document.getElementById("documentList");
const documentDetails = document.getElementById("documentDetails");

// ======================================
// GLOBAL VARIABLES
// ======================================

let documents = [];

// ======================================
// LOAD DOCUMENTS
// ======================================

async function loadDocuments() {

    documentList.innerHTML = "Loading documents...";

    try {

        documents = await getDocuments();

        renderDocuments(documents);

    } catch (error) {

    console.error(error);

    documentList.innerHTML = `

        <div style="color:red; padding:15px;">

            <p>${error.message}</p>

            <button onclick="loadDocuments()">

                Retry

            </button>

        </div>

    `;

}
}

// ======================================
// RENDER DOCUMENT LIST
// ======================================

function renderDocuments(data) {

    documentList.innerHTML = "";

    if (data.length === 0) {

        documentList.innerHTML =
            "<p>No documents found.</p>";

        return;
    }

    data.forEach(doc => {

        const item = document.createElement("div");

        item.className = "document-item";

        item.innerHTML = `
            <strong>${doc.document_name}</strong>
        `;

        item.style.cursor = "pointer";
        item.style.padding = "10px";
        item.style.marginBottom = "10px";
        item.style.border = "1px solid #ddd";
        item.style.borderRadius = "6px";

        item.onclick = () => {

            loadDocument(doc.document_id);

        };

        documentList.appendChild(item);

    });

}

// ======================================
// LOAD SINGLE DOCUMENT
// ======================================

async function loadDocument(documentId) {

    documentDetails.innerHTML = "Loading document...";

    try {

        const doc = await getDocumentContent(documentId);

        let html = `

            <h3>${doc.document_name}</h3>

            <p>
                <strong>Document ID:</strong>
                ${doc.document_id}
            </p>

            <hr>

        `;

        doc.pages.forEach(page => {

            html += `

                <div class="page-block">

                    <h4>Page ${page.page_number}</h4>

            `;

            page.sections.forEach(section => {

                html += `

                    <div class="section-block">

                        <h5>${section.header || "Untitled Section"}</h5>

                `;

                if (section.paragraphs.length === 0) {

                    html += `

                        <p><i>No paragraphs</i></p>

                    `;

                }

                section.paragraphs.forEach(paragraph => {

                    html += `

                        <p>${paragraph.text}</p>

                    `;

                });

                html += `

                    </div>

                `;

            });

            html += `

                </div>

            `;

        });

        documentDetails.innerHTML = html;

    }

    catch (error) {

    console.error(error);

    documentDetails.innerHTML = `

        <div style="color:red; padding:15px;">

            <p>${error.message}</p>

            <button onclick="loadDocument(${documentId})">

                Retry

            </button>

        </div>

    `;

}

}

// ======================================
// SEARCH
// ======================================

searchInput.addEventListener("input", () => {

    const keyword = searchInput.value
        .trim()
        .toLowerCase();

    const filtered = documents.filter(doc =>

        doc.document_name
            .toLowerCase()
            .includes(keyword)

    );

    renderDocuments(filtered);

});

// ======================================
// INITIAL LOAD
// ======================================

console.log("documents.js loaded");

window.onload = () => {

    console.log("window loaded");

    loadDocuments();

};