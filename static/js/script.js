
function openAddForm() {
    closeRagForm()
    document.getElementById("noteAddForm").style.display = "block";
}

function closeAddForm() {
    document.getElementById("noteAddForm").style.display = "none";
}

function openRagForm() {
    closeAddForm()
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
            closeAddForm()
            closeRagForm()
            closeRagResultForm()
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
    document.getElementById("editModal").style.display = "block";
    document.getElementById("orgModal").style.display = "none";

}

function closeEditForm() {
    document.getElementById("editModal").style.display = "none";
    document.getElementById("orgModal").style.display = "block";
    document.getElementById("editForm").style.display = "none";
}

function ClearAlert() {
    document.getElementById("alert-popup").style.display = "block";
}

function closeAlert() {
    document.getElementById("alert-popup").style.display = "none";
}

document.addEventListener('DOMContentLoaded', function() {
    // 绑定RAG表单的提交事件
    const ragForm = document.getElementById("ragForm");
    if (ragForm) {
        ragForm.addEventListener("submit", handleRagFormSubmit);
    }
});

function handleRagFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const question = form.question_1.value;

    // 显示加载消息
    document.getElementById("loadingMessage").style.display = "block";

    fetch('/rag_note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            question_1: question,
        }),
    })
    .then(response => response.json())
    .then(data => {

        document.getElementById("loadingMessage").style.display = "none";

        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("resultQuestion").value = data.question;
            document.getElementById("resultAnswer").value = data.answer;
            document.getElementById("noteRagResultForm").style.display = "block";
            enable_all_buttons();
        }
    })
    .catch(error => {
        // 隐藏加载消息
        document.getElementById("loadingMessage").style.display = "none";
        console.error('Error:', error);
    });
}

function closeRagResultForm() {
    document.getElementById("noteRagResultForm").style.display = "none";
}

function openRagForm() {
    closeAddForm()
    closeRagResultForm()
    document.getElementById("noteRagForm").style.display = "block";
}

function closeRagForm() {
    document.getElementById("noteRagForm").style.display = "none";
}

function disable_all_buttons() {
    document.getElementById("addButton").disabled = true;
    document.getElementById("editButton").disabled = true;
    document.getElementById("clearButton").disabled = true;
    document.getElementById("ragButton").disabled = true;
    document.getElementById("saveButton").disabled = true;
    document.getElementById("deleteButton").disabled = true;
    document.getElementById("pdfButton").disabled = true;
}

function rag_button() {
    disable_all_buttons();
    closeRagForm();
}
function enable_all_buttons() {
    document.getElementById("addButton").disabled = false;
    document.getElementById("editButton").disabled = false;false
    document.getElementById("clearButton").disabled = false;
    document.getElementById("ragButton").disabled = false;
    document.getElementById("saveButton").disabled = false;
    document.getElementById("deleteButton").disabled = false;
    document.getElementById("pdfButton").disabled = false;
}

document.getElementById('pdfButton').addEventListener('click', () => {
    document.getElementById('pdfFile').click();
});

document.getElementById('pdfFile').addEventListener('change', uploadPDF);

function uploadPDF() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a PDF file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/read_pdf', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            console.log("Extracted Text: ", data.text);
            
            alert("PDF uploaded successfully. Please wait a few seconds for embedding the text into the note.");
            fetch('/add_note', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    title: file.name,
                    content: data.text,
                })
            })
            .then(response => {
                if (response.ok) {
                    alert("Note added successfully!");
                    location.reload();  // 重新整理頁面
                } else {
                    alert("Failed to add the note.");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred while adding the note.");
            });
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while uploading the PDF.");
    });
}


