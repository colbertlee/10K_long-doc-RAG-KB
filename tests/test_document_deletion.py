"""Unit tests for document deletion functionality."""

import pytest
import json
from pathlib import Path
import tempfile
import shutil


def delete_document_logic(doc_id: str, data_dir: Path):
    """Core logic for deleting a document (copied for testing).
    
    Args:
        doc_id: Document ID to delete
        data_dir: Data directory path
        
    Returns:
        Deletion result dictionary
    """
    try:
        # Check for document registry
        registry_file = data_dir / 'document_registry.json'
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            if doc_id in registry:
                # Remove from registry
                doc_info = registry.pop(doc_id)
                
                # Delete the actual file if it exists
                if 'source' in doc_info:
                    file_path = Path(doc_info['source'])
                    if file_path.exists():
                        file_path.unlink()
                
                # Update registry file
                with open(registry_file, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, ensure_ascii=False, indent=2)
                
                return {
                    'success': True,
                    'message': f'Document {doc_id} deleted successfully',
                    'doc_id': doc_id
                }
            else:
                return {
                    'success': False,
                    'message': f'Document {doc_id} not found in registry'
                }
        else:
            # Fallback to uploaded files directory
            upload_dir = data_dir / 'uploads'
            
            # Try to find and delete the file
            for ext in ['.pdf', '.docx', '.md', '.txt', '.html']:
                potential_file = upload_dir / f'{doc_id}{ext}'
                if potential_file.exists():
                    potential_file.unlink()
                    return {
                        'success': True,
                        'message': f'Document {doc_id} deleted successfully',
                        'doc_id': doc_id
                    }
            
            return {
                'success': False,
                'message': f'Document {doc_id} not found'
            }
    except Exception as e:
        return {'error': str(e), 'message': f'Failed to delete document {doc_id}'}


