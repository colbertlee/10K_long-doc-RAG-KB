"""Basic multimodal support for image and table processing."""

from typing import Dict, Any, List, Optional, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json


class ModalityType(Enum):
    """Types of multimodal content."""
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"
    CHART = "chart"
    DIAGRAM = "diagram"


@dataclass
class MultimodalContent:
    """Multimodal content data structure."""
    content_id: str
    modality_type: ModalityType
    source_file: str
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    text_description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'content_id': self.content_id,
            'modality_type': self.modality_type.value,
            'source_file': self.source_file,
            'extracted_data': self.extracted_data,
            'text_description': self.text_description,
            'metadata': self.metadata
        }


class ImageProcessor:
    """Basic image processor for multimodal support."""
    
    def __init__(self):
        """Initialize image processor."""
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    
    def can_process(self, file_path: str) -> bool:
        """Check if file can be processed as image.
        
        Args:
            file_path: File path
            
        Returns:
            True if processable
        """
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def extract_image_info(self, file_path: str) -> Dict[str, Any]:
        """Extract basic image information.
        
        Args:
            file_path: Image file path
            
        Returns:
            Image information
        """
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                return {
                    'format': img.format,
                    'size': img.size,
                    'mode': img.mode,
                    'width': img.width,
                    'height': img.height
                }
        except ImportError:
            # Fallback if PIL not available
            return {
                'format': 'unknown',
                'size': (0, 0),
                'mode': 'unknown',
                'width': 0,
                'height': 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'format': 'error',
                'size': (0, 0)
            }
    
    def generate_image_description(self, file_path: str) -> str:
        """Generate text description for image.
        
        Args:
            file_path: Image file path
            
        Returns:
            Text description
        """
        # In a real implementation, you'd use a vision model
        # For now, return a placeholder
        info = self.extract_image_info(file_path)
        
        if 'error' in info:
            return f"Unable to process image: {info['error']}"
        
        return f"Image file with format {info.get('format', 'unknown')}, size {info.get('size', 'unknown')}"


class TableProcessor:
    """Basic table processor for multimodal support."""
    
    def __init__(self):
        """Initialize table processor."""
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.tsv']
    
    def can_process(self, file_path: str) -> bool:
        """Check if file can be processed as table.
        
        Args:
            file_path: File path
            
        Returns:
            True if processable
        """
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def extract_table_data(self, file_path: str) -> Dict[str, Any]:
        """Extract table data from file.
        
        Args:
            file_path: Table file path
            
        Returns:
            Table data
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                return self._extract_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                return self._extract_excel(file_path)
            else:
                return {'error': f'Unsupported format: {file_ext}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_csv(self, file_path: str) -> Dict[str, Any]:
        """Extract data from CSV file.
        
        Args:
            file_path: CSV file path
            
        Returns:
            Table data
        """
        import csv
        
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
        
        return {
            'format': 'csv',
            'rows': len(rows),
            'columns': len(rows[0]) if rows else 0,
            'headers': rows[0] if rows else [],
            'data': rows[1:] if rows else []
        }
    
    def _extract_excel(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Excel file.
        
        Args:
            file_path: Excel file path
            
        Returns:
            Table data
        """
        try:
            import openpyxl
            
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            data = []
            for row in ws.iter_rows(values_only=True):
                data.append([str(cell) if cell is not None else '' for cell in row])
            
            return {
                'format': 'excel',
                'rows': len(data),
                'columns': len(data[0]) if data else 0,
                'headers': data[0] if data else [],
                'data': data[1:] if data else []
            }
        except ImportError:
            return {'error': 'openpyxl not available for Excel processing'}
        except Exception as e:
            return {'error': str(e)}
    
    def generate_table_description(self, file_path: str) -> str:
        """Generate text description for table.
        
        Args:
            file_path: Table file path
            
        Returns:
            Text description
        """
        table_data = self.extract_table_data(file_path)
        
        if 'error' in table_data:
            return f"Unable to process table: {table_data['error']}"
        
        return f"Table with {table_data.get('rows', 0)} rows and {table_data.get('columns', 0)} columns"


