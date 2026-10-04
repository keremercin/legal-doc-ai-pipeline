from io import BytesIO
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from legal_doc_ai.core.pipeline import DocumentPipeline
from legal_doc_ai.main import app
from legal_doc_ai.services.ocr import ExtractionError, OCRService


@pytest.mark.parametrize('name,content', [('blank.txt', b'  \n'), ('unknown.bin', b'content'), ('invalid.txt', b'\xff')])
def test_invalid_extraction_never_reaches_store(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content)
    store = Mock()
    pipeline = DocumentPipeline(store)
    pipeline.classifier = Mock()
    with pytest.raises(ExtractionError):
        pipeline.ingest(path)
    store.add_document.assert_not_called()
    pipeline.classifier.classify.assert_not_called()


def test_blank_pdf_reports_preprocessing_requirement(tmp_path):
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    path = tmp_path / 'blank.pdf'
    writer.write(path)
    with pytest.raises(ExtractionError, match='OCR preprocessing'):
        OCRService().extract_text(path)


def test_unsupported_upload_is_client_error():
    response = TestClient(app).post('/v1/ingest', files={'file': ('input.bin', BytesIO(b'content'), 'application/octet-stream')})
    assert response.status_code == 422
    assert 'Unsupported file type' in response.json()['error']['message']



def test_malformed_pdf_upload_is_client_error():
    response = TestClient(app).post('/v1/ingest', files={'file': ('broken.pdf', b'not a PDF', 'application/pdf')})
    assert response.status_code == 422
    assert 'PDF could not be parsed' in response.json()['error']['message']


def test_whitespace_question_is_validation_error():
    response = TestClient(app).post('/v1/qa', json={'question': '   ', 'top_k': 3})
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'VALIDATION_ERROR'