class TestDocumentDeletionLogic:
    """Test suite for document deletion logic (unit tests)."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_document_registry(self, temp_data_dir):
        """Create a sample document registry for testing."""
        registry = {
            "test_doc_1": {
                "doc_id": "test_doc_1",
                "title": "Test Document 1",
                "source": str(temp_data_dir / "uploads" / "test_doc_1.txt"),
                "import_type": "upload",
                "timestamp": "2026-08-26 10:00:00"
            },
            "test_doc_2": {
                "doc_id": "test_doc_2", 
                "title": "Test Document 2",
                "source": str(temp_data_dir / "uploads" / "test_doc_2.txt"),
                "import_type": "upload",
                "timestamp": "2026-08-26 10:05:00"
            }
        }
        
        # Create uploads directory and test files
        uploads_dir = temp_data_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        for doc_id, doc_data in registry.items():
            file_path = Path(doc_data["source"])
            file_path.write_text(f"Content for {doc_id}")
        
        # Write registry file
        registry_file = temp_data_dir / "document_registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        
        return registry, registry_file, uploads_dir
    
    def test_delete_existing_document_from_registry(self, sample_document_registry):
        """Test deleting an existing document from the registry."""
        registry, registry_file, uploads_dir = sample_document_registry
        
        # Delete the first document
        result = delete_document_logic("test_doc_1", uploads_dir.parent)
        
        # Verify the result
        assert result["success"] is True
        assert result["doc_id"] == "test_doc_1"
        assert "deleted successfully" in result["message"]
        
        # Verify the document was removed from registry
        with open(registry_file, 'r', encoding='utf-8') as f:
            updated_registry = json.load(f)
        
        assert "test_doc_1" not in updated_registry
        assert "test_doc_2" in updated_registry  # Other document should remain
        
        # Verify the file was deleted
        assert not (uploads_dir / "test_doc_1.txt").exists()
        assert (uploads_dir / "test_doc_2.txt").exists()  # Other file should remain
    
    def test_delete_nonexistent_document(self, sample_document_registry):
        """Test attempting to delete a document that doesn't exist."""
        registry, registry_file, uploads_dir = sample_document_registry
        
        # Try to delete a non-existent document
        result = delete_document_logic("nonexistent_doc", uploads_dir.parent)
        
        # Verify the result
        assert result["success"] is False
        assert "not found" in result["message"].lower()
        
        # Verify the registry was not modified
        with open(registry_file, 'r', encoding='utf-8') as f:
            updated_registry = json.load(f)
        
        assert len(updated_registry) == 2  # Should still have 2 documents
    
    def test_delete_document_without_registry(self, temp_data_dir):
        """Test deletion when registry file doesn't exist (fallback mode)."""
        # Create uploads directory with test files
        uploads_dir = temp_data_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        test_file = uploads_dir / "fallback_test.txt"
        test_file.write_text("Fallback test content")
        
        # Try to delete using file stem as doc_id
        result = delete_document_logic("fallback_test", temp_data_dir)
        
        # Verify the result
        assert result["success"] is True
        assert "deleted successfully" in result["message"]
        
        # Verify the file was deleted
        assert not test_file.exists()
    
    def test_delete_document_file_not_found_in_fallback(self, temp_data_dir):
        """Test fallback deletion when file doesn't exist."""
        uploads_dir = temp_data_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to delete a file that doesn't exist
        result = delete_document_logic("nonexistent_file", temp_data_dir)
        
        # Verify the result
        assert result["success"] is False
        assert "not found" in result["message"].lower()
    
    def test_delete_document_with_various_extensions(self, temp_data_dir):
        """Test deletion handles different file extensions correctly."""
        uploads_dir = temp_data_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files with different extensions
        test_files = [
            uploads_dir / "test.pdf",
            uploads_dir / "test.docx", 
            uploads_dir / "test.md",
            uploads_dir / "test.txt"
        ]
        
        for test_file in test_files:
            test_file.write_text("Test content")
        
        # Delete each file
        for test_file in test_files:
            doc_id = test_file.stem
            result = delete_document_logic(doc_id, temp_data_dir)
            assert result["success"] is True
            assert not test_file.exists()
    
    def test_delete_document_preserves_other_data(self, sample_document_registry):
        """Test that deleting one document doesn't affect other documents."""
        registry, registry_file, uploads_dir = sample_document_registry
        
        # Delete one document
        delete_document_logic("test_doc_1", uploads_dir.parent)
        
        # Verify the other document is intact
        with open(registry_file, 'r', encoding='utf-8') as f:
            updated_registry = json.load(f)
        
        assert "test_doc_2" in updated_registry
        assert updated_registry["test_doc_2"]["title"] == "Test Document 2"
        assert (uploads_dir / "test_doc_2.txt").exists()
        assert (uploads_dir / "test_doc_2.txt").read_text() == "Content for test_doc_2"
    
    def test_delete_document_empty_registry(self, temp_data_dir):
        """Test deletion when registry is empty."""
        # Create empty registry
        registry_file = temp_data_dir / "document_registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        
        result = delete_document_logic("any_doc", temp_data_dir)
        
        # Should fail since document doesn't exist in empty registry
        assert result["success"] is False
        assert "not found" in result["message"].lower()
    
    def test_delete_document_registry_corrupted(self, temp_data_dir):
        """Test deletion when registry file is corrupted."""
        # Create corrupted registry file
        registry_file = temp_data_dir / "document_registry.json"
        registry_file.write_text("invalid json content")
        
        result = delete_document_logic("any_doc", temp_data_dir)
        
        # Should handle error gracefully
        # When there's an error, the function returns {'error': ..., 'message': ...}
        # instead of {'success': False, ...}
        assert "error" in result or "success" in result
        if "success" in result:
            assert result["success"] is False
        if "error" in result:
            assert "failed" in result["message"].lower()


