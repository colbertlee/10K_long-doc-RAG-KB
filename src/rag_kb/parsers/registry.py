"""Parser registry for managing document parsers."""

from rag_kb.parsers.docx_parser import DocxParser
from rag_kb.parsers.markdown_parser import MarkdownParser
from rag_kb.parsers.pdf_pdfplumber import PDFPlumberParser
from rag_kb.parsers.pdf_pymupdf import PyMuPDFParser
from rag_kb.parsers.text_parser import TextParser

PARSER_REGISTRY = [
    PyMuPDFParser(), 
    PDFPlumberParser(),
    DocxParser(),
    TextParser(),
    MarkdownParser()
]