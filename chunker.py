import re
from typing import List

def chunk_text(text: str, max_length: int = 800) -> List[str]:
    """
    1차: 장 단위 분리
    2차: 길이 기준 재분할
    """

    # 1️⃣ 장 단위 분리 (제1장, 제2장 등)
    chapter_pattern = r"(제\s*\d+\s*장)"
    parts = re.split(chapter_pattern, text)

    chunks = []
    buffer = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if re.match(chapter_pattern, part):
            if buffer:
                chunks.extend(_split_by_length(buffer, max_length))
                buffer = part
            else:
                buffer = part
        else:
            buffer += "\n" + part

    if buffer:
        chunks.extend(_split_by_length(buffer, max_length))

    return chunks


def _split_by_length(text: str, max_length: int) -> List[str]:
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(" ".join(current)) >= max_length:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks
