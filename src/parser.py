from pypdf import PdfReader

from .models import Document, Page


def parse_pdf(file_path: str) -> Document:
    reader = PdfReader(file_path)
    file_name = file_path.rsplit("/", 1)[-1]
    document = Document(name=file_name)

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text.endswith("\n"):
            text += "\n"
        document.pages.append(Page(content=text, number=i))

    return document