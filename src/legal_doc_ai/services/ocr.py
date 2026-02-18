from pathlib import Path

import pytesseract
from pypdf import PdfReader


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
            return file_path.read_text(encoding="utf-8", errors="ignore")

        if suffix == ".pdf":
            return self._read_pdf(file_path)

        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}:
            return self._read_image(file_path)

        return (
            "[unsupported_file_type] Convert input to txt/pdf/image or integrate "
            "additional parsers in OCRService."
        )

    def _read_pdf(self, file_path: Path) -> str:
        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        return text or "[empty_pdf_text]"

    def _read_image(self, file_path: Path) -> str:
        from PIL import Image

        with Image.open(file_path) as image:
            text = pytesseract.image_to_string(image)
        return text.strip() or "[empty_ocr_text]"
