from flask import Flask, render_template, request, redirect
import sqlite3
import ollama

app = Flask(__name__)

# 設定 SQLite 資料庫
DATABASE = 'notes.db'

# 創建資料庫表格
def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT)''')
    conn.commit()
    conn.close()

create_table()

def generate_answer_with_ollama(question_1):
    response = ollama.chat(
        model="phi3:3.8b-mini-128k-instruct-q4_K_M",
        #model="yabi/breeze-7b-32k-instruct-v1_0_q4_k",
        messages=[
            {"role": "user", "content": question_1},
        ]
    )

    return response["message"]["content"]

# 首頁路由，顯示所有筆記
@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM notes")
    fetched_notes = c.fetchall()
    conn.close()
    notes = []
    for fetched_note in fetched_notes:
        note = (fetched_note[0], fetched_note[1], fetched_note[2])
        notes.append(note)
    return render_template('index.html', notes=notes)

# 新增筆記路由
@app.route('/add_note', methods=['POST'])
def add_note():
    title = request.form['title']
    content = request.form['content']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()
    return redirect('/')

# RAG筆記路由
@app.route('/rag_note', methods=['POST'])
def rag_note():
    question_1 = request.form['question_1']
    
    answer = generate_answer_with_ollama(question_1)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
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
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE notes SET title=?, content=? WHERE id=?", (title, content, note_id))
    conn.commit()
    conn.close()
    return redirect('/')

# 刪除筆記的路由
@app.route('/delete_note', methods=['POST'])
def delete_note():
    note_id = request.form['id']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
    return redirect('/')

# 清空資料庫路由
@app.route('/clear_database', methods=['POST'])
def clear_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM notes")
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5500)
