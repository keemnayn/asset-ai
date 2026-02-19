import os
import fitz  # pymupdf
import numpy as np
import faiss
import requests
from dotenv import load_dotenv

# =====================
# 환경 설정
# =====================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
LLM_MODEL = "llama-3.3-70b-versatile"

EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI-compatible
EMBEDDING_URL = "https://api.openai.com/v1/embeddings"
OPENAI_API_KEY = GROQ_API_KEY  # Groq는 OpenAI 호환

# =====================
# 1. PDF 로드
# =====================
def load_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# =====================
# 2. Chunking
# =====================
def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# =====================
# 3. Embedding (API)
# =====================
def embed_texts(texts):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    embeddings = []
    for t in texts:
        res = requests.post(
            EMBEDDING_URL,
            headers=headers,
            json={
                "model": EMBEDDING_MODEL,
                "input": t
            }
        )
        res.raise_for_status()
        embeddings.append(res.json()["data"][0]["embedding"])

    return np.array(embeddings).astype("float32")

# =====================
# 4. FAISS 인덱스 생성
# =====================
def build_faiss(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

# =====================
# 5. 검색
# =====================
def search(index, query_embedding, k=3):
    distances, indices = index.search(
        np.array([query_embedding]).astype("float32"),
        k
    )
    return indices[0]

# =====================
# 6. LLM 호출 (Groq)
# =====================
def ask_llm(context, question):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
너는 문서 기반 QA 시스템이다.
아래 문서 내용을 기반으로 질문에 답하라.

[문서]
{context}

[질문]
{question}
"""

    res = requests.post(
        GROQ_URL,
        headers=headers,
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
    )

    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

# =====================
# main
# =====================
def main():
    print("PDF 로딩 중...")
    text = load_pdf("fss_guide_2025.pdf")

    print("청킹 중...")
    chunks = chunk_text(text)

    print("임베딩 생성 중...")
    embeddings = embed_texts(chunks)

    print("FAISS 인덱스 생성...")
    index = build_faiss(embeddings)

    question = input("\n질문을 입력하세요: ")

    print("질문 임베딩...")
    query_embedding = embed_texts([question])[0]

    print("문서 검색...")
    top_idx = search(index, query_embedding, k=3)

    context = "\n\n".join([chunks[i] for i in top_idx])

    print("\nLLM 호출 중...\n")
    answer = ask_llm(context, question)

    print("=== 답변 ===")
    print(answer)


if __name__ == "__main__":
    main()
