"""PyMuPDF-based PDF parser."""

import hashlib
from pathlib import Path
import fitz  # PyMuPDF
from rag_kb.models import Document


class PyMuPDFParser:
    """PDF parser using PyMuPDF (fitz)."""
    
    supported_ext = ('.pdf',)

    def parse(self, path: Path) -> Document:
        """Parse PDF file and return Document."""
        doc = fitz.open(path)
        parts = []
        for page in doc:
            parts.append(page.get_text())
        content = '\n\n'.join(parts)
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return Document(
            doc_id=file_hash[:16],
            title=path.stem,
            source=str(path),
            content=content,
            metadata={'pages': len(doc), 'parser': 'pymupdf'},
            file_hash=file_hash,
        )