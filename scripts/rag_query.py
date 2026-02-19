import faiss
import json
import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

def embed_query(q):
    r = requests.post(
        "https://api.openai.com/v1/embeddings",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={"model": "text-embedding-3-small", "input": q}
    )
    return np.array(r.json()["data"][0]["embedding"]).astype("float32")

def main():
    index = faiss.read_index("data/faiss.index")
    chunks = json.load(open("data/chunks.json", encoding="utf-8"))

    question = input("질문: ")
    q_emb = embed_query(question)

    _, idx = index.search(np.array([q_emb]), 3)
    context = "\n\n".join(chunks[i] for i in idx[0])

    # LLM 호출 (Groq)
    print(context)

if __name__ == "__main__":
    main()
