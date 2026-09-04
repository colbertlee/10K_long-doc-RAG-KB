"""Markdown file parser."""

import hashlib
from pathlib import Path

from rag_kb.models import Document
from rag_kb.parsers.base import BaseParser


class MarkdownParser(BaseParser):
    """Markdown file parser for .md files."""
    
    supported_ext = ('.md', '.markdown')

    def parse(self, path: Path) -> Document:
        """Parse markdown file and return Document with structure preservation."""
        content = path.read_text(encoding='utf-8')
        
        # Analyze structure
        lines = content.split('\n')
        metadata = {
            'parser': 'markdown',
            'lines': len(lines),
            'structure_preserved': True,
            'has_headings': False,
            'has_lists': False,
            'has_tables': False,
            'has_code_blocks': False
        }
        
        for line in lines:
            # Check for headings
            if line.startswith('#'):
                metadata['has_headings'] = True
            # Check for lists
            if line.strip().startswith(('-', '*', '+', '•')) or (line.strip() and line.strip()[0].isdigit() and line.strip()[1] in '.'):
                metadata['has_lists'] = True
            # Check for tables
            if '|' in line and line.strip().startswith('|'):
                metadata['has_tables'] = True
            # Check for code blocks
            if line.strip().startswith('```') or line.strip().startswith('    '):
                metadata['has_code_blocks'] = True
        
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        return Document(
            doc_id=file_hash[:16],
            title=path.stem,
            source=str(path),
            content=content,
            metadata=metadata,
            file_hash=file_hash,
        )