class TestDocumentListUpdate:
    """Test suite for document list updates after deletion."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_documents(self, temp_data_dir):
        """Create sample documents for testing."""
        registry = {
            "doc_1": {
                "doc_id": "doc_1",
                "title": "Document 1",
                "source": str(temp_data_dir / "uploads" / "doc_1.txt"),
                "import_type": "upload",
                "timestamp": "2026-08-26 10:00:00"
            },
            "doc_2": {
                "doc_id": "doc_2",
                "title": "Document 2", 
                "source": str(temp_data_dir / "uploads" / "doc_2.txt"),
                "import_type": "upload",
                "timestamp": "2026-08-26 10:05:00"
            },
            "doc_3": {
                "doc_id": "doc_3",
                "title": "Document 3",
                "source": str(temp_data_dir / "uploads" / "doc_3.txt"),
                "import_type": "folder",
                "timestamp": "2026-08-26 10:10:00"
            }
        }
        
        uploads_dir = temp_data_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        for doc_data in registry.values():
            file_path = Path(doc_data["source"])
            file_path.write_text(f"Content for {doc_data['doc_id']}")
        
        registry_file = temp_data_dir / "document_registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        
        return registry, registry_file
    
    def test_get_documents_after_deletion(self, sample_documents):
        """Test that document list is updated after deletion."""
        registry, registry_file = sample_documents
        
        # Get initial document count
        with open(registry_file, 'r', encoding='utf-8') as f:
            initial_registry = json.load(f)
        initial_count = len(initial_registry)
        assert initial_count == 3
        
        # Delete one document
        delete_document_logic("doc_2", registry_file.parent)
        
        # Get updated document count
        with open(registry_file, 'r', encoding='utf-8') as f:
            updated_registry = json.load(f)
        updated_count = len(updated_registry)
        assert updated_count == 2
        
        # Verify the deleted document is not in the list
        assert "doc_2" not in updated_registry
        assert "doc_1" in updated_registry
        assert "doc_3" in updated_registry
    
    def test_get_documents_filters_by_import_type(self, sample_documents):
        """Test that documents are correctly filtered by import type."""
        registry, registry_file = sample_documents
        
        # Get documents from registry
        with open(registry_file, 'r', encoding='utf-8') as f:
            documents = list(json.load(f).values())
        
        upload_docs = [doc for doc in documents if doc["import_type"] == "upload"]
        folder_docs = [doc for doc in documents if doc["import_type"] == "folder"]
        
        assert len(upload_docs) == 2
        assert len(folder_docs) == 1
        assert folder_docs[0]["doc_id"] == "doc_3"


class TestDocumentDeletionIntegration:
    """Integration tests for document deletion workflow."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_full_deletion_workflow(self, temp_data_dir):
        """Test complete workflow: create, list, delete, verify."""
        # Setup: Create initial documents
        registry = {
            "workflow_doc_1": {
                "doc_id": "workflow_doc_1",
                "title": "Workflow Test 1",
                "source": str(temp_data_dir / "uploads" / "workflow_doc_1.txt"),
                "import_type": "upload",
                "timestamp": "2026-08-26 10:00:00"
            }
        }
        
        uploads_dir = temp_data_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = Path(registry["workflow_doc_1"]["source"])
        file_path.write_text("Workflow test content")
        
        registry_file = temp_data_dir / "document_registry.json"
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        
        # Step 1: Verify document exists
        with open(registry_file, 'r', encoding='utf-8') as f:
            initial_registry = json.load(f)
        assert len(initial_registry) == 1
        assert "workflow_doc_1" in initial_registry
        
        # Step 2: Delete the document
        delete_result = delete_document_logic("workflow_doc_1", temp_data_dir)
        assert delete_result["success"] is True
        
        # Step 3: Verify document is gone from list
        with open(registry_file, 'r', encoding='utf-8') as f:
            final_registry = json.load(f)
        assert len(final_registry) == 0
        
        # Step 4: Verify file is deleted
        assert not file_path.exists()
        
        # Step 5: Verify registry is empty
        with open(registry_file, 'r', encoding='utf-8') as f:
            final_registry = json.load(f)
        assert len(final_registry) == 0