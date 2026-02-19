import pdfplumber
import re

# ---------------------
# 텍스트 정제 유틸
# ---------------------

def remove_dotted_lines(text: str) -> str:
    return re.sub(r"⋯{2,}.*\d+", "", text)

def remove_icon_lines(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if not re.match(r"^[-]", line.strip())
    )

def remove_toc_style_lines(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if not re.search(r"•\d+$", line.strip())
    )

def remove_short_noise_lines(text: str, min_length=20) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if len(line.strip()) >= min_length
    )

def clean_text(text: str) -> str:
    text = remove_dotted_lines(text)
    text = remove_icon_lines(text)
    text = remove_toc_style_lines(text)
    text = remove_short_noise_lines(text)
    return text


# ---------------------
# PDF 로더
# ---------------------

def load_pdf_text(pdf_path: str, start_page=0, end_page=None) -> str:
    texts = []

    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages[start_page:end_page]
        for page in pages:
            raw = page.extract_text()
            if raw:
                texts.append(clean_text(raw))

    return "\n".join(texts)


