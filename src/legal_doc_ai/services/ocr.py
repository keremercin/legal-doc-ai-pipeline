from pathlib import Path

import pytesseract
from pypdf import PdfReader
from pypdf.errors import PdfReadError


class ExtractionError(ValueError):
    """Input cannot yield indexable text; never store diagnostic text as content."""


class OCRService:
    """Text extraction service.

    v2 behavior:
    - .txt: read directly
    - .pdf: parse with pypdf
    - image formats: OCR with pytesseract + PIL
    """

    def extract_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()

        if suffix == ".txt":
            try:
                text = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                raise ExtractionError("Text input must use UTF-8 encoding") from exc
            if not text.strip():
                raise ExtractionError("Document contains no extractable text")
            return text

        if suffix == ".pdf":
            return self._read_pdf(file_path)

        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}:
            return self._read_image(file_path)

        raise ExtractionError("Unsupported file type; use txt, PDF or a supported image")

    def _read_pdf(self, file_path: Path) -> str:
        try:
            reader = PdfReader(str(file_path))
            pages = [page.extract_text() or "" for page in reader.pages]
        except (PdfReadError, ValueError) as exc:
            raise ExtractionError("PDF could not be parsed; verify the document is readable and unencrypted") from exc
        text = "\n".join(pages).strip()
        if not text:
            raise ExtractionError("PDF contains no extractable text; scanned PDFs require OCR preprocessing")
        return text

    def _read_image(self, file_path: Path) -> str:
        from PIL import Image

        with Image.open(file_path) as image:
            text = pytesseract.image_to_string(image)
        if not text.strip():
            raise ExtractionError("Image OCR returned no text")
        return text.strip()
