import pdfplumber

PDF_PATH = "fss_guide_2025.pdf"

def test_pdf_extract(start=0, end=10):
    with pdfplumber.open(PDF_PATH) as pdf:
        for i, page in enumerate(pdf.pages[start:end], start=start + 1):
            print(f"\n===== PAGE {i} =====")
            text = page.extract_text()
            print("start: ", start)
            print("end: ", end)
            if text:
                print(text[:1000])  # 앞부분만
            else:
                print("[텍스트 없음]")

if __name__ == "__main__":
    test_pdf_extract(22, 23)
