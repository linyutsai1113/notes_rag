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

function openModal(id, title, content) {
    document.getElementById("modalTitle").innerText = title;
    document.getElementById("modalContent").innerText = content;
    document.getElementById("noteModal").style.display = "block";
    document.getElementById("editId").value = id;
    document.getElementById("editTitle").value = title;
    document.getElementById("editContent").value = content.replace(/<br\/>/g, '\n');
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