class MultimodalManager:
    """Manager for multimodal content processing."""
    
    def __init__(self):
        """Initialize multimodal manager."""
        from rag_kb.config import settings
        self.multimodal_file = settings.data_dir / 'multimodal_index.json'
        self.content_index: Dict[str, MultimodalContent] = {}
        self.image_processor = ImageProcessor()
        self.table_processor = TableProcessor()
        self._load_index()
    
    def _load_index(self):
        """Load multimodal content index from file."""
        if self.multimodal_file.exists():
            try:
                with open(self.multimodal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for content_id, content_data in data.get('content', {}).items():
                        self.content_index[content_id] = self._dict_to_content(content_data)
            except Exception as e:
                print(f"Error loading multimodal index: {e}")
    
    def _save_index(self):
        """Save multimodal content index to file."""
        try:
            data = {
                'content': {
                    content_id: content.to_dict()
                    for content_id, content in self.content_index.items()
                },
                'total_content': len(self.content_index)
            }
            with open(self.multimodal_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving multimodal index: {e}")
    
    def _dict_to_content(self, data: Dict[str, Any]) -> MultimodalContent:
        """Convert dictionary to content object."""
        return MultimodalContent(
            content_id=data['content_id'],
            modality_type=ModalityType(data['modality_type']),
            source_file=data['source_file'],
            extracted_data=data.get('extracted_data', {}),
            text_description=data.get('text_description', ''),
            metadata=data.get('metadata', {})
        )
    
    def process_multimodal_file(self, file_path: str, doc_id: str = None) -> Dict[str, Any]:
        """Process a multimodal file.
        
        Args:
            file_path: File path
            doc_id: Associated document ID
            
        Returns:
            Processing result
        """
        import uuid
        
        # Determine modality type
        if self.image_processor.can_process(file_path):
            modality_type = ModalityType.IMAGE
            processor = self.image_processor
        elif self.table_processor.can_process(file_path):
            modality_type = ModalityType.TABLE
            processor = self.table_processor
        else:
            return {
                'success': False,
                'error': 'Unsupported file type for multimodal processing'
            }
        
        # Extract data
        extracted_data = processor.extract_image_info(file_path) if modality_type == ModalityType.IMAGE else processor.extract_table_data(file_path)
        
        # Generate description
        text_description = processor.generate_image_description(file_path) if modality_type == ModalityType.IMAGE else processor.generate_table_description(file_path)
        
        # Create content object
        content = MultimodalContent(
            content_id=f"content_{uuid.uuid4().hex[:8]}",
            modality_type=modality_type,
            source_file=file_path,
            extracted_data=extracted_data,
            text_description=text_description,
            metadata={
                'doc_id': doc_id,
                'processed_at': self._get_timestamp()
            }
        )
        
        self.content_index[content.content_id] = content
        self._save_index()
        
        return {
            'success': True,
            'content_id': content.content_id,
            'modality_type': modality_type.value,
            'description': text_description,
            'extracted_data': extracted_data
        }
    
    def search_multimodal_content(self, query: str, modality_type: str = None) -> List[Dict[str, Any]]:
        """Search multimodal content by description.
        
        Args:
            query: Search query
            modality_type: Filter by modality type (optional)
            
        Returns:
            Matching content items
        """
        query_lower = query.lower()
        
        results = []
        for content in self.content_index.values():
            # Filter by modality type if specified
            if modality_type and content.modality_type.value != modality_type:
                continue
            
            # Search in description
            if query_lower in content.text_description.lower():
                results.append(content.to_dict())
        
        return results
    
    def get_content_by_type(self, modality_type: str) -> List[Dict[str, Any]]:
        """Get all content of a specific type.
        
        Args:
            modality_type: Modality type
            
        Returns:
            Content items of specified type
        """
        return [
            content.to_dict()
            for content in self.content_index.values()
            if content.modality_type.value == modality_type
        ]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
multimodal_manager = MultimodalManager()