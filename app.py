from flask import Flask, render_template, request, redirect, jsonify

import ollama
import chromadb


app = Flask(__name__)

# 設定 SQLite 資料庫
DATABASE = 'notes.db'

# 連接 ChromaDB 資料庫
client = chromadb.PersistentClient("vector_embedding_db")
collection = client.get_or_create_collection("embedding_db", metadata={"key": "value"})


documents = []


# 創建資料庫表格
def create_table():
    conn = chromadb.sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT)''')
    conn.commit()
    conn.close()

create_table()

def get_conn_last_row_id():
    conn = chromadb.sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT last_insert_rowid()")
    last_row_id = c.fetchone()[0]
    conn.close()
    return last_row_id

def delect_chromadb():
    collection = client.get_or_create_collection("embedding_db", metadata={"key": "value"})
    client.delete_collection(name="embedding_db")



def generate_answer_with_ollama(question_1):
    collection = client.get_or_create_collection("embedding_db", metadata={"key": "value"})
    # an example prompt
    prompt = f"""\
                你是一個專業的訊息檢索人員，根據過去的內容而非事先知識，回答問題，不知道就說不知道。
                以下是一些示例。
                查詢: {question_1}
                回答:
                """
    # generate an embedding for the prompt and retrieve the most relevant doc
    response = ollama.embeddings(
        prompt=question_1,
        model="mxbai-embed-large"
        )
    
    results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=1
        )
    
    data = results['documents']

    output = ollama.generate(
        model="phi3:3.8b-mini-128k-instruct-q4_K_M",
        prompt=f"使用這些內容: {data}. 回應這個prompt: {prompt}"
        )
    return output["response"]

# 首頁路由，顯示所有筆記
@app.route('/')
def index():
    #如果沒有notes表格，則創建一個
    if not chromadb.sqlite3.connect(DATABASE).execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'").fetchone():
        create_table()
    conn = chromadb.sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    fetched_notes = c.fetchall()
    conn.close()
    notes = []
    for fetched_note in fetched_notes:
        fetched_note = list(fetched_note)
        fetched_note[1]= fetched_note[1].replace(')', ' ').replace('(', ' ')
        fetched_note[2]= fetched_note[2].replace('(', ' ').replace(')', ' ')
        note = (fetched_note[0], fetched_note[1], fetched_note[2])    
        notes.append(note)


    return render_template('index.html', notes=notes)

# 搜尋筆記路由
@app.route('/select_note', methods=['POST'])
def select_note():
    id = request.json['id']
    conn = chromadb.sqlite3.connect(DATABASE)
    conn.row_factory = chromadb.sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id=?", (id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify(dict(result)), 200
    else:
        return jsonify({"error": "Note not found"}), 404

# 新增筆記路由
@app.route('/add_note', methods=['POST'])
def add_note():

    id = get_conn_last_row_id()
    title = request.form['title']
    content = request.form['content']
    conn = chromadb.sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()
    # store each document in a vector embedding database
    response = ollama.embeddings(model="mxbai-embed-large", prompt=content+","+title)
    embedding = response["embedding"]

    collection = client.get_or_create_collection("embedding_db", metadata={"key": "value"})
    collection.add(
        ids=[str(id+1)],
        embeddings=[embedding],
        documents=str(id+1)+','+content+","+title
    )
    return redirect('/')

# RAG筆記路由
@app.route('/rag_note', methods=['POST'])
def rag_note():
    conn = chromadb.sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    fetched_notes = c.fetchall()
    
    if len(fetched_notes) == 0:
        return redirect('/')
    else:
        question_1 = request.form['question_1']
        answer = generate_answer_with_ollama(question_1) 
        c.execute("INSERT INTO notes (title, content) VALUES (?, ?)", ('RAG Generated Note', answer))
    conn.commit()
    conn.close()
    return redirect('/')
    

# 修改筆記路由
@app.route('/edit_note', methods=['POST'])
def edit_note():
    note_id = request.form['id']
    title = request.form['title']
    content = request.form['content']
    conn = chromadb.sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title, content, note_id))
    conn.commit()
    conn.close()
    return redirect('/')

# 刪除筆記的路由
@app.route('/delete_note', methods=['POST'])
def delete_note():
    note_id = request.form['id']

    collection = client.get_or_create_collection("embedding_db", metadata={"key": "value"})
    collection.delete(ids=note_id)
    conn = chromadb.sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
    return redirect('/')

# 清空資料庫路由
@app.route('/clear_database', methods=['POST'])
def clear_database():
    delect_chromadb()
    conn = chromadb.sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE  FROM notes")
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5500)
