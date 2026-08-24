"""PDFPlumber-based PDF parser with table support."""

import hashlib
from pathlib import Path
import pdfplumber
from rag_kb.models import Document
from rag_kb.parsers.base import BaseParser


class PDFPlumberParser(BaseParser):
    """PDF parser using pdfplumber with table extraction support."""
    
    supported_ext = ('.pdf',)

    def parse(self, path: Path) -> Document:
        """Parse PDF file and return Document with table content."""
        parts = []
        tables_md = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ''
                parts.append(text)
                for table in (page.extract_tables() or []):
                    rows = ['| ' + ' | '.join(str(c or '') for c in row) + ' |' for row in table]
                    tables_md.append('\n'.join(rows))
        content = '\n\n'.join(parts)
        if tables_md:
            content += '\n\n## Tables\n' + '\n\n'.join(tables_md)
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return Document(
            doc_id=file_hash[:16],
            title=path.stem,
            source=str(path),
            content=content,
            metadata={'pages': len(pdf.pages), 'parser': 'pdfplumber', 'tables': len(tables_md)},
            file_hash=file_hash,
        )