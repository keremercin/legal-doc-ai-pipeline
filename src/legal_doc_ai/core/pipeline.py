from pathlib import Path

from legal_doc_ai.config import get_settings
from legal_doc_ai.services.chunker import simple_chunk
from legal_doc_ai.services.classifier import ClassifierService
from legal_doc_ai.services.entities import LegalEntityExtractor
from legal_doc_ai.services.ocr import ExtractionError, OCRService
from legal_doc_ai.services.vector_store import VectorStore

settings = get_settings()


class DocumentPipeline:
    def __init__(self, store: VectorStore) -> None:
        self.ocr = OCRService()
        self.classifier = ClassifierService()
        self.entity_extractor = LegalEntityExtractor()
        self.store = store

    def ingest(self, file_path: Path) -> dict:
        text = self.ocr.extract_text(file_path)
        if not text.strip():
            raise ExtractionError("Document contains no extractable text")
        classification = self.classifier.classify(text)
        entities = self.entity_extractor.extract(text)
        chunks = simple_chunk(
            text=text,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )

        result = self.store.add_document(
            filename=file_path.name,
            classification=classification,
            full_text=text,
            chunks=chunks,
        )
        result["metadata"] = {
            **result.get("metadata", {}),
            "entities": {
                "parties": len(entities.get("parties", [])),
                "dates": len(entities.get("dates", [])),
                "amounts": len(entities.get("amounts", [])),
                "obligations": len(entities.get("obligations", [])),
            },
        }
        return result
