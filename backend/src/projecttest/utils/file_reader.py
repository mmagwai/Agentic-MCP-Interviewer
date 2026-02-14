import os


def read_cv_file(path: str) -> str:
    """
    Read CV content from a TXT or PDF file and return plain text.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    # ================= TXT =================
    if path.lower().endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # ================= PDF =================
    elif path.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "pypdf is required to read PDF files. Install with: pip install pypdf"
            )

        reader = PdfReader(path)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        return text

    # ================= OTHER =================
    else:
        raise ValueError("Unsupported file type. Please provide PDF or TXT.")
