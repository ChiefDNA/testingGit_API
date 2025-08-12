let currentApp = null;
let currentModel = null;
let jwtToken = null; // Set this after login or however you get your token

function setJwtToken(token) {
    jwtToken = token;
}

document.addEventListener("DOMContentLoaded", () => {
    const tokenMeta = document.querySelector('meta[name="jwt-token"]');
    if (tokenMeta) {
        setJwtToken(tokenMeta.getAttribute('content'));
    }
});

function loadTable(app, model) {
    currentApp = app;
    currentModel = model;

    document.getElementById('main-title').textContent = model;
    // Optional: store currentApp visibly or in a hidden element if needed

    fetch(`/crud/${app}/${model}/`, {
        headers: {
            'Authorization': 'Bearer ' + jwtToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Failed to load: ${response.statusText}`);
            console.log(response.statusText);
        }
        return response.json();
    })
    .then(data => {
        renderTable(model, data);
    })
    .catch(err => {
        document.getElementById('table-container').innerHTML = `<p>Error loading data: ${err.message}</p>`;
    });
}

function toggleGroup(app_label) {
    const list = document.querySelector(`.${app_label}-li`);
    list.style.display = (list.style.display === 'none' || list.style.display === '') ? 'block' : 'none';
}

function renderTable(modelName, rows) {
    if (!rows || rows.length === 0) {
        document.getElementById('table-container').innerHTML = "<p>No data available</p>";
        return;
    }

    const headers = Object.keys(rows[0]);
    let html = `<table><thead><tr>`;

    headers.forEach(header => {
        html += `<th>${header.toUpperCase()}</th>`;
    });

    html += `<th>Actions</th></tr></thead><tbody>`;

    rows.forEach(row => {
        html += `<tr>`;
        headers.forEach(header => {
            html += `<td contenteditable="false">${row[header]}</td>`;
        });

        html += `<td class="crud-actions">`;
        html += `<button onclick="editRow(this)">✏️</button>`;
        html += `<button onclick="deleteRow('${currentApp}', ${row.id}, '${modelName}')">🗑️</button>`;
        html += `</td>`;
        html += `</tr>`;
    });

    // Add last row (for CREATE)
    html += `<tr>`;
    headers.forEach(() => {
        html += `<td contenteditable="true" data-new="true"></td>`;
    });
    html += `<td class="crud-actions"><button onclick="createRow('${currentApp}', '${modelName}')">➕</button></td></tr>`;

    html += `</tbody></table>`;
    document.getElementById('table-container').innerHTML = html;
}

function editRow(btn) {
    const row = btn.closest('tr');
    row.querySelectorAll('td').forEach(td => {
        if (!td.classList.contains('crud-actions')) {
            td.contentEditable = true;
        }
    });
    btn.textContent = '💾';
    btn.onclick = () => saveRow(row);
}

function saveRow(row) {
    const cells = row.querySelectorAll('td');
    const data = {};
    const id = cells[0].textContent.trim();

    const ths = document.querySelectorAll('th');
    cells.forEach((td, i) => {
        if (!td.classList.contains('crud-actions')) {
            const key = ths[i].textContent.trim();
            data[key] = td.textContent.trim();
        }
    });

    fetch(`/crud/${currentApp}/${currentModel}/${id}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwtToken
        },
        body: JSON.stringify(data)
    })
    .then(res => {
        if (res.ok) {
            location.reload();
        } else {
            alert('Failed to save record.');
        }
    });
}

function deleteRow(app, id, modelName) {
    if (confirm("Are you sure you want to delete this record?")) {
        fetch(`/crud/${app}/${modelName}/${id}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': 'Bearer ' + jwtToken
            }
        }).then(res => {
            if (res.ok) {
                location.reload();
            } else {
                alert('Failed to delete record.');
            }
        });
    }
}

function createRow(app, modelName) {
    const newRow = document.querySelector('[data-new]');
    if (!newRow) {
        alert('No editable row found for creating new record.');
        return;
    }
    const cells = newRow.parentElement.querySelectorAll('[data-new]');
    const data = {};
    const ths = document.querySelectorAll('th');

    cells.forEach((cell, i) => {
        const key = ths[i].textContent.trim();
        data[key] = cell.textContent.trim();
    });

    fetch(`/crud/${app}/${modelName}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + jwtToken
        },
        body: JSON.stringify(data)
    }).then(res => {
        if (res.ok) {

            location.reload();
        } else {
            alert('Failed to create record.');
        }
    });
}
