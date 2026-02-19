import json
import fitz
import faiss
import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

EMBED_URL = "https://api.openai.com/v1/embeddings"
MODEL = "text-embedding-3-small"

def load_pdf(path):
    doc = fitz.open(path)
    return "".join(page.get_text() for page in doc)

def chunk(text, size=800, overlap=100):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start+size])
        start += size - overlap
    return chunks

def embed(texts):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    vectors = []
    for t in texts:
        r = requests.post(
            EMBED_URL,
            headers=headers,
            json={"model": MODEL, "input": t}
        )
        vectors.append(r.json()["data"][0]["embedding"])
    return np.array(vectors).astype("float32")

def main():
    text = load_pdf("data/raw/fss_guide_2025.pdf")
    chunks = chunk(text)

    embeddings = embed(chunks)

    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)

    faiss.write_index(index, "data/faiss.index")

    with open("data/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)

    print("✅ 인덱스 생성 완료")

if __name__ == "__main__":
    main()
