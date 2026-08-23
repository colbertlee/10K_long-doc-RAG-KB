"""API routes for RAG KB."""

import json
import re
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.ingest.user_manager import UserDataManager
from rag_kb.config import settings
from rag_kb.utils.validation import validate_user_id, validate_kb_name, get_current_user
from rag_kb.api.advanced_filters import AdvancedFilter, FilterBuilder
from rag_kb.api.feedback import FeedbackCollector, FeedbackAnalyzer
from rag_kb.knowledge.organization import SmartKnowledgeOrganizer, KnowledgeQualityAnalyzer
from rag_kb.knowledge.batch_operations import BatchKnowledgeOperations

router = APIRouter()
rag = LightRAGAdapter()
user_manager = UserDataManager(settings.data_dir / "users")
advanced_filter = AdvancedFilter()
feedback_collector = FeedbackCollector(settings.data_dir / "feedback")
feedback_analyzer = FeedbackAnalyzer(feedback_collector)
knowledge_organizer = SmartKnowledgeOrganizer()
quality_analyzer = KnowledgeQualityAnalyzer()


@router.get('/current-user')
async def get_current_user_endpoint():
    """Get current logged-in user ID.
    
    Returns:
        Current user information
    """
    current_user = get_current_user()
    return {
        "user_id": current_user,
        "authenticated": current_user != "default"
    }


def extract_sources(answer):
    """Extract source citations from LightRAG answer.
    
    Args:
        answer: Answer text from LightRAG
        
    Returns:
        List of source citations
    """
    # Simple example: match patterns like [DATA:...]
    return re.findall(r'\[DATA:([^\]]+)\]', answer)


@router.post('/chat/completions')
async def chat_completions(body: dict):
    """OpenAI-compatible chat completions endpoint.
    
    Args:
        body: Request body with messages and parameters
        
    Returns:
        Response with answer and sources
    """
    question = body['messages'][-1]['content']
    mode = body.get('mode', 'hybrid')
    
    # Extract user roles for ACL filtering
    user_roles = body.get('user_roles', {})
    if not user_roles:
        # Default to internal access if no roles specified
        user_roles = {'level': ['Internal']}
    
    try:
        # Use async query to avoid event loop issues
        answer = await rag.aquery(question, mode=mode, user_roles=user_roles)
    except Exception as e:
        # Fallback to sync query if async fails
        try:
            answer = rag.query(question, mode=mode, user_roles=user_roles)
        except Exception as e2:
            # Return a simple error response if both fail
            return {'answer': f'Error: {str(e2)}', 'sources': []}
    
    sources = extract_sources(answer)
    
    return {'answer': answer, 'sources': sources}


