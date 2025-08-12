let state = {
    jwtToken: "",
    currentApp: null,
    currentModel: null,
    selectedRecordIds: [],
    rows: [], // Last fetched data
    currentMode: "read",
    currentPage: 1,
    rowsPerPage: 10,
    sortColumn: null,
    sortDirection: "asc",
    filterText: ""
};

// Token setup
document.addEventListener("DOMContentLoaded", () => {
    const tokenMeta = document.querySelector('meta[name="jwt-token"]');
    if (tokenMeta) state.jwtToken = tokenMeta.getAttribute('content');
    initCrudControls();
});

// CRUD control setup
function initCrudControls() {
    document.querySelectorAll("#crud-controls span").forEach(span => {
        span.addEventListener("click", () => {
            setCrudMode(span.dataset.mode);
        });
    });
}

function setCrudMode(mode) {
    state.currentMode = mode;
    document.querySelectorAll("#crud-controls span").forEach(s => s.classList.remove("active"));
    document.querySelector(`#crud-controls span[data-mode="${mode}"]`).classList.add("active");
    renderCurrentView();
}

function loadTable(app, model) {
    state.currentApp = app;
    state.currentModel = model;
    state.selectedRecordIds = [];
    fetch(`/crud/${app}/${model}/`, {
        headers: { "Authorization": `Bearer ${state.jwtToken}` }
    })
    .then(res => res.json())
    .then(data => {
        state.rows = data;
        state.currentPage = 1;
        setCrudMode("read"); // Always start in View mode
    });
}

function renderCurrentView() {
    if (!state.currentApp || !state.currentModel) {
        document.getElementById('table-container').innerHTML = `<p>Select a table first!</p>`;
        return;
    }
    switch (state.currentMode) {
        case "read":
            renderTableView();
            break;
        case "create":
            renderCreateForm();
            break;
        case "update":
            if (state.selectedRecordIds.length === 0) {
                document.getElementById('table-container').innerHTML = `<p>Select a record to update!</p>`;
            } else {
                renderUpdateForm();
            }
            break;
        case "delete":
            renderDeleteTable();
            break;
        case "file":
            renderRecordReport();
            break;
    }
}


function toggleGroup(app_label) {
    const list = document.querySelector(`.${app_label}-li`);
    list.style.display = (list.style.display === 'none' || list.style.display === '') ? 'block' : 'none';
}
function renderTableView() {
    let filteredRows = state.rows.filter(row =>
        Object.values(row).some(v => String(v).toLowerCase().includes(state.filterText.toLowerCase()))
    );

    if (state.sortColumn) {
        filteredRows.sort((a, b) => {
            let valA = a[state.sortColumn], valB = b[state.sortColumn];
            return state.sortDirection === "asc" ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
        });
    }

    const start = (state.currentPage - 1) * state.rowsPerPage;
    const pageRows = filteredRows.slice(start, start + state.rowsPerPage);

    let html = `<input type="text" placeholder="Filter..." oninput="state.filterText=this.value; renderTableView()">`;
    html += `<table><thead><tr>`;
    Object.keys(state.rows[0]).forEach(col => {
        html += `<th onclick="toggleSort('${col}')">${col.toUpperCase()}</th>`;
    });
    html += `</tr></thead><tbody>`;

    pageRows.forEach(row => {
        html += `<tr onclick="selectRecord(${row.id})">`;
        Object.values(row).forEach(val => html += `<td>${val}</td>`);
        html += `</tr>`;
    });
    html += `</tbody></table>`;
    html += renderPagination(filteredRows.length);
    document.getElementById("table-container").innerHTML = html;
}

function toggleSort(col) {
    if (state.sortColumn === col) {
        state.sortDirection = state.sortDirection === "asc" ? "desc" : "asc";
    } else {
        state.sortColumn = col;
        state.sortDirection = "asc";
    }
    renderTableView();
}

function renderPagination(total) {
    let pages = Math.ceil(total / state.rowsPerPage);
    let html = `<div class="pagination">`;
    for (let i = 1; i <= pages; i++) {
        html += `<span class="${i === state.currentPage ? 'active' : ''}" onclick="state.currentPage=${i}; renderTableView()">${i}</span>`;
    }
    html += `</div>`;
    return html;
}
function renderCreateForm() {
    let html = `<h3>Add New ${state.currentModel}</h3><form id="create-form">`;
    Object.keys(state.rows[0] || {}).forEach(key => {
        if (key !== "id") {
            html += `<label>${key}</label><input name="${key}">`;
        }
    });
    html += `<button type="button" onclick="submitCreate()">Save</button></form>`;
    document.getElementById("table-container").innerHTML = html;
}

function renderUpdateForm() {
    let record = state.rows.find(r => r.id === state.selectedRecordIds[0]);
    let html = `<h3>Update ${state.currentModel}</h3><form id="update-form">`;
    Object.keys(record).forEach(key => {
        if (key !== "id") {
            html += `<label>${key}</label><input name="${key}" value="${record[key]}">`;
        }
    });
    html += `<button type="button" onclick="submitUpdate(${record.id})">Update</button></form>`;
    document.getElementById("table-container").innerHTML = html;
}
function renderDeleteTable() {
    let html = `<h3>Delete ${state.currentModel}</h3><table><thead><tr><th>Select</th>`;
    Object.keys(state.rows[0]).forEach(col => html += `<th>${col}</th>`);
    html += `</tr></thead><tbody>`;
    state.rows.forEach(row => {
        html += `<tr><td><input type="checkbox" value="${row.id}" onchange="toggleSelect(${row.id}, this.checked)"></td>`;
        Object.values(row).forEach(val => html += `<td>${val}</td>`);
        html += `</tr>`;
    });
    html += `</tbody></table><button onclick="submitDelete()">Delete Selected</button>`;
    document.getElementById("table-container").innerHTML = html;
}
function renderRecordReport() {
    if (state.rows.length === 0) {
        document.getElementById('table-container').innerHTML = `<p>No records available.</p>`;
        return;
    }
    let index = state.selectedRecordIds.length > 0
        ? state.rows.findIndex(r => r.id === state.selectedRecordIds[0])
        : 0;

    let record = state.rows[index];
    let html = `<div class="record-report"><h3>${state.currentModel} Report</h3>`;
    for (let key in record) {
        html += `<p><strong>${key}:</strong> ${record[key]}</p>`;
    }
    html += `<div class="record-nav">
        <button ${index === 0 ? 'disabled' : ''} onclick="navigateRecord(${index - 1})">Prev</button>
        <button ${index === state.rows.length - 1 ? 'disabled' : ''} onclick="navigateRecord(${index + 1})">Next</button>
    </div></div>`;
    document.getElementById("table-container").innerHTML = html;
}

function navigateRecord(newIndex) {
    state.selectedRecordIds = [state.rows[newIndex].id];
    renderRecordReport();
}
