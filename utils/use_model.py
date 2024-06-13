import chromadb
import ollama
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