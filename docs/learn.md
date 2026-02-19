[Python 코드]
↓ HTTP 요청
[Groq API 서버]
↓
[LLaMA 3.3 70B 모델]
↓
[응답 JSON]
↓
[터미널 출력]

===================
pdfplumber는 “추출 단계”
임베딩 API는 “벡터화 단계”
FAISS는 “검색 단계”
Groq는 “생성 단계”

===================
asset-ai/
├─ pdf_loader.py ← PDF 로딩 + 정제
├─ chunker.py ← 제목 기준 청킹
├─ build_index.py ← 임베딩 + 벡터 DB 저장
├─ rag_pipeline.py ← 질의 → 검색 → LLM
└─ main.py ← 실행 진입점

pdf_loader.py
→ “PDF → 쓸만한 텍스트”
chunker.py
→ “텍스트 → 의미 단위”
build_index.py
→ “의미 단위 → 벡터”
rag_pipeline.py
→ “질문 → 답변”
