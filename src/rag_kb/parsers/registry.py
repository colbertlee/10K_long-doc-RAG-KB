"""Parser registry for managing document parsers."""

from rag_kb.parsers.pdf_pymupdf import PyMuPDFParser
from rag_kb.parsers.pdf_pdfplumber import PDFPlumberParser

PARSER_REGISTRY = [PyMuPDFParser(), PDFPlumberParser()]