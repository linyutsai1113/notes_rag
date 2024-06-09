## 基本教學



### 下載程式檔案

##### Use git：

`git clone https://github.com/linyutsai1113/notes_rag.git`

...



### 建立python 環境

##### Use conda：

`conda create -n notes_rag python==3.9`

`conda activate notes_rag`

`pip install -r requirements.txt`

...




### 安裝 ollama

請到這裡下載[Ollama](https://www.ollama.com/)，下載好之後打開terminal執行以下指令，用以安裝對應模型

`ollama pull phi3:3.8b-mini-128k-instruct-q4_K_M`

`ollama pull mxbai-embed-large`

...




### 進目標資料夾執行程式

##### For example：

`cd C:\Users\user\notes-RAG`

`python app.py`
