"""PyMuPDF-based PDF parser with OCR support."""

import hashlib
from pathlib import Path
import fitz  # PyMuPDF
from rag_kb.models import Document
from rag_kb.parsers.base import BaseParser


class PyMuPDFParser(BaseParser):
    """PDF parser using PyMuPDF (fitz) with OCR support for scanned documents."""
    
    supported_ext = ('.pdf',)

    def parse(self, path: Path) -> Document:
        """Parse PDF file and return Document with OCR support."""
        doc = fitz.open(path)
        
        # First try normal text extraction
        parts = []
        total_text_length = 0
        
        for page in doc:
            text = page.get_text()
            parts.append(text)
            total_text_length += len(text)
        
        content = '\n\n'.join(parts)
        
        # Check if the PDF might be scanned (very little text extracted)
        # If average text per page is less than 100 characters, it's likely scanned
        avg_text_per_page = total_text_length / len(doc) if len(doc) > 0 else 0
        
        if avg_text_per_page < 100:
            print(f"Detected scanned PDF (avg {avg_text_per_page:.1f} chars/page), applying OCR...")
            content = self._apply_ocr(doc)
        
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return Document(
            doc_id=file_hash[:16],
            title=path.stem,
            source=str(path),
            content=content,
            metadata={'pages': len(doc), 'parser': 'pymupdf', 'ocr_used': avg_text_per_page < 100},
            file_hash=file_hash,
        )
    
    def _apply_ocr(self, doc) -> str:
        """Apply OCR to extract text from scanned PDF pages."""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            ocr_parts = []
            
            for page_num, page in enumerate(doc):
                # Render page to image
                pix = page.get_pixmap(dpi=300)  # Higher DPI for better OCR
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Apply OCR
                try:
                    text = pytesseract.image_to_string(img, lang='chi_sim+eng')  # Chinese and English
                    if text.strip():
                        ocr_parts.append(text)
                        print(f"OCR completed for page {page_num + 1}: {len(text)} characters")
                    else:
                        print(f"OCR returned no text for page {page_num + 1}")
                except Exception as e:
                    print(f"OCR failed for page {page_num + 1}: {e}")
                    # Fallback to basic text extraction
                    ocr_parts.append(page.get_text())
            
            ocr_content = '\n\n'.join(ocr_parts)
            
            if not ocr_content.strip():
                print("OCR failed to extract any text, falling back to basic extraction")
                # Final fallback
                ocr_content = '\n\n'.join([page.get_text() for page in doc])
            
            return ocr_content
            
        except ImportError:
            print("OCR libraries not available, falling back to basic text extraction")
            return '\n\n'.join([page.get_text() for page in doc])
        except Exception as e:
            print(f"OCR processing failed: {e}, falling back to basic extraction")
            return '\n\n'.join([page.get_text() for page in doc])