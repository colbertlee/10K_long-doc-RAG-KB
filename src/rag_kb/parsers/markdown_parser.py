"""Markdown file parser."""

import hashlib
from pathlib import Path
from rag_kb.models import Document
from rag_kb.parsers.base import BaseParser


class MarkdownParser(BaseParser):
    """Markdown file parser for .md files."""
    
    supported_ext = ('.md', '.markdown')

    def parse(self, path: Path) -> Document:
        """Parse markdown file and return Document."""
        content = path.read_text(encoding='utf-8')
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return Document(
            doc_id=file_hash[:16],
            title=path.stem,
            source=str(path),
            content=content,
            metadata={'parser': 'markdown', 'lines': len(content.splitlines())},
            file_hash=file_hash,
        )