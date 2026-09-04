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
        """Parse PDF file and return Document with enhanced structure extraction."""
        parts = []
        tables_md = []
        metadata = {
            'parser': 'pdfplumber',
            'tables': 0,
            'structure_preserved': True,
            'has_headings': False,
            'has_lists': False
        }
        
        with pdfplumber.open(path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ''
                
                # Enhanced structure detection
                lines = text.split('\n')
                structured_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Detect potential headings (all caps, centered, or larger font hints)
                    if self._is_heading(line):
                        structured_lines.append(f"## {line}")
                        metadata['has_headings'] = True
                    # Detect list items (bullet points, numbered lists)
                    elif self._is_list_item(line):
                        structured_lines.append(f"- {line}")
                        metadata['has_lists'] = True
                    else:
                        structured_lines.append(line)
                
                page_content = '\n'.join(structured_lines)
                parts.append(f"[Page {page_num}]\n{page_content}")
                
                # Extract tables with markdown format
                for table in (page.extract_tables() or []):
                    rows = ['| ' + ' | '.join(str(c or '') for c in row) + ' |' for row in table]
                    tables_md.append(f"\n\n## Table on Page {page_num}\n" + '\n'.join(rows))
                    metadata['tables'] += 1
        
        content = '\n\n'.join(parts)
        if tables_md:
            content += '\n\n'.join(tables_md)
        
        metadata['pages'] = len(pdf.pages)
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        return Document(
            doc_id=file_hash[:16],
            title=path.stem,
            source=str(path),
            content=content,
            metadata=metadata,
            file_hash=file_hash,
        )
    
    def _is_heading(self, line: str) -> bool:
        """Detect if a line is likely a heading."""
        # Simple heuristics for heading detection
        if len(line) < 5:  # Too short to be a heading
            return False
        if len(line) > 100:  # Too long to be a heading
            return False
        
        # All caps
        if line.isupper() and len(line.split()) >= 2:
            return True
        
        # Title case with common words
        title_case_words = ['Chapter', 'Section', 'Part', 'Introduction', 'Conclusion', 'Summary']
        if any(word in line for word in title_case_words):
            return True
        
        # Numbered pattern (1., 2., etc.)
        if line[0].isdigit() and (line[1] == '.' or line[1] == ' '):
            return True
        
        return False
    
    def _is_list_item(self, line: str) -> bool:
        """Detect if a line is a list item."""
        # Bullet points
        if line.startswith(('•', '-', '*', '○', '●')):
            return True
        
        # Numbered lists
        if line[0].isdigit() and (line[1] == '.' or line[1] == ')'):
            return True
        
        # Lettered lists (a., b., etc.)
        if len(line) > 2 and line[0].isalpha() and line[1] == '.':
            return True
        
        return False