@router.post('/users/{user_id}/kbs')
async def create_user_kb(user_id: str, kb_name: str = Form(...)):
    """Create a new knowledge base for a user.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        
    Returns:
        Knowledge base creation result
    """
    # Validate inputs
    is_valid_user, user_error = validate_user_id(user_id)
    if not is_valid_user:
        raise HTTPException(status_code=400, detail=f"Invalid user ID: {user_error}")
    
    is_valid_kb, kb_error = validate_kb_name(kb_name)
    if not is_valid_kb:
        raise HTTPException(status_code=400, detail=f"Invalid knowledge base name: {kb_error}")
    
    try:
        kb_path = user_manager.create_user_kb(user_id, kb_name)
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "kb_path": str(kb_path)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/users/{user_id}/kbs')
async def list_user_kbs(user_id: str):
    """List all knowledge bases for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        List of knowledge base names
    """
    try:
        kbs = user_manager.get_user_kbs(user_id)
        return {
            "user_id": user_id,
            "knowledge_bases": kbs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/users/{user_id}/kbs/{kb_name}/upload')
async def upload_to_user_kb(user_id: str, kb_name: str, file: UploadFile = File(...)):
    """Upload a file to a user's knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        file: Uploaded file
        
    Returns:
        Upload result
    """
    try:
        kb_folder = user_manager.get_user_folder(user_id) / kb_name
        raw_folder = kb_folder / "raw"
        raw_folder.mkdir(parents=True, exist_ok=True)
        
        file_path = raw_folder / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "filename": file.filename,
            "file_path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/users/{user_id}/kbs/{kb_name}/ingest')
async def ingest_user_kb(user_id: str, kb_name: str, acl: dict = None):
    """Ingest all documents from a user's knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        acl: Access control list metadata
        
    Returns:
        Ingestion result
    """
    try:
        documents = user_manager.ingest_user_folder(user_id, kb_name, acl)
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "documents_processed": len(documents),
            "documents": [doc.metadata for doc in documents]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/users/{user_id}/kbs/{kb_name}/stats')
async def get_kb_stats(user_id: str, kb_name: str):
    """Get statistics for a user's knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        
    Returns:
        Knowledge base statistics
    """
    try:
        stats = user_manager.get_kb_stats(user_id, kb_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/users/{user_id}/kbs/{kb_name}')
async def delete_user_kb(user_id: str, kb_name: str):
    """Delete a user's knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        
    Returns:
        Deletion result
    """
    try:
        success = user_manager.delete_user_kb(user_id, kb_name)
        return {
            "success": success,
            "user_id": user_id,
            "kb_name": kb_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/users/{user_id}/kbs/{kb_name}/import-folder')
async def import_folder(user_id: str, kb_name: str, folder_path: str, acl: dict = None):
    """Import entire folder to knowledge base.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        folder_path: Path to local folder to import
        acl: Access control list metadata
        
    Returns:
        Import result with statistics
    """
    try:
        from pathlib import Path
        import shutil
        
        folder = Path(folder_path)
        if not folder.exists():
            raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
        
        if not folder.is_dir():
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {folder_path}")
        
        # Get user knowledge base folder
        kb_folder = user_manager.get_user_folder(user_id) / kb_name
        raw_folder = kb_folder / "raw"
        raw_folder.mkdir(parents=True, exist_ok=True)
        
        # Process files
        documents = []
        skipped_files = []
        failed_files = []
        
        for file_path in folder.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    # Check if file already exists
                    target_path = raw_folder / file_path.name
                    if target_path.exists():
                        skipped_files.append(file_path.name)
                        continue
                    
                    # Copy file to user knowledge base
                    shutil.copy2(file_path, target_path)
                    
                    # Process document
                    doc = user_manager.pipeline.run(target_path, acl=acl)
                    documents.append(doc)
                    
                except Exception as e:
                    failed_files.append({
                        "file": file_path.name,
                        "error": str(e)
                    })
        
        return {
            "success": True,
            "user_id": user_id,
            "kb_name": kb_name,
            "source_folder": str(folder),
            "total_files_found": len(list(folder.rglob('*'))),
            "files_processed": len(documents),
            "files_skipped": len(skipped_files),
            "files_failed": len(failed_files),
            "documents": [doc.metadata for doc in documents],
            "skipped_files": skipped_files,
            "failed_files": failed_files
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/advanced-search')
async def advanced_search(search_request: dict):
    """Advanced search with filtering capabilities.
    
    Args:
        search_request: Dictionary containing:
            - query: Search query string
            - mode: Search mode (hybrid/naive/local/global)
            - filters: Advanced filters (time_range, document_type, etc.)
            - user_roles: User roles for ACL filtering
            
    Returns:
        Search results with applied filters
    """
    try:
        query = search_request.get('query', '')
        mode = search_request.get('mode', 'hybrid')
        filters = search_request.get('filters', {})
        user_roles = search_request.get('user_roles', {'level': ['Internal']})
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Perform initial search
        if not user_roles:
            user_roles = {'level': ['Internal']}
        
        try:
            # Use async query to avoid event loop issues
            answer = await rag.aquery(query, mode=mode, user_roles=user_roles)
        except Exception as e:
            # Fallback to sync query if async fails
            try:
                answer = rag.query(query, mode=mode, user_roles=user_roles)
            except Exception as e2:
                # Return a simple error response if both fail
                return {'answer': f'Error: {str(e2)}', 'sources': []}
        
        # Parse sources from answer
        sources = extract_sources(answer)
        
        # Apply advanced filters if provided
        if filters and sources:
            # Convert sources to SearchResult format for filtering
            from rag_kb.models import SearchResult
            search_results = []
            for source in sources:
                search_result = SearchResult(
                    content=answer,  # Use the full answer as content
                    metadata=source,
                    score=source.get('score', 0.0)
                )
                search_results.append(search_result)
            
            # Apply filters
            filtered_results = advanced_filter.apply_filters(search_results, filters)
            
            # Convert back to source format
            filtered_sources = [result.metadata for result in filtered_results]
        else:
            filtered_sources = sources
        
        return {
            'answer': answer,
            'sources': filtered_sources,
            'total_sources': len(filtered_sources),
            'filters_applied': list(filters.keys()) if filters else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/import-local-folder')
async def import_local_folder_simple(folder_path: str, user_id: str = "default", kb_name: str = "default", acl: dict = None):
    """Simple endpoint to import local folder without requiring user/kb creation first.
    
    Args:
        folder_path: Path to local folder to import
        user_id: User identifier (default: "default")
        kb_name: Knowledge base name (default: "default")
        acl: Access control list metadata
        
    Returns:
        Import result
    """
    try:
        # Auto-create user and KB if they don't exist
        user_manager.create_user_kb(user_id, kb_name)
        
        # Import folder
        return await import_folder(user_id, kb_name, folder_path, acl)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/users/{user_id}/kbs/{kb_name}/graph')
async def get_knowledge_graph(user_id: str, kb_name: str):
    """Get knowledge graph data for visualization.
    
    Args:
        user_id: User identifier
        kb_name: Knowledge base name
        
    Returns:
        Graph data with nodes and edges
    """
    try:
        # Get the knowledge base directory
        kb_folder = user_manager.get_user_folder(user_id) / kb_name
        graph_file = kb_folder / "graph_data.json"
        
        # Check if cached graph data exists
        if graph_file.exists():
            import json
            with open(graph_file, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            return graph_data
        else:
            # Try to extract from LightRAG using the new graph extractor
            try:
                from rag_kb.lightrag.graph_extractor import LightRAGGraphExtractor
                
                # Look for LightRAG working directory
                lightrag_dir = kb_folder / "index"
                if not lightrag_dir.exists():
                    lightrag_dir = kb_folder  # Fallback to KB folder
                
                if lightrag_dir.exists():
                    # Extract graph data using the new extractor
                    extractor = LightRAGGraphExtractor(lightrag_dir)
                    graph_data = extractor.get_graph_data()
                    
                    # Cache the extracted data
                    extractor.save_graph_data(graph_file)
                    
                    # Add statistics
                    stats = extractor.get_statistics()
                    graph_data['statistics'] = stats
                    
                    return graph_data
                
                # Return empty graph if no data found
                return {
                    "nodes": [],
                    "edges": [],
                    "statistics": {
                        "total_nodes": 0,
                        "total_edges": 0,
                        "node_types": {},
                        "relation_types": {},
                        "avg_degree": 0,
                        "connected_components": 0
                    },
                    "message": "没有找到知识图谱数据。请先导入文档以生成知识图谱。"
                }
            except ImportError:
                return {
                    "nodes": [],
                    "edges": [],
                    "statistics": {
                        "total_nodes": 0,
                        "total_edges": 0,
                        "node_types": {},
                        "relation_types": {},
                        "avg_degree": 0,
                        "connected_components": 0
                    },
                    "message": "知识图谱可视化需要NetworkX库。请安装: pip install networkx"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/feedback')
async def submit_feedback(feedback_data: dict):
    """Submit user feedback for search results.
    
    Args:
        feedback_data: Dictionary containing:
            - user_id: User identifier
            - query: User query
            - answer: System answer
            - rating: User rating (positive/negative/neutral or 1-5)
            - comment: Optional user comment
            - sources: Source documents
            - search_mode: Search mode used
            
    Returns:
        Feedback submission result
    """
    try:
        success = feedback_collector.add_feedback(feedback_data)
        if success:
            return {
                "success": True,
                "message": "Feedback submitted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to submit feedback")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/feedback/statistics')
async def get_feedback_statistics():
    """Get feedback statistics.
    
    Returns:
        Feedback statistics including total count, positive/negative counts, average rating
    """
    try:
        stats = feedback_collector.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/feedback/analysis')
async def get_feedback_analysis():
    """Get feedback analysis and improvement suggestions.
    
    Returns:
        Analysis results including common issues and improvement suggestions
    """
    try:
        common_issues = feedback_analyzer.identify_common_issues()
        suggestions = feedback_analyzer.suggest_improvements()
        
        return {
            "common_issues": common_issues,
            "improvement_suggestions": suggestions,
            "statistics": feedback_collector.get_statistics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/feedback/recent')
async def get_recent_feedback(limit: int = 50, offset: int = 0):
    """Get recent feedback entries.
    
    Args:
        limit: Maximum number of entries to return
        offset: Number of entries to skip
        
    Returns:
        List of recent feedback entries
    """
    try:
        feedbacks = feedback_collector.get_feedback(limit=limit, offset=offset)
        return {
            "feedbacks": feedbacks,
            "total": len(feedbacks),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
 
 @ r o u t e r . p o s t ( ' / k n o w l e d g e / o r g a n i z e ' ) 
 
 a s y n c   d e f   o r g a n i z e _ d o c u m e n t ( d o c u m e n t _ d a t a :   d i c t ) : 
 
         " " " O r g a n i z e   a   d o c u m e n t   w i t h   a u t o m a t i c   c l a s s i f i c a t i o n   a n d   t a g g i n g . " " " 
 
         t r y : 
 
                 c o n t e n t   =   d o c u m e n t _ d a t a . g e t ( ' c o n t e n t ' ,   ' ' ) 
 
                 f i l e n a m e   =   d o c u m e n t _ d a t a . g e t ( ' f i l e n a m e ' ,   ' ' ) 
 
                 m e t a d a t a   =   d o c u m e n t _ d a t a . g e t ( ' m e t a d a t a ' ,   { } ) 
 
                 
 
                 i f   n o t   c o n t e n t : 
 
                         r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 0 ,   d e t a i l = " C o n t e n t   i s   r e q u i r e d " ) 
 
                 
 
                 o r g a n i z a t i o n   =   k n o w l e d g e _ o r g a n i z e r . o r g a n i z e _ d o c u m e n t ( c o n t e n t ,   f i l e n a m e ) 
 
                 q u a l i t y _ a n a l y s i s   =   q u a l i t y _ a n a l y z e r . a n a l y z e _ d o c u m e n t _ q u a l i t y ( c o n t e n t ,   m e t a d a t a ) 
 
                 
 
                 r e t u r n   { 
 
                         " o r g a n i z a t i o n " :   o r g a n i z a t i o n , 
 
                         " q u a l i t y _ a n a l y s i s " :   q u a l i t y _ a n a l y s i s , 
 
                         " s u g g e s t i o n s " :   q u a l i t y _ a n a l y s i s . g e t ( ' s u g g e s t i o n s ' ,   [ ] ) 
 
                 } 
 
         e x c e p t   E x c e p t i o n   a s   e : 
 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 5 0 0 ,   d e t a i l = s t r ( e ) ) 
 
 
 
 
 
 @ r o u t e r . p o s t ( ' / k n o w l e d g e / b a t c h - o r g a n i z e ' ) 
 
 a s y n c   d e f   b a t c h _ o r g a n i z e _ d o c u m e n t s ( d o c u m e n t s :   l i s t ) : 
 
         " " " B a t c h   o r g a n i z e   m u l t i p l e   d o c u m e n t s . " " " 
 
         t r y : 
 
                 r e s u l t s   =   [ ] 
 
                 f o r   d o c _ d a t a   i n   d o c u m e n t s : 
 
                         t r y : 
 
                                 c o n t e n t   =   d o c _ d a t a . g e t ( ' c o n t e n t ' ,   ' ' ) 
 
                                 f i l e n a m e   =   d o c _ d a t a . g e t ( ' f i l e n a m e ' ,   ' ' ) 
 
                                 m e t a d a t a   =   d o c _ d a t a . g e t ( ' m e t a d a t a ' ,   { } ) 
 
                                 
 
                                 o r g a n i z a t i o n   =   k n o w l e d g e _ o r g a n i z e r . o r g a n i z e _ d o c u m e n t ( c o n t e n t ,   f i l e n a m e ) 
 
                                 q u a l i t y _ a n a l y s i s   =   q u a l i t y _ a n a l y z e r . a n a l y z e _ d o c u m e n t _ q u a l i t y ( c o n t e n t ,   m e t a d a t a ) 
 
                                 
 
                                 r e s u l t s . a p p e n d ( { 
 
                                         " f i l e n a m e " :   f i l e n a m e , 
 
                                         " o r g a n i z a t i o n " :   o r g a n i z a t i o n , 
 
                                         " q u a l i t y _ a n a l y s i s " :   q u a l i t y _ a n a l y s i s , 
 
                                         " s t a t u s " :   " s u c c e s s " 
 
                                 } ) 
 
                         e x c e p t   E x c e p t i o n   a s   e : 
 
                                 r e s u l t s . a p p e n d ( { 
 
                                         " f i l e n a m e " :   d o c _ d a t a . g e t ( ' f i l e n a m e ' ,   ' u n k n o w n ' ) , 
 
                                         " e r r o r " :   s t r ( e ) , 
 
                                         " s t a t u s " :   " f a i l e d " 
 
                                 } ) 
 
                 
 
                 r e t u r n   { 
 
                         " t o t a l " :   l e n ( d o c u m e n t s ) , 
 
                         " s u c c e s s f u l " :   s u m ( 1   f o r   r   i n   r e s u l t s   i f   r [ " s t a t u s " ]   = =   " s u c c e s s " ) , 
 
                         " f a i l e d " :   s u m ( 1   f o r   r   i n   r e s u l t s   i f   r [ " s t a t u s " ]   = =   " f a i l e d " ) , 
 
                         " r e s u l t s " :   r e s u l t s 
 
                 } 
 
         e x c e p t   E x c e p t i o n   a s   e : 
 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 5 0 0 ,   d e t a i l ( s t r ( e ) ) 
 
 
 
 
 
 @ r o u t e r . g e t ( ' / k n o w l e d g e / s t a t i s t i c s ' ) 
 
 a s y n c   d e f   g e t _ k n o w l e d g e _ s t a t i s t i c s ( ) : 
 
         " " " G e t   o v e r a l l   k n o w l e d g e   b a s e   s t a t i s t i c s . " " " 
 
         t r y : 
 
                 s t a t s   =   { 
 
                         " t o t a l _ d o c u m e n t s " :   0 , 
 
                         " p r o c e s s e d _ d o c u m e n t s " :   0 , 
 
                         " c a t e g o r i e s " :   { } , 
 
                         " t a g s " :   { } , 
 
                         " t o t a l _ s i z e " :   0 , 
 
                         " q u a l i t y _ s c o r e s " :   { " a v e r a g e " :   0 . 0 ,   " m i n " :   0 . 0 ,   " m a x " :   0 . 0 } 
 
                 } 
 
                 
 
                 t r y : 
 
                         k b _ s t a t s   =   u s e r _ m a n a g e r . g e t _ k b _ s t a t s ( " d e f a u l t " ,   " d e f a u l t " ) 
 
                         i f   k b _ s t a t s : 
 
                                 s t a t s [ " t o t a l _ d o c u m e n t s " ]   =   k b _ s t a t s . g e t ( " t o t a l _ d o c u m e n t s " ,   0 ) 
 
                                 s t a t s [ " p r o c e s s e d _ d o c u m e n t s " ]   =   k b _ s t a t s . g e t ( " p r o c e s s e d _ d o c u m e n t s " ,   0 ) 
 
                                 s t a t s [ " t o t a l _ s i z e " ]   =   k b _ s t a t s . g e t ( " t o t a l _ s i z e " ,   0 ) 
 
                 e x c e p t : 
 
                         p a s s 
 
                 
 
                 r e t u r n   s t a t s 
 
         e x c e p t   E x c e p t i o n   a s   e : 
 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 5 0 0 ,   d e t a i l ( s t r ( e ) ) 
 
 
 
 
 
 @ r o u t e r . p o s t ( ' / k n o w l e d g e / s u g g e s t - r e l a t e d ' ) 
 
 a s y n c   d e f   s u g g e s t _ r e l a t e d _ d o c u m e n t s ( q u e r y _ d a t a :   d i c t ) : 
 
         " " " S u g g e s t   r e l a t e d   d o c u m e n t s   b a s e d   o n   c o n t e n t   s i m i l a r i t y . " " " 
 
         t r y : 
 
                 d o c _ i d   =   q u e r y _ d a t a . g e t ( ' d o c _ i d ' ) 
 
                 a l l _ d o c s   =   q u e r y _ d a t a . g e t ( ' a l l _ d o c s ' ,   [ ] ) 
 
                 
 
                 i f   n o t   d o c _ i d   o r   n o t   a l l _ d o c s : 
 
                         r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 4 0 0 ,   d e t a i l ( " d o c _ i d   a n d   a l l _ d o c s   a r e   r e q u i r e d " ) ) 
 
                 
 
                 r e l a t e d   =   k n o w l e d g e _ o r g a n i z e r . s u g g e s t _ r e l a t e d _ d o c s ( d o c _ i d ,   a l l _ d o c s ) 
 
                 
 
                 r e t u r n   { 
 
                         " r e l a t e d _ d o c u m e n t s " :   r e l a t e d , 
 
                         " c o u n t " :   l e n ( r e l a t e d ) 
 
                 } 
 
         e x c e p t   E x c e p t i o n   a s   e : 
 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 5 0 0 ,   d e t a i l ( s t r ( e ) ) 
 
 
 
 
 
 @ r o u t e r . p o s t ( ' / k n o w l e d g e / b a t c h - o p e r a t i o n ' ) 
 
 a s y n c   d e f   b a t c h _ k n o w l e d g e _ o p e r a t i o n ( o p e r a t i o n _ d a t a :   d i c t ) : 
 
         " " " P e r f o r m   b a t c h   o p e r a t i o n s   o n   k n o w l e d g e   d o c u m e n t s . " " " 
 
         t r y : 
 
                 f r o m   r a g _ k b . k n o w l e d g e . b a t c h _ o p e r a t i o n s   i m p o r t   B a t c h K n o w l e d g e O p e r a t i o n s 
 
                 
 
                 b a t c h _ o p s   =   B a t c h K n o w l e d g e O p e r a t i o n s ( ) 
 
                 
 
                 o p e r a t i o n   =   o p e r a t i o n _ d a t a . g e t ( ' o p e r a t i o n ' ) 
 
                 d o c u m e n t _ i d s   =   o p e r a t i o n _ d a t a . g e t ( ' d o c u m e n t _ i d s ' ,   [ ] ) 
 
                 p a r a m e t e r s   =   o p e r a t i o n _ d a t a . g e t ( ' p a r a m e t e r s ' ,   { } ) 
 
                 
 
                 r e s u l t   =   b a t c h _ o p s . e x e c u t e _ b a t c h _ o p e r a t i o n ( o p e r a t i o n ,   d o c u m e n t _ i d s ,   p a r a m e t e r s ) 
 
                 r e t u r n   r e s u l t 
 
         e x c e p t   E x c e p t i o n   a s   e : 
 
                 r a i s e   H T T P E x c e p t i o n ( s t a t u s _ c o d e = 5 0 0 ,   d e t a i l ( s t r ( e ) ) 
 
 