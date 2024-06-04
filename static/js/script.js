
function openAddForm() {
    document.getElementById("noteAddForm").style.display = "block";
}

function closeAddForm() {
    document.getElementById("noteAddForm").style.display = "none";
}

function openRagForm() {
    document.getElementById("noteRagForm").style.display = "block";
}

function closeRagForm() {
    document.getElementById("noteRagForm").style.display = "none";
}

function openDeleteForm() {
    document.getElementById("delete-alert-popup").style.display = "block";
}

function closeDeleteForm() {
    document.getElementById("delete-alert-popup").style.display = "none";
}

function openModal(id, title, content) {
    document.getElementById("deleteId").value = id;
    document.getElementById("modalTitle").innerText = title;
    document.getElementById("modalContent").innerText = content;
    document.getElementById("noteModal").style.display = "block";
    document.getElementById("editId").value = id;
    document.getElementById("editTitle").value = title;
    document.getElementById("editContent").value = content;
}


function openModalBySelect(id) {
    document.getElementById("editId").value = id;
    document.getElementById("deleteId").value = id;
    document.getElementById("selectId").value = id;
    fetch('/select_note', { 
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "id": id }),
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById("modalTitle").innerText = data.title;
            document.getElementById("modalContent").innerText = data.content;
            document.getElementById("noteModal").style.display = "block";
            document.getElementById("editTitle").value = data.title;
            document.getElementById("editContent").value = data.content;
        });
}

function closeModal() {
    document.getElementById("noteModal").style.display = "none";
}

function openEditForm() {
    document.getElementById("editForm").style.display = "block";
}

function closeEditForm() {
    document.getElementById("editForm").style.display = "none";
}

function ClearAlert() {
    document.getElementById("alert-popup").style.display = "block";
}

function closeAlert() {
    document.getElementById("alert-popup").style.display = "none";
}
