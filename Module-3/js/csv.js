// ======================================
// HTML ELEMENTS
// ======================================

const searchInput = document.getElementById("searchInput");
const csvList = document.getElementById("csvList");
const csvDetails = document.getElementById("csvDetails");

// ======================================
// GLOBAL VARIABLES
// ======================================

let csvFiles = [];

// ======================================
// LOAD ALL CSV FILES
// ======================================

async function loadCsvFiles() {

    csvList.innerHTML = "Loading CSV files...";

    try {

        csvFiles = await getCsvFiles();

        renderCsvFiles(csvFiles);

    } catch (error) {

    console.error(error);

    csvList.innerHTML = `
        <div style="color:red; padding:15px;">

            <p>${error.message}</p>

            <button onclick="loadCsvFiles()">

                Retry

            </button>

        </div>
    `;

}

}

// ======================================
// RENDER CSV LIST
// ======================================

function renderCsvFiles(files) {

    csvList.innerHTML = "";

    if (files.length === 0) {

        csvList.innerHTML = "<p>No CSV files found.</p>";

        return;

    }

    files.forEach(file => {

        const item = document.createElement("div");

        item.className = "csv-item";

        item.innerHTML = `
            <strong>${file.file_name}</strong><br>
            Rows : ${file.total_rows}
        `;

        item.onclick = () => {

            loadCsv(file.file_id);

        };

        csvList.appendChild(item);

    });

}

// ======================================
// LOAD SINGLE CSV
// ======================================

async function loadCsv(fileId) {

    csvDetails.innerHTML = "Loading...";

    try {

        const info = await getCsvFile(fileId);

        const data = await getCsvRecords(fileId);

        let html = `
            <h3>${info.file_name}</h3>

            <p><strong>File ID:</strong> ${info.file_id}</p>

            <p><strong>Total Rows:</strong> ${info.total_rows}</p>
        `;

        if (!data.records || data.records.length === 0) {

            html += "<p>No records available.</p>";

            csvDetails.innerHTML = html;

            return;

        }

        const headers = Object.keys(data.records[0].record_data);

        html += "<table class='csv-table'>";

        html += "<tr>";

        headers.forEach(header => {

            html += `<th>${header}</th>`;

        });

        html += "</tr>";

        data.records.slice(0,20).forEach(record => {

            html += "<tr>";

            headers.forEach(header => {

                html += `<td>${record.record_data[header]}</td>`;

            });

            html += "</tr>";

        });

        html += "</table>";

        if (data.records.length > 20) {

            html += `
                <p style="margin-top:15px;">
                    Showing first 20 of ${data.records.length} rows.
                </p>
            `;

        }

        csvDetails.innerHTML = html;

    }

    catch (error) {

    console.error(error);

    csvDetails.innerHTML = `
        <div style="color:red; padding:15px;">

            <p>${error.message}</p>

            <button onclick="loadCsv(${fileId})">

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

    const filtered = csvFiles.filter(file =>

        file.file_name
            .toLowerCase()
            .includes(keyword)

    );

    renderCsvFiles(filtered);

});

// ======================================
// INITIAL LOAD
// ======================================

window.onload = () => {

    loadCsvFiles();

};