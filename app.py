from flask import Flask, render_template, request, redirect, jsonify
from utils.use_model import generate_answer_with_ollama
import ollama
import chromadb
import uuid
import fitz

app = Flask(__name__)

# 連接 ChromaDB 資料庫
client = chromadb.PersistentClient("vector_embedding_db")
collection = client.get_or_create_collection("embedding_db", metadata={"key": "value"})


@app.route('/')
def index():
    results = collection.get()
    notes = []
    for doc in results["documents"]:
        note_id, title, content = doc.split(',', 2)
        notes.append((note_id, title.replace(')', ' ').replace('(', ' '), content.replace('(', ' ').replace(')', ' ')))
    return render_template('index.html', notes=notes)

@app.route('/select_note', methods=['POST'])
def select_note():
    collection_name = request.json['collection_name']
    collection = client.get_or_create_collection( collection_name, metadata={"key": "value"})
    note_id = request.json['id']
    results = collection.get(ids=[note_id])
    if results["documents"]:
        doc = results["documents"][0]
        note_id, title, content = doc.split(',', 2)
        return jsonify({"id": note_id, "title": title, "content": content}), 200
    return jsonify({"error": "Note not found"}), 404

@app.route('/add_note', methods=['POST'])
def add_note():
    ids = str(uuid.uuid4())
    title = request.form['title']
    content = request.form['content']
    response = ollama.embeddings(model="mxbai-embed-large", prompt=f"{title},{content}")
    embedding = response["embedding"]
    collection.add(
        ids=[ids],
        embeddings=[embedding],
        documents=[f"{ids},{title},{content}"]
    )
    return redirect('/')

@app.route('/read_pdf', methods=['POST'])
def read_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    try:

        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        text = ""

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        
        return jsonify({"text": text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route('/rag_note', methods=['POST'])
def rag_note():
    collection = client.get_or_create_collection("rag_history", metadata={"key": "value"})
    ids = str(uuid.uuid4())
    question = request.form['question_1']
    answer = generate_answer_with_ollama(question)
    collection.add(
        ids=[ids],
        embeddings=[ollama.embeddings(model="mxbai-embed-large", prompt=f"{question} — by RAG,{answer}")["embedding"]],
        documents=[f"{ids},{question},{answer}"]
    )
    return jsonify({"question": question, "answer": answer}), 200

@app.route('/edit_note', methods=['POST'])
def edit_note():
    collection_name = request.form['collection_name']
    collection = client.get_or_create_collection( collection_name, metadata={"key": "value"})
    note_id = request.form['id']
    title = request.form['title']
    content = request.form['content']
    collection.update(
        ids=[note_id],
        embeddings=[ollama.embeddings(model="mxbai-embed-large", prompt=f"{title},{content}")["embedding"]],
        documents=[f"{note_id},{title},{content}"]
    )
    return redirect('/')

@app.route('/delete_note', methods=['POST'])
def delete_note():
    collection_name = request.form['collection_name']
    collection = client.get_or_create_collection( collection_name, metadata={"key": "value"})
    note_id = request.form['id']
    try:
        collection.delete(ids=[note_id])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return redirect('/')

@app.route('/clear_database', methods=['POST'])
def clear_database():
    collection_name = request.form['collection_name']
    collection = client.get_or_create_collection( collection_name, metadata={"key": "value"})
    for each in collection.get()['documents']:
        collection.delete(ids=[each.split(',')[0]])
    return redirect('/')

@app.route('/rag_history')
def rag_history():
    collection = client.get_or_create_collection("rag_history", metadata={"key": "value"})
    documents = collection.get()['documents']
    rag_data = []
    for doc in documents:
        parts = doc.split(",")
        entry = {
                "id": parts[0],
                "question": parts[1],
                "answer": parts[2],
            }
        rag_data.append(entry)
        
    return render_template('rag_history.html', rag_data=rag_data)

if __name__ == '__main__':
    app.run(debug=True, port=5500)
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=5500)
