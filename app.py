from flask import Flask, render_template, request, redirect, jsonify
import ollama
import chromadb
import uuid
import fitz

app = Flask(__name__)

# 連接 ChromaDB 資料庫
client = chromadb.PersistentClient("vector_embedding_db")
collection = client.get_or_create_collection("embedding_db", metadata={"key": "value"})


def generate_answer_with_ollama(question):
    prompt = f"""\
        你是一個專業的訊息檢索人員，根據過去的內容而非事先知識，回答問題，不知道就說不知道。
        以下是一些示例。
        查詢: {question}
        回答:
    """
    response = ollama.embeddings(
        prompt=question,
        model="mxbai-embed-large"
    )
    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=1
    )
    data = results['documents']
    output = ollama.generate(
        model="phi3:3.8b-mini-128k-instruct-q4_K_M",
        prompt=f"使用這些內容: {data}. 回應這個prompt: {prompt}，生成大約100字的內容。"
    )
    return output["response"]

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
    #ids = str(uuid.uuid4())
    question = request.form['question_1']
    answer = generate_answer_with_ollama(question)
   #collection.add(
   #    ids=[ids],
   #    embeddings=[ollama.embeddings(model="mxbai-embed-large", prompt=answer)["embedding"]],
   #    documents=[f"{ids},{question} — by RAG,{answer}"]
   #)
    return jsonify({"question": question, "answer": answer}), 200

@app.route('/edit_note', methods=['POST'])
def edit_note():
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
    note_id = request.form['id']
    try:
        collection.delete(ids=[note_id])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return redirect('/')

@app.route('/clear_database', methods=['POST'])
def clear_database():
    for each in collection.get()['documents']:
        collection.delete(ids=[each.split(',')[0]])
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5500)
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=5500)
