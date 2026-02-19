from pdf_loader import load_pdf_text
from chunker import chunk_text
from build_index import main as build_index
from rag_pipeline import answer_question

def main():
    text = load_pdf_text("fss_guide_2025.pdf")
    chunks = chunk_text(text)

    print(f"총 청크 수: {len(chunks)}")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- chunk {i} ---\n")
        print(chunk[:500])

def run():
    store, embedder = build_index()

    while True:
        q = input("\n질문을 입력하세요 (종료: exit): ")
        if q == "exit":
            break

        answer = answer_question(q, store, embedder)
        print("\n답변:\n", answer)

if __name__ == "__main__":
    run()
