"""API routes for RAG KB."""

import asyncio
import sys
from fastapi import APIRouter, HTTPException, Query, File, UploadFile

router = APIRouter()


# Global instances for performance optimization
_rag_adapter = None
_query_rewriter = None
_conversation_manager = None
_quality_monitor = None

def get_rag():
    """Get LightRAG adapter instance (singleton for performance)."""
    global _rag_adapter
    if _rag_adapter is None:
        from rag_kb.lightrag.adapter import LightRAGAdapter
        _rag_adapter = LightRAGAdapter()
    return _rag_adapter


def get_quality_monitor():
    """Get quality monitor instance (lazy initialization)."""
    from rag_kb.utils.quality_monitor import get_quality_monitor
    return get_quality_monitor()


def get_query_rewriter():
    """Get query rewriter instance (lazy initialization)."""
    from rag_kb.retrieval.query_rewriter import get_query_rewriter
    return get_query_rewriter()


def get_conversation_manager():
    """Get conversation manager instance (lazy initialization)."""
    from rag_kb.retrieval.conversation_manager import get_conversation_manager
    return get_conversation_manager()


@router.get("/scan-upload-directory")
async def scan_upload_directory():
    """Scan upload directory for unregistered files and automatically index them."""
    try:
        from rag_kb.ingest.index_manager import get_index_manager
        
        index_manager = get_index_manager()
        results = await index_manager.auto_scan_and_index()
        
        return {
            'success': True,
            'results': results,
            'message': results.get('message', 'Scan completed')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Scan failed'
        }


@router.get("/index/status")
async def index_status():
    """Get current index status."""
    try:
        from rag_kb.ingest.index_manager import get_index_manager
        
        index_manager = get_index_manager()
        report = index_manager.get_index_integrity_report()
        
        return {
            'success': True,
            'report': report
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to get index status'
        }


@router.post("/index/all")
async def index_all():
    """Index all unindexed documents."""
    try:
        from rag_kb.ingest.index_manager import get_index_manager
        
        index_manager = get_index_manager()
        results = await index_manager.index_all_unindexed()
        
        return {
            'success': True,
            'results': results
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to index documents'
        }


@router.get("/search")
async def search_endpoint(q: str = Query(''), mode: str = 'hybrid', query_mode: str = 'hybrid', force_multi_step: bool = False, enable_validation: bool = False):
    """Search endpoint (GET method) with direct BM25 search for fast response."""
    try:
        import sys
        import json
        import math
        from collections import defaultdict
        from pathlib import Path
        from rag_kb.config.core_config import settings
        
        print(f"GET search request: query='{q}'", file=sys.stderr, flush=True)
        
        # Direct BM25 search without any adapter initialization
        # Use the actual data file that exists (kv_store_full_docs.json)
        text_chunks_file = Path(settings.lightrag_working_dir) / 'kv_store_full_docs.json'
        if not text_chunks_file.exists():
            return {
                'answer': "抱歉，我在知识库中没有找到相关信息。请尝试重新表述您的问题或提供更具体的关键词。",
                'structured': {
                    'answer_content': "抱歉，我在知识库中没有找到相关信息。",
                    'core_summary': "知识库中无相关信息",
                    'citations': [],
                    'is_structured': True
                },
                'citations': {'citations': [], 'total_sources': 0, 'has_citations': False},
                'sources_used': 0,
                'format_version': 'v2',
                'mode': 'bm25_direct',
                'query_mode': 'bm25',
                'category': 'all',
                'intent_classification': None
            }
        
        with open(text_chunks_file, 'r', encoding='utf-8') as f:
            text_chunks = json.load(f)
        
        # Convert to BM25 format using the full docs structure
        bm25_docs = []
        for doc_id, doc_data in text_chunks.items():
            # Skip documents that failed indexing
            if doc_data.get('status') == 'failed':
                continue
                
            bm25_docs.append({
                'id': doc_id,
                'text': doc_data.get('content', '')
            })
        
        # Simple BM25 search
        query_terms = q.lower().split()
        doc_freqs = defaultdict(int)
        term_doc_map = defaultdict(list)
        doc_lengths = []
        
        for doc in bm25_docs:
            text = doc.get('text', '').lower()
            terms = text.split()
            doc_lengths.append(len(terms))
            
            term_freq = defaultdict(int)
            for term in terms:
                term_freq[term] += 1
            
            for term, freq in term_freq.items():
                term_doc_map[term].append((doc['id'], freq))
                doc_freqs[term] += 1
        
        avg_doc_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0
        scores = defaultdict(float)
        k1 = 1.5
        b = 0.75
        
        for term in query_terms:
            if term not in term_doc_map:
                continue
            
            df = doc_freqs[term]
            idf = math.log((len(bm25_docs) - df + 0.5) / (df + 0.5) + 1.0)
            
            for doc_id, term_freq in term_doc_map[term]:
                doc_idx = next(i for i, doc in enumerate(bm25_docs) if doc['id'] == doc_id)
                doc_length = doc_lengths[doc_idx]
                
                numerator = term_freq * (k1 + 1)
                denominator = term_freq + k1 * (1 - b + b * doc_length / avg_doc_length)
                scores[doc_id] += idf * (numerator / denominator)
        
        # Get top results
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Check if results are meaningful (have non-zero scores)
        meaningful_results = [(doc_id, score) for doc_id, score in sorted_results if score > 0.01]
        
        if not meaningful_results:
            return {
                'answer': "抱歉，我在知识库中没有找到与您查询相关的信息。系统需要配置向量数据库才能进行语义搜索。请确保Ollama服务正在运行并且已下载必要的模型。",
                'structured': {
                    'answer_content': "抱歉，我在知识库中没有找到与您查询相关的信息。",
                    'core_summary': "知识库中无匹配信息",
                    'citations': [],
                    'is_structured': True
                },
                'citations': {'citations': [], 'total_sources': 0, 'has_citations': False},
                'sources_used': 0,
                'format_version': 'v2',
                'mode': 'bm25_direct',
                'query_mode': 'bm25',
                'category': 'all',
                'intent_classification': None,
                'match_details': {
                    'query_terms': query_terms,
                    'total_docs': len(bm25_docs),
                    'matched_docs': 0,
                    'reason': 'No meaningful BM25 scores'
                }
            }
        
        # Combine top meaningful results
        combined_context = ""
        for doc_id, score in meaningful_results:
            doc = next(doc for doc in bm25_docs if doc['id'] == doc_id)
            combined_context += f"\n[Source: {doc_id}]\n{doc['text']}\n"
        
        # Generate answer
        answer = f"基于关键词搜索找到以下相关信息：\n\n{combined_context}"
        
        print(f"GET search result: {len(answer)} chars", file=sys.stderr, flush=True)
        print(f"GET search result answer preview: {answer[:100]}", file=sys.stderr, flush=True)
        
        return {
            'answer': answer,
            'structured': {
                'answer_content': answer,
                'core_summary': answer[:200] + '...' if len(answer) > 200 else answer,
                'citations': [],
                'is_structured': True
            },
            'citations': {'citations': [], 'total_sources': 0, 'has_citations': False},
            'sources_used': len(meaningful_results),
            'format_version': 'v2',
            'mode': 'bm25_direct',
            'query_mode': 'bm25',
            'category': 'all',
            'intent_classification': None
        }
        
    except Exception as e:
        import traceback
        print(f"Error in search endpoint: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        return {
            'answer': f"搜索过程中出现错误: {str(e)}",
            'error': str(e),
            'query': q,
            'mode': query_mode
        }
def is_simple_query(query: str) -> bool:
    """Enhanced query complexity detection with fast-path optimization.
    
    Args:
        query: 用户查询
        
    Returns:
        True 如果是简单查询（适合快速路径）
    """
    # Fast-path for very short queries
    if len(query) < 10:
        return True
    
    # Fast-path for exact keyword matches (high precision needed)
    exact_match_patterns = [
        r'^[A-Z][a-zA-Z0-9_]+$',  # Exact technical term
        r'^\d+(\.\d+)?$',  # Exact number
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # Email
    ]
    
    import re
    for pattern in exact_match_patterns:
        if re.match(pattern, query.strip()):
            return True
    
    # Medium complexity detection
    if len(query) < 20:
        # Check for simple factual queries
        simple_patterns = [
            r'^什么是',  # Simple definition
            r'^多少',  # Simple quantity
            r'^有没有',  # Simple existence
            r'^是否',  # Simple yes/no
        ]
        for pattern in simple_patterns:
            if re.search(pattern, query):
                return True
    
    # Complex query detection (triggers multi-step RAG)
    complex_indicators = {
        'multi_hop_reasoning': [
            r'关系|依赖|影响|区别|对比|比较|联系',
            r'为什么|如何|怎么|原理|原因'
        ],
        'technical_operations': [
            r'配置|部署|安装|设置|调试|监控|管理',
            r'步骤|流程|方法|实现|方案'
        ],
        'reference_resolution': [
            r'它|这个|那个|上面|下面|前面|后面|该|其|其中',
            r'这里|那里'
        ],
        'multi_entity': [
            r'和|以及|或者|还有|与',
            r'分别|各自|各个'
        ]
    }
    
    # Check for complex indicators
    for category, patterns in complex_indicators.items():
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False  # Complex query
    
    # Check for multiple question words
    question_words = r'(什么|怎么|如何|为什么|哪|多少|是否|吗|呢|does|what|how|why|which|where|when)'
    if len(re.findall(question_words, query, re.IGNORECASE)) > 1:
        return False  # Complex query
    
    # Default to simple for remaining cases
    return True

@router.post("/search")
async def search_endpoint_post(body: dict):
    """Search endpoint (POST method) with structured output and conditional multi-step processing.
    
    Args:
        body: Request body with parameters:
            - q: Search query
            - mode: Search mode (deprecated, use query_mode)
            - query_mode: LightRAG query mode (hybrid/naive/local/global)
            - force_multi_step: Force multi-step RAG processing
            - enable_validation: Enable answer validation (performance optimization, default False)
    """
    try:
        import sys

        from rag_kb.lightrag.adapter import LightRAGAdapter
        
        q = body.get('q', '')
        mode = body.get('mode', 'hybrid')
        query_mode = body.get('query_mode', 'hybrid')
        force_multi_step = body.get('force_multi_step', False)
        enable_validation = body.get('enable_validation', False)  # Performance optimization
        
        print(f"POST search request: query='{q}', mode='{query_mode}', enable_validation={enable_validation}", file=sys.stderr, flush=True)
        
        # 条件多步处理：简单查询直接使用LightRAG，复杂查询使用多步RAG
        if not force_multi_step and is_simple_query(q):
            print(f"Using direct LightRAG for simple query", file=sys.stderr, flush=True)
            rag = LightRAGAdapter()
            result = await rag.query(q, mode=query_mode, enable_validation=enable_validation)
        else:
            print(f"Using multi-step RAG for complex query", file=sys.stderr, flush=True)
            # 使用多步RAG处理复杂查询
            from rag_kb.engines.multi_step_rag_engine import get_multi_step_rag_engine, MultiStepRAGRequest
            
            engine = get_multi_step_rag_engine()
            await engine.initialize()
            
            request = MultiStepRAGRequest(
                query=q,
                top_k=body.get('top_k', 10),
                mode=mode,
                use_reranking=body.get('use_reranking', True),
                enable_conversation_history=body.get('enable_conversation_history', False)
            )
            
            response = await engine.process_query(request)
            
            # 转换为标准格式
            result = {
                'answer': response.answer,
                'structured': {
                    'answer_content': response.answer,
                    'core_summary': response.answer[:200] + '...' if len(response.answer) > 200 else response.answer,
                    'citations': [{'source': f'chunk_{i}'} for i in response.citations],
                    'is_structured': True,
                    'sub_queries': response.sub_queries
                },
                'citations': {
                    'citations': response.citations,
                    'total_sources': response.chunks_used,
                    'has_citations': len(response.citations) > 0
                },
                'sources_used': response.chunks_used,
                'format_version': 'multi_step_v1',
                'mode': 'multi_step_rag',
                'query_mode': query_mode,
                'category': 'all',
                'intent_classification': None,
                'processing_time': response.processing_time
            }
        
        print(f"POST search result: {len(str(result)) if result else 0} chars", file=sys.stderr, flush=True)
        
        # Handle both old string format and new structured format
        if isinstance(result, dict):
            # New structured format
            return {
                'answer': result.get('answer', ''),
                'structured': result.get('structured', {}),
                'citations': result.get('citations', {}),
                'sources_used': result.get('sources_used', 0),
                'format_version': result.get('format_version', 'unknown'),
                'mode': result.get('mode', 'lightrag'),
                'query_mode': query_mode,
                'category': 'all',
                'intent_classification': None
            }
        else:
            # Legacy string format - convert to structured
            return {
                'answer': result,
                'structured': {
                    'answer_content': result,
                    'core_summary': result[:200] + '...' if len(result) > 200 else result,
                    'citations': [],
                    'is_structured': False
                },
                'citations': {'citations': [], 'total_sources': 0, 'has_citations': False},
                'sources_used': 0,
                'format_version': 'legacy',
                'mode': 'lightrag',
                'query_mode': query_mode,
                'category': 'all',
                'intent_classification': None
            }
    except ConnectionError as e:
        import traceback
        from rag_kb.config.core_config import settings
        error_msg = f"连接错误: {str(e)}. 请确保Ollama服务正在运行 (ollama serve) 并且已下载必要的模型 (ollama pull {settings.embedding_model})"
        print(f"POST search connection error: {error_msg}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return {
            'error': error_msg, 
            'answer': error_msg, 
            'sources': [], 
            'mode': 'lightrag',
            'structured': {
                'answer_content': error_msg,
                'core_summary': error_msg[:200] + '...' if len(error_msg) > 200 else error_msg,
                'citations': [],
                'is_structured': False
            }
        }
    except Exception as e:
        import traceback
        print(f"POST search error: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return {
            'error': str(e), 
            'answer': f'搜索失败: {str(e)}', 
            'sources': [], 
            'mode': 'lightrag',
            'structured': {
                'answer_content': f'搜索失败: {str(e)}',
                'core_summary': f'搜索失败: {str(e)}',
                'citations': [],
                'is_structured': False
            }
        }


@router.post("/multi-step-search")
async def multi_step_search_endpoint(body: dict):
    """Multi-step search endpoint with query decomposition and strict citation rules."""
    try:
        import sys
        from rag_kb.engines.multi_step_rag_engine import get_multi_step_rag_engine, MultiStepRAGRequest
        
        q = body.get('q', '')
        user_id = body.get('user_id')
        session_id = body.get('session_id')
        top_k = body.get('top_k', 10)
        mode = body.get('mode', 'hybrid')
        use_reranking = body.get('use_reranking', False)
        enable_conversation_history = body.get('enable_conversation_history', True)
        
        print(f"Multi-step search request: query='{q}', top_k={top_k}, mode='{mode}'", file=sys.stderr, flush=True)
        
        # Get multi-step RAG engine
        engine = get_multi_step_rag_engine()
        await engine.initialize()
        
        # Create request
        request = MultiStepRAGRequest(
            query=q,
            user_id=user_id,
            session_id=session_id,
            top_k=top_k,
            mode=mode,
            use_reranking=use_reranking,
            enable_conversation_history=enable_conversation_history
        )
        
        # Process query
        response = await engine.process_query(request)
        
        print(f"Multi-step search completed: {len(response.answer)} chars answer, {response.chunks_used} chunks used", 
              file=sys.stderr, flush=True)
        
        # Return structured response
        return {
            'answer': response.answer,
            'original_query': response.original_query,
            'resolved_query': response.resolved_query,
            'sub_queries': response.sub_queries,
            'answer_type': response.answer_type,
            'citations': response.citations,
            'contradictions': response.contradictions,
            'chunks_used': response.chunks_used,
            'processing_time': response.processing_time,
            'metadata': response.metadata,
            'timestamp': response.timestamp,
            'mode': 'multi_step_rag',
            'format_version': 'multi_step_v1'
        }
        
    except Exception as e:
        import traceback
        print(f"Multi-step search error: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return {
            'error': str(e),
            'answer': f'多步检索失败: {str(e)}',
            'original_query': body.get('q', ''),
            'resolved_query': body.get('q', ''),
            'sub_queries': [],
            'answer_type': 'error',
            'citations': [],
            'contradictions': [],
            'chunks_used': 0,
            'processing_time': 0,
            'metadata': {'error': str(e)},
            'timestamp': '',
            'mode': 'multi_step_rag',
            'format_version': 'multi_step_v1'
        }


@router.get("/multi-step-debug")
async def multi_step_debug_endpoint(q: str = Query(''), top_k: int = 10, mode: str = 'hybrid'):
    """Debug endpoint to see step-by-step processing without execution."""
    try:
        from rag_kb.engines.multi_step_rag_engine import get_multi_step_rag_engine, MultiStepRAGRequest
        
        engine = get_multi_step_rag_engine()
        
        request = MultiStepRAGRequest(
            query=q,
            top_k=top_k,
            mode=mode,
            enable_conversation_history=False
        )
        
        debug_info = engine.get_step_by_step_debug_info(request)
        
        return {
            'query': q,
            'debug_info': debug_info,
            'engine_stats': engine.get_statistics()
        }
        
    except Exception as e:
        import traceback
        print(f"Multi-step debug error: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return {
            'error': str(e),
            'query': q,
            'debug_info': None,
            'engine_stats': None
        }


def get_answer_validator():
    """Get answer validator instance (lazy initialization)."""
    from rag_kb.utils.answer_validator import AnswerValidator
    return AnswerValidator()


def get_config_history_manager():
    """Get config history manager instance (lazy initialization)."""
    from rag_kb.config.config_history import get_config_history_manager
    return get_config_history_manager()


@router.post("/llm/config/save")
async def save_llm_config(request: dict):
    """Save current LLM configuration as a named profile.
    
    Args:
        request: Configuration with name and description
        
    Returns:
        Save result
    """
    try:
        from rag_kb.config.config_history import get_config_history_manager
        
        name = request.get("name", "Unnamed Configuration")
        description = request.get("description", "")
        
        # Import current configuration
        config_manager = get_config_history_manager()
        saved_config = config_manager.import_from_current_config(name, description)
        
        return {
            "success": True,
            "message": "Configuration saved successfully",
            "config": {
                "config_id": saved_config.config_id,
                "name": saved_config.name,
                "provider": saved_config.provider,
                "model": saved_config.model,
                "created_at": saved_config.created_at
            }
        }
    except Exception as e:
        import traceback
        print(f"Error saving LLM config: {e}", flush=True)
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/llm/config/history")
async def get_config_history():
    """Get all saved LLM configurations.
    
    Returns:
        List of saved configurations
    """
    try:
        from rag_kb.config.config_history import get_config_history_manager
        
        config_manager = get_config_history_manager()
        configs = config_manager.get_all_configs()
        active_config = config_manager.get_active_config()
        
        return {
            "success": True,
            "configs": configs,
            "active_config_id": active_config.get('config_id') if active_config else None
        }
    except Exception as e:
        import traceback
        print(f"Error getting config history: {e}", flush=True)
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "configs": []
        }


@router.post("/llm/config/activate")
async def activate_config(request: dict):
    """Activate a saved configuration.
    
    Args:
        request: Request with config_id
        
    Returns:
        Activation result
    """
    try:
        from rag_kb.config.config_history import get_config_history_manager
        
        config_id = request.get("config_id")
        if not config_id:
            return {
                "success": False,
                "error": "config_id is required"
            }
        
        config_manager = get_config_history_manager()
        
        # Apply configuration to system
        success = config_manager.apply_config_to_system(config_id)
        
        if success:
            return {
                "success": True,
                "message": "Configuration activated successfully",
                "config_id": config_id
            }
        else:
            return {
                "success": False,
                "error": "Configuration not found or activation failed"
            }
    except Exception as e:
        import traceback
        print(f"Error activating config: {e}", flush=True)
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.delete("/llm/config/{config_id}")
async def delete_config(config_id: str):
    """Delete a saved configuration.
    
    Args:
        config_id: Configuration ID to delete
        
    Returns:
        Deletion result
    """
    try:
        from rag_kb.config.config_history import get_config_history_manager
        
        config_manager = get_config_history_manager()
        success = config_manager.delete_config(config_id)
        
        if success:
            return {
                "success": True,
                "message": "Configuration deleted successfully",
                "config_id": config_id
            }
        else:
            return {
                "success": False,
                "error": "Cannot delete active configuration or configuration not found"
            }
    except Exception as e:
        import traceback
        print(f"Error deleting config: {e}", flush=True)
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/llm/config/update")
async def update_config(request: dict):
    """Update a saved configuration.
    
    Args:
        request: Request with config_id and fields to update
        
    Returns:
        Update result
    """
    try:
        from rag_kb.config.config_history import get_config_history_manager
        
        config_id = request.get("config_id")
        if not config_id:
            return {
                "success": False,
                "error": "config_id is required"
            }
        
        config_manager = get_config_history_manager()
        
        # Extract updatable fields
        update_fields = {}
        if "name" in request:
            update_fields["name"] = request["name"]
        if "description" in request:
            update_fields["description"] = request["description"]
        
        success = config_manager.update_config(config_id, **update_fields)
        
        if success:
            return {
                "success": True,
                "message": "Configuration updated successfully",
                "config_id": config_id
            }
        else:
            return {
                "success": False,
                "error": "Configuration not found"
            }
    except Exception as e:
        import traceback
        print(f"Error updating config: {e}", flush=True)
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/validate/answer")
async def validate_answer_endpoint(body: dict):
    """Validate an answer for accuracy, rigor, and traceability."""
    try:
        answer = body.get('answer', '')
        retrieved_context = body.get('retrieved_context', '')
        query = body.get('query', '')
        sources = body.get('sources', [])
        
        validator = get_answer_validator()
        validation_result = validator.validate_answer(
            answer=answer,
            retrieved_context=retrieved_context,
            query=query,
            sources=sources
        )
        
        return {
            'is_valid': validation_result.is_valid,
            'accuracy_score': validation_result.accuracy_score,
            'rigor_score': validation_result.rigor_score,
            'traceability_score': validation_result.traceability_score,
            'hallucination_risk': validation_result.hallucination_risk,
            'issues': validation_result.issues,
            'warnings': validation_result.warnings,
            'source_coverage': validation_result.source_coverage
        }
    except Exception as e:
        import traceback
        print(f"Answer validation error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/summary")
async def quality_summary_endpoint():
    """Get quality summary statistics."""
    try:
        quality_monitor = get_quality_monitor()
        summary = quality_monitor.calculate_quality_summary()
        return summary
    except Exception as e:
        import traceback
        print(f"Quality summary error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/recent")
async def quality_recent_endpoint(limit: int = Query(100, ge=1, le=1000)):
    """Get recent query metrics."""
    try:
        quality_monitor = get_quality_monitor()
        recent_metrics = quality_monitor.get_recent_metrics(limit=limit)
        return {
            'recent_metrics': recent_metrics,
            'count': len(recent_metrics)
        }
    except Exception as e:
        import traceback
        print(f"Quality recent metrics error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/rewrite")
async def rewrite_query_endpoint(body: dict):
    """Rewrite query based on conversation context for better retrieval.
    
    Args:
        body: Request with query, user_id, session_id, and conversation_history
        
    Returns:
        Rewrite result with original and rewritten query
    """
    try:
        from rag_kb.retrieval.query_rewriter import RewriteContext, get_query_rewriter
        from rag_kb.retrieval.conversation_manager import get_conversation_manager
        
        query = body.get('query', '')
        user_id = body.get('user_id', 'default')
        session_id = body.get('session_id', 'default')
        conversation_history = body.get('conversation_history', [])
        
        # Get conversation history if not provided
        if not conversation_history and session_id:
            conv_manager = get_conversation_manager()
            conversation_history = conv_manager.get_conversation_history(user_id, session_id)
        
        # Create rewrite context
        context = RewriteContext(
            conversation_history=conversation_history,
            user_id=user_id,
            session_id=session_id,
            current_query=query,
            previous_queries=[turn.get('query', '') for turn in conversation_history]
        )
        
        # Rewrite query
        query_rewriter = get_query_rewriter()
        rewrite_result = query_rewriter.rewrite_query(context)
        
        return {
            'original_query': rewrite_result.original_query,
            'rewritten_query': rewrite_result.rewritten_query,
            'changes_made': rewrite_result.changes_made,
            'confidence': rewrite_result.confidence,
            'references_resolved': rewrite_result.references_resolved,
            'metadata': rewrite_result.metadata
        }
        
    except Exception as e:
        import traceback
        print(f"Query rewrite error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/turn")
async def add_conversation_turn(body: dict):
    """Add a conversation turn to the session history.
    
    Args:
        body: Request with user_id, session_id, query, rewritten_query, answer
        
    Returns:
        Created conversation turn
    """
    try:
        from rag_kb.retrieval.conversation_manager import get_conversation_manager
        
        user_id = body.get('user_id', 'default')
        session_id = body.get('session_id', 'default')
        query = body.get('query', '')
        rewritten_query = body.get('rewritten_query', query)
        answer = body.get('answer', '')
        metadata = body.get('metadata', {})
        
        conv_manager = get_conversation_manager()
        turn = conv_manager.add_conversation_turn(
            user_id=user_id,
            session_id=session_id,
            query=query,
            rewritten_query=rewritten_query,
            answer=answer,
            metadata=metadata
        )
        
        return {
            'turn_id': turn.turn_id,
            'session_id': turn.session_id,
            'timestamp': turn.timestamp,
            'metadata': turn.metadata
        }
        
    except Exception as e:
        import traceback
        print(f"Conversation turn error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/history/{user_id}/{session_id}")
async def get_conversation_history(user_id: str, session_id: str, max_turns: int = Query(5, ge=1, le=20)):
    """Get conversation history for a session.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        max_turns: Maximum number of turns to return
        
    Returns:
        Conversation history
    """
    try:
        from rag_kb.retrieval.conversation_manager import get_conversation_manager
        
        conv_manager = get_conversation_manager()
        history = conv_manager.get_conversation_history(user_id, session_id, max_turns)
        
        return {
            'user_id': user_id,
            'session_id': session_id,
            'history': history,
            'turn_count': len(history)
        }
        
    except Exception as e:
        import traceback
        print(f"Conversation history error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/context/{user_id}/{session_id}")
async def get_conversation_context(user_id: str, session_id: str):
    """Get conversation context summary for a session.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        
    Returns:
        Session context summary
    """
    try:
        from rag_kb.retrieval.conversation_manager import get_conversation_manager
        
        conv_manager = get_conversation_manager()
        context = conv_manager.get_session_context(user_id, session_id)
        
        return context
        
    except Exception as e:
        import traceback
        print(f"Conversation context error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/session/{user_id}/{session_id}")
async def clear_conversation_session(user_id: str, session_id: str):
    """Clear conversation history for a session.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        
    Returns:
        Deletion result
    """
    try:
        from rag_kb.retrieval.conversation_manager import get_conversation_manager
        
        conv_manager = get_conversation_manager()
        success = conv_manager.clear_session(user_id, session_id)
        
        if success:
            return {
                'success': True,
                'message': f'Session {session_id} cleared successfully'
            }
        else:
            return {
                'success': False,
                'error': f'Session {session_id} not found'
            }
        
    except Exception as e:
        import traceback
        print(f"Clear session error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """Get all session IDs for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        List of session IDs
    """
    try:
        from rag_kb.retrieval.conversation_manager import get_conversation_manager
        
        conv_manager = get_conversation_manager()
        sessions = conv_manager.get_user_sessions(user_id)
        
        return {
            'user_id': user_id,
            'sessions': sessions,
            'session_count': len(sessions)
        }
        
    except Exception as e:
        import traceback
        print(f"Get user sessions error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/filtered")
async def filtered_search_endpoint(body: dict):
    """Perform filtered search with folder/type/metadata filters.
    
    Args:
        body: Request with query, filters, and search parameters
        
    Returns:
        Filtered search results
    """
    try:
        from rag_kb.retrieval.hybrid_search import HybridSearchEngine, SearchFilter
        
        query = body.get('query', '')
        top_k = body.get('top_k', 10)
        mode = body.get('mode', 'hybrid')
        use_reranking = body.get('use_reranking', False)
        
        # Parse filters
        filter_data = body.get('filter', {})
        search_filter = SearchFilter(
            folder_path=filter_data.get('folder_path'),
            file_type=filter_data.get('file_type'),
            metadata_filters=filter_data.get('metadata_filters'),
            date_range=tuple(filter_data.get('date_range', [])) if filter_data.get('date_range') else None
        )
        
        # Perform search
        engine = HybridSearchEngine()
        await engine.initialize()
        
        results = await engine.search(
            query=query,
            top_k=top_k,
            mode=mode,
            use_reranking=use_reranking,
            search_filter=search_filter
        )
        
        return {
            'query': query,
            'results': [
                {
                    'doc_id': r.doc_id,
                    'content': r.content,
                    'score': r.score,
                    'source': r.source,
                    'metadata': r.metadata
                }
                for r in results
            ],
            'result_count': len(results),
            'filter_applied': {
                'folder_path': search_filter.folder_path,
                'file_type': search_filter.file_type,
                'metadata_filters': search_filter.metadata_filters,
                'date_range': search_filter.date_range
            }
        }
        
    except Exception as e:
        import traceback
        print(f"Filtered search error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer/link")
async def link_answer_to_sources(body: dict):
    """Link answer to precise source locations.
    
    Args:
        body: Request with answer and search results
        
    Returns:
        Answer with source locations and citations
    """
    try:
        from rag_kb.retrieval.answer_linker import get_answer_linker
        
        answer = body.get('answer', '')
        search_results = body.get('search_results', [])
        confidence = body.get('confidence', 0.8)
        add_citations = body.get('add_citations', True)
        
        # Link answer to sources
        answer_linker = get_answer_linker()
        answer_with_source = answer_linker.link_answer_to_sources(
            answer=answer,
            search_results=search_results,
            confidence=confidence
        )
        
        # Add citations if requested
        if add_citations:
            answer_with_citations = answer_linker.add_citations_to_answer(answer_with_source)
            answer_with_source.answer = answer_with_citations
        
        return answer_with_source.to_dict()
        
    except Exception as e:
        import traceback
        print(f"Answer linking error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer/segments")
async def extract_answer_segments(body: dict):
    """Extract answer segments with source mappings.
    
    Args:
        body: Request with answer and source locations
        
    Returns:
        Answer segments with source mappings
    """
    try:
        from rag_kb.retrieval.answer_linker import get_answer_linker, SourceLocation
        
        answer = body.get('answer', '')
        sources_data = body.get('sources', [])
        
        # Convert source data to SourceLocation objects
        sources = [SourceLocation(**source) for source in sources_data]
        
        # Extract segments
        answer_linker = get_answer_linker()
        segments = answer_linker.extract_answer_segments(answer, sources)
        
        return {
            'answer': answer,
            'segments': segments,
            'segment_count': len(segments)
        }
        
    except Exception as e:
        import traceback
        print(f"Answer segment extraction error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/issues")
async def quality_issues_endpoint():
    """Get identified quality issues."""
    try:
        quality_monitor = get_quality_monitor()
        issues = quality_monitor.identify_quality_issues()
        return {
            'issues': issues,
            'count': len(issues)
        }
    except Exception as e:
        import traceback
        print(f"Quality issues error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quality/feedback")
async def quality_feedback_endpoint(body: dict):
    """Submit user feedback for a query."""
    try:
        query_id = body.get('query_id')
        feedback = body.get('feedback')
        
        if not query_id or not feedback:
            raise HTTPException(status_code=400, detail="query_id and feedback are required")
        
        quality_monitor = get_quality_monitor()
        quality_monitor.add_user_feedback(query_id, feedback)
        
        return {
            'success': True,
            'message': 'Feedback recorded successfully'
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Quality feedback error: {e}", flush=True)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/completions")
async def chat_completions_endpoint(body: dict):
    """OpenAI-compatible chat completions endpoint with streaming support and enhanced conversation context.
    
    Args:
        body: Request body with messages and parameters
        
    Returns:
        Streaming response with chat completions
    """
    try:
        messages = body.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Check if streaming is requested
        stream = body.get("stream", False)
        
        # Extract conversation context and the last user message
        conversation_context = []
        user_message = ""
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                if not user_message:  # Keep the last user message as the main query
                    user_message = content
                conversation_context.append(f"用户: {content}")
            elif role == "assistant":
                conversation_context.append(f"助手: {content}")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        rag = get_rag()
        
        # Generate response using LightRAG (async) with conversation awareness
        import sys
        print(f"Chat completions request: user_message='{user_message[:100]}...', stream={stream}, context_length={len(conversation_context)}", file=sys.stderr, flush=True)
        
        # If there's conversation context, enhance the query
        if len(conversation_context) > 1:  # More than just the current message
            conversation_history = "\n".join(conversation_context[:-1])  # Exclude current message
            enhanced_query = f"""基于以下对话历史，回答用户的最新问题：

对话历史：
{conversation_history}

用户最新问题：{user_message}

请基于对话历史和知识库内容，准确回答用户的问题。确保回答与问题高度相关，避免答非所问。"""
            print(f"Using enhanced query with conversation context", file=sys.stderr, flush=True)
            query_to_use = enhanced_query
        else:
            query_to_use = user_message
        
        if stream:
            # Return streaming response
            from fastapi.responses import StreamingResponse
            return StreamingResponse(
                _stream_chat_response(rag, query_to_use),
                media_type="text/event-stream"
            )
        else:
            # Return non-streaming response with hybrid mode for better results
            result = await rag.query(query_to_use, mode="hybrid")
            print(f"Chat completions response: result type={type(result)}", file=sys.stderr, flush=True)
            
            # Handle both structured and legacy formats
            if isinstance(result, dict):
                answer = result.get('answer', '')
                structured_data = result.get('structured', {})
                citations = result.get('citations', {})
                format_version = result.get('format_version', 'unknown')
            else:
                answer = result
                structured_data = {
                    'answer_content': answer,
                    'core_summary': answer[:200] + '...' if len(answer) > 200 else answer,
                    'citations': [],
                    'is_structured': False
                }
                citations = {'citations': [], 'total_sources': 0, 'has_citations': False}
                format_version = 'legacy'
            
            print(f"Chat completions response: answer length={len(answer) if answer else 0}", file=sys.stderr, flush=True)
            print(f"Chat completions response preview: {answer[:200] if answer else 'empty'}...", file=sys.stderr, flush=True)
            
            # Validate answer quality - check for irrelevant fallback responses
            if not answer or len(answer) < 10 or answer == '[]':
                print("Answer too short or empty, returning proper no-results message", file=sys.stderr, flush=True)
                answer = "抱歉，我在知识库中没有找到与您查询相关的信息。请尝试重新表述您的问题或提供更具体的关键词。"
            elif '基于知识库找到以下相关信息' in answer and ('doc-71c44449ac6861e621f744589e2fbd2d' in answer or 'Dell AI学习资料深度学习总结' in answer):
                print("Answer appears to be irrelevant fallback (Dell AI content), returning proper no-results message", file=sys.stderr, flush=True)
                answer = "抱歉，我在知识库中没有找到与您查询相关的信息。请尝试重新表述您的问题或提供更具体的关键词。"
                print(f"Replaced answer with: {answer[:100]}...", file=sys.stderr, flush=True)
            else:
                print("Answer validation passed, using original answer", file=sys.stderr, flush=True)
            
            # Return in OpenAI-compatible format with enhanced metadata
            return {
                "id": "chat-" + str(hash(user_message)),
                "object": "chat.completion",
                "created": int(__import__("time").time()),
                "model": "lightrag",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": answer
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(user_message),
                    "completion_tokens": len(answer),
                    "total_tokens": len(user_message) + len(answer)
                },
                # Enhanced metadata for structured output
                "rag_metadata": {
                    "structured": structured_data,
                    "citations": citations,
                    "format_version": format_version,
                    "sources_used": result.get('sources_used', 0) if isinstance(result, dict) else 0
                }
            }
    except ConnectionError as e:
        import traceback
        error_msg = f"连接错误: {str(e)}. 请确保 Ollama 服务正在运行 (ollama serve) 并且已下载必要的模型"
        print(f"Chat completions connection error: {error_msg}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        
        # Return error in OpenAI-compatible format
        return {
            "id": "chat-error",
            "object": "chat.completion",
            "created": int(__import__("time").time()),
            "model": "lightrag",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": error_msg
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "error": error_msg
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = f"服务错误: {str(e)}"
        return {
            "id": "chat-error",
            "object": "chat.completion", 
            "created": int(__import__("time").time()),
            "model": "lightrag",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": error_msg
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "error": error_msg
        }


async def _stream_chat_response(rag, question):
    """Stream chat response in SSE format.
    
    Args:
        rag: LightRAG adapter instance
        question: User question
        
    Yields:
        SSE-formatted response chunks
    """
    import json
    import time
    import sys
    
    try:
        # Generate response with hybrid mode for better accuracy
        result = await rag.query(question, mode="hybrid")
        
        # Handle both structured and legacy formats
        if isinstance(result, dict):
            answer = result.get('answer', '')
            structured_data = result.get('structured', {})
            citations = result.get('citations', {})
            format_version = result.get('format_version', 'unknown')
        else:
            answer = result
            structured_data = {
                'answer_content': answer,
                'core_summary': answer[:200] + '...' if len(answer) > 200 else answer,
                'citations': [],
                'is_structured': False
            }
            citations = {'citations': [], 'total_sources': 0, 'has_citations': False}
            format_version = 'legacy'
        
        # Validate answer quality, fallback to naive if needed
        if not answer or len(answer) < 20 or answer == '[]':
            print("Streaming answer too short, retrying with naive mode", file=sys.stderr, flush=True)
            retry_result = await rag.query(question, mode="naive")
            if isinstance(retry_result, dict):
                answer = retry_result.get('answer', '')
                structured_data = retry_result.get('structured', structured_data)
                citations = retry_result.get('citations', citations)
            else:
                answer = retry_result
        
        # Check if answer is still empty or error
        if not answer or len(answer) < 20 or answer == '[]':
            error_msg = "服务连接失败：请确保 Ollama 服务正在运行 (ollama serve) 并且已下载必要的模型 (ollama pull nomic-embed-text 和 ollama pull qwen3.5:4b)"
            print(f"Streaming answer validation failed: {error_msg}", file=sys.stderr, flush=True)
            answer = error_msg
        
        # Stream the answer character by character
        chat_id = "chat-" + str(hash(question))
        created = int(time.time())
        
        # Send initial chunk
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': 'lightrag', 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
        
        # Stream content
        for i, char in enumerate(answer):
            yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': 'lightrag', 'choices': [{'index': 0, 'delta': {'content': char}, 'finish_reason': None}]})}\n\n"
            
            # Small delay to simulate streaming
            if i % 10 == 0:
                await asyncio.sleep(0.01)
        
        # Send final chunk with metadata
        final_chunk = {
            'id': chat_id, 
            'object': 'chat.completion.chunk', 
            'created': created, 
            'model': 'lightrag', 
            'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}],
            'rag_metadata': {
                'structured': structured_data,
                'citations': citations,
                'format_version': format_version,
                'sources_used': result.get('sources_used', 0) if isinstance(result, dict) else 0
            }
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
        
    except ConnectionError as e:
        import traceback
        error_msg = f"连接错误: {str(e)}. 请确保 Ollama 服务正在运行 (ollama serve) 并且已下载必要的模型"
        print(f"Streaming connection error: {error_msg}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        
        # Stream error message
        chat_id = "chat-error"
        created = int(time.time())
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': 'lightrag', 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
        
        for char in error_msg:
            yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': 'lightrag', 'choices': [{'index': 0, 'delta': {'content': char}, 'finish_reason': None}]})}\n\n"
        
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': 'lightrag', 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}], 'error': error_msg})}\n\n"
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        error_msg = f"Error: {str(e)}"
        chat_id = "chat-error"
        created = int(time.time())
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': 'lightrag', 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
        
        for char in error_msg:
            yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': 'lightrag', 'choices': [{'index': 0, 'delta': {'content': char}, 'finish_reason': None}]})}\n\n"
        
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': created, 'model': 'lightrag', 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}], 'error': error_msg})}\n\n"
        yield "data: [DONE]\n\n"


@router.get("/current-user")
async def get_current_user():
    """Get current user information.
    
    Returns:
        Current user information
    """
    import os
    return {
        "user_id": os.environ.get('RAGKB_CURRENT_USER', 'default'),
        "authenticated": True
    }


@router.get("/llm/providers")
async def get_llm_providers():
    """Get available LLM providers.
    
    Returns:
        List of available LLM providers
    """
    return {
        "providers": [
            {
                "id": "ollama",
                "name": "Ollama",
                "description": "Local LLM provider (推荐)",
                "models": ["qwen3.5:4b", "gemma4:e4b", "llama3.1:8b", "mistral:7b"]
            },
            {
                "id": "minimax",
                "name": "Minimax AI",
                "description": "Chinese domestic AI provider (M2.5/M2.7/M3 series)",
                "models": ["abab6.5s-chat (M3)", "abab6.5-chat (M2.7)", "abab5.5-chat (M2.5)", "abab5.5s-chat (M2.5s)"]
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "OpenAI API",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
            }
        ]
    }


@router.get("/llm/minimax/models")
async def get_minimax_models():
    """Get available Minimax models.
    
    Returns:
        List of available Minimax models
    """
    from rag_kb.lightrag.minimax_adapter import MinimaxAdapter
    
    adapter = MinimaxAdapter()  # Will use env vars
    return {
        "models": adapter.get_available_models()
    }


@router.get("/llm/minimax/recommended-params")
async def get_minimax_recommended_params(model: str = Query("abab6.5s-chat", description="Model name to get recommendations for")):
    """Get recommended parameters for a specific Minimax model.
    
    Args:
        model: Model name to get recommendations for
        
    Returns:
        Recommended parameters for the model
    """
    # Model-specific recommended parameters
    model_configs = {
        'abab6.5s-chat': {
            'chunk_token_size': 800,
            'max_token': 3072,
            'max_tokens': 1536,
            'description': 'M3系列最新模型，性能最佳，推荐使用'
        },
        'abab6.5-chat': {
            'chunk_token_size': 700,
            'max_token': 2568,
            'max_tokens': 1280,
            'description': 'M2.7系列高性能模型，适合复杂任务'
        },
        'abab5.5-chat': {
            'chunk_token_size': 500,
            'max_token': 2048,
            'max_tokens': 1024,
            'description': 'M2.5系列标准模型，性价比高'
        },
        'abab5.5s-chat': {
            'chunk_token_size': 400,
            'max_token': 1536,
            'max_tokens': 768,
            'description': 'M2.5s系列标准模型小型版本'
        }
    }
    
    config = model_configs.get(model, model_configs['abab6.5s-chat'])
    
    return {
        "success": True,
        "model": model,
        "recommended_params": config
    }


@router.post("/llm/minimax/test")
async def test_minimax_config(request: dict):
    """Test Minimax configuration.
    
    Args:
        request: Configuration with api_key, group_id, model
        
    Returns:
        Test result
    """
    from rag_kb.lightrag.minimax_adapter import check_minimax_config
    
    api_key = request.get("api_key")
    group_id = request.get("group_id")
    model = request.get("model", "abab6.5s-chat")
    
    if not api_key or not group_id:
        return {
            "success": False,
            "error": "api_key and group_id are required"
        }
    
    result = await check_minimax_config(api_key, group_id, model)
    return result


@router.post("/llm/minimax/configure")
async def configure_minimax(request: dict):
    """Configure Minimax provider.
    
    Args:
        request: Configuration with api_key, group_id, model, etc.
        
    Returns:
        Configuration result
    """
    import os
    import yaml
    from pathlib import Path
    from rag_kb.lightrag.minimax_adapter import MinimaxAdapter, MinimaxConfig
    
    api_key = request.get("api_key")
    group_id = request.get("group_id")
    model = request.get("model", "abab6.5s-chat")
    base_url = request.get("base_url", "https://api.minimax.chat/v1")
    temperature = request.get("temperature", 0.3)
    top_p = request.get("top_p", 0.9)
    max_tokens = request.get("max_tokens", 2048)
    
    # New parameters for automatic configuration
    chunk_token_size = request.get("chunk_token_size")
    max_token = request.get("max_token")
    
    if not api_key or not group_id:
        return {
            "success": False,
            "error": "api_key and group_id are required"
        }
    
    # Validate configuration
    config = MinimaxConfig(
        api_key=api_key,
        group_id=group_id,
        model=model,
        base_url=base_url,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
    
    adapter = MinimaxAdapter(config)
    validation = adapter.validate_config()
    
    if not validation["valid"]:
        return {
            "success": False,
            "error": "Configuration validation failed",
            "errors": validation["errors"]
        }
    
    # Set environment variables
    os.environ["MINIMAX_API_KEY"] = api_key
    os.environ["MINIMAX_GROUP_ID"] = group_id
    os.environ["MINIMAX_MODEL"] = model
    os.environ["MINIMAX_BASE_URL"] = base_url
    os.environ["MINIMAX_TEMPERATURE"] = str(temperature)
    os.environ["MINIMAX_TOP_P"] = str(top_p)
    os.environ["MINIMAX_MAX_TOKENS"] = str(max_tokens)
    
    # Update config.yaml file
    try:
        config_path = Path("configs/config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Update LLM configuration
            config_data['llm']['provider'] = 'minimax'
            config_data['llm']['base_url'] = base_url
            config_data['llm']['model'] = model
            config_data['llm']['temperature'] = temperature
            config_data['llm']['top_p'] = top_p
            config_data['llm']['max_tokens'] = max_tokens
            
            # Add Minimax-specific fields
            config_data['llm']['group_id'] = group_id
            config_data['llm']['api_key'] = api_key  # Save API key to config for persistence
            
            # Update LightRAG configuration if parameters provided
            if chunk_token_size is not None:
                config_data['lightrag']['chunk_token_size'] = chunk_token_size
            if max_token is not None:
                config_data['lightrag']['max_token'] = max_token
            
            # Write back to config file
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
                
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Could not update config.yaml: {e}")
    
    return {
        "success": True,
        "message": "Minimax configured successfully with optimized parameters",
        "config": validation["config"],
        "applied_settings": {
            "chunk_token_size": chunk_token_size,
            "max_token": max_token
        }
    }


@router.get("/system/config")
async def get_system_config():
    """Get current system configuration.
    
    Returns:
        Current system configuration
    """
    import os
    import yaml
    from pathlib import Path
    
    try:
        # Read directly from config.yaml to get current values
        config_path = Path("configs/config.yaml")
        print(f"DEBUG: Reading config from: {config_path.absolute()}", flush=True)
        print(f"DEBUG: Config file exists: {config_path.exists()}", flush=True)
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            print(f"DEBUG: Config data loaded: {config_data}", flush=True)
            
            lightrag_config = config_data.get('lightrag', {})
            llm_config = config_data.get('llm', {})
            app_config = config_data.get('app', {})
            reranking_config = config_data.get('reranking', {})
            
            config = {
                "chunk_token_size": lightrag_config.get('chunk_token_size', 1200),
                "max_token": lightrag_config.get('max_token', 4096),
                "query_mode": lightrag_config.get('query_mode', 'naive'),
                "enable_llm_cache": lightrag_config.get('enable_llm_cache', True),
                "enable_reranking": reranking_config.get('enable', False),
                "reranking_model": reranking_config.get('model', 'BAAI/bge-reranker-base'),
                "log_level": app_config.get('log_level', 'INFO'),
                "llm_provider": llm_config.get('provider', 'ollama'),
                "llm_model": llm_config.get('model', 'gemma4:e4b')
            }
            
            print(f"DEBUG: Final config: {config}", flush=True)
            
            # If using minimax, add recommended parameters info
            if llm_config.get('provider') == "minimax":
                model_configs = {
                    'abab6.5s-chat': {
                        'chunk_token_size': 800,
                        'max_token': 3072,
                        'max_tokens': 1536,
                        'description': 'M3系列最新模型，性能最佳'
                    },
                    'abab6.5-chat': {
                        'chunk_token_size': 700,
                        'max_token': 2568,
                        'max_tokens': 1280,
                        'description': 'M2.7系列高性能模型'
                    },
                    'abab5.5-chat': {
                        'chunk_token_size': 500,
                        'max_token': 2048,
                        'max_tokens': 1024,
                        'description': 'M2.5系列标准模型'
                    },
                    'abab5.5s-chat': {
                        'chunk_token_size': 400,
                        'max_token': 1536,
                        'max_tokens': 768,
                        'description': 'M2.5s系列小型模型'
                    }
                }
                
                current_model = llm_config.get('model', 'abab6.5s-chat')
                recommended = model_configs.get(current_model, model_configs['abab6.5s-chat'])
                config["minimax_recommended"] = recommended
                config["current_matches_recommended"] = (
                    config["chunk_token_size"] == recommended["chunk_token_size"] and
                    config["max_token"] == recommended["max_token"]
                )
            
            return {
                "success": True,
                "config": config
            }
        else:
            return {
                "success": False,
                "error": "Config file not found",
                "config": None
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "config": None
        }


@router.post("/system/config")
async def update_system_config(request: dict):
    """Update system configuration.
    
    Args:
        request: Configuration parameters
        
    Returns:
        Configuration result
    """
    import yaml
    from pathlib import Path
    from rag_kb.config.core_config import settings
    
    try:
        config_path = Path("configs/config.yaml")
        if not config_path.exists():
            return {
                "success": False,
                "error": "Config file not found"
            }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Update LightRAG settings
        if "chunk_token_size" in request:
            config_data['lightrag']['chunk_token_size'] = request["chunk_token_size"]
        
        if "max_token" in request:
            config_data['lightrag']['max_token'] = request["max_token"]
        
        if "query_mode" in request:
            config_data['lightrag']['query_mode'] = request["query_mode"]
        
        if "enable_llm_cache" in request:
            config_data['lightrag']['enable_llm_cache'] = request["enable_llm_cache"]
        
        # Update reranking settings
        if "enable_reranking" in request:
            config_data['reranking'] = config_data.get('reranking', {})
            config_data['reranking']['enable'] = request["enable_reranking"]
        
        if "reranking_model" in request:
            config_data['reranking'] = config_data.get('reranking', {})
            config_data['reranking']['model'] = request["reranking_model"]
        
        # Update app settings
        if "log_level" in request:
            config_data['app']['log_level'] = request["log_level"]
        
        # Write back to config file
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
        
        return {
            "success": True,
            "message": "System configuration updated successfully. Please restart the service to apply changes."
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/llm/current")
async def get_current_llm_config():
    """Get current LLM configuration.
    
    Returns:
        Current LLM configuration
    """
    import os
    import yaml
    from pathlib import Path
    
    try:
        # Read directly from config.yaml to get current values
        config_path = Path("configs/config.yaml")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            llm_config = config_data.get('llm', {})
            provider = llm_config.get('provider', 'ollama')
            
            config = {
                "provider": provider,
                "base_url": llm_config.get('base_url', 'http://localhost:11434'),
                "model": llm_config.get('model', 'gemma4:e4b'),
                "temperature": llm_config.get('temperature', 0.3),
                "top_p": llm_config.get('top_p', 0.9),
                "max_tokens": llm_config.get('max_tokens', 2048)
            }
            
            # Add provider-specific info
            if provider == "minimax":
                config["group_id"] = llm_config.get('group_id', '')
                config["api_key"] = llm_config.get('api_key', '')
                config["has_api_key"] = bool(llm_config.get('api_key', ''))
            elif provider == "openai":
                config["has_api_key"] = bool(os.getenv("OPENAI_API_KEY", ""))
            else:
                # For ollama and other providers
                config["has_api_key"] = True  # Local providers don't need API keys
            
            return {
                "success": True,
                "config": config
            }
        else:
            # Fallback to environment variables if config file doesn't exist
            provider = os.getenv("RAGKB_LLM_PROVIDER", "ollama")
            
            config = {
                "provider": provider,
                "base_url": os.getenv("RAGKB_LLM_BASE_URL", "http://localhost:11434"),
                "model": os.getenv("RAGKB_LLM_MODEL", "gemma4:e4b"),
                "temperature": float(os.getenv("RAGKB_LLM_TEMPERATURE", "0.3")),
                "top_p": float(os.getenv("RAGKB_LLM_TOP_P", "0.9")),
                "max_tokens": int(os.getenv("RAGKB_LLM_MAX_TOKENS", "2048"))
            }
            
            # Add provider-specific info
            if provider == "minimax":
                config["group_id"] = os.getenv("MINIMAX_GROUP_ID", "")
                config["has_api_key"] = bool(os.getenv("MINIMAX_API_KEY", ""))
            elif provider == "openai":
                config["has_api_key"] = bool(os.getenv("OPENAI_API_KEY", ""))
            else:
                config["has_api_key"] = True
            
            return {
                "success": True,
                "config": config
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "config": None
        }


@router.post("/llm/openai/test")
async def test_openai_config(body: dict):
    """Test OpenAI configuration.
    
    Args:
        body: Request body with api_key and model
        
    Returns:
        Test result
    """
    import os
    
    api_key = body.get("api_key")
    model = body.get("model", "gpt-4o")
    
    if not api_key:
        return {
            "success": False,
            "message": "api_key is required"
        }
    
    # Set environment variable for testing
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Validate API key format
    if not api_key.startswith("sk-"):
        return {
            "success": False,
            "message": "Invalid API key format. Should start with 'sk-'"
        }
    
    # Validate model
    valid_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    if model not in valid_models:
        return {
            "success": False,
            "message": f"Invalid model. Valid models: {', '.join(valid_models)}"
        }
    
    return {
        "success": True,
        "message": "OpenAI configuration is valid",
        "model": model
    }


@router.post("/llm/ollama/test")
async def test_ollama_config(body: dict):
    """Test Ollama configuration.
    
    Args:
        body: Request body with base_url and model
        
    Returns:
        Test result
    """
    base_url = body.get("base_url", "http://localhost:11434")
    model = body.get("model", "qwen3.5:4b")
    
    # Basic validation
    if not base_url:
        return {
            "success": False,
            "message": "base_url is required"
        }
    
    # Try to connect to Ollama
    try:
        import aiohttp
        import asyncio
        
        async def test_connection():
            async with aiohttp.ClientSession() as session:
                # Try to get model list
                url = f"{base_url}/api/tags"
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            data = await response.json()
                            models = data.get('models', [])
                            model_names = [m.get('name', '') for m in models]
                            
                            # Check if requested model is available
                            model_available = any(model in name for name in model_names)
                            
                            return {
                                "success": True,
                                "message": "Ollama连接测试成功",
                                "model": model,
                                "available_models": model_names,
                                "model_available": model_available
                            }
                        else:
                            return {
                                "success": False,
                                "message": f"Ollama服务响应异常: HTTP {response.status}"
                            }
                except asyncio.TimeoutError:
                    return {
                        "success": False,
                        "message": "连接Ollama超时，请检查服务是否运行"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"连接Ollama失败: {str(e)}"
                    }
        
        return await test_connection()
        
    except Exception as e:
        return {
            "success": False,
            "message": f"测试失败: {str(e)}"
        }


@router.post("/llm/ollama/configure")
async def configure_ollama(body: dict):
    """Configure Ollama provider.
    
    Args:
        body: Request body with Ollama configuration
        
    Returns:
        Configuration result
    """
    import os
    import yaml
    from pathlib import Path
    
    base_url = body.get("base_url", "http://localhost:11434")
    model = body.get("model", "qwen3.5:4b")
    temperature = body.get("temperature", 0.3)
    top_p = body.get("top_p", 0.9)
    max_tokens = body.get("max_tokens", 2048)
    
    # Validate parameters
    if not (0 <= temperature <= 2):
        return {
            "success": False,
            "error": "Temperature must be between 0 and 2"
        }
    
    if not (0 <= top_p <= 1):
        return {
            "success": False,
            "error": "Top P must be between 0 and 1"
        }
    
    if max_tokens < 1:
        return {
            "success": False,
            "error": "Max tokens must be at least 1"
        }
    
    # Set environment variables
    os.environ["OLLAMA_BASE_URL"] = base_url
    os.environ["OLLAMA_MODEL"] = model
    os.environ["OLLAMA_TEMPERATURE"] = str(temperature)
    os.environ["OLLAMA_TOP_P"] = str(top_p)
    os.environ["OLLAMA_MAX_TOKENS"] = str(max_tokens)
    
    # Update config.yaml file
    try:
        config_path = Path("configs/config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Update LLM configuration
            config_data['llm']['provider'] = 'ollama'
            config_data['llm']['base_url'] = base_url
            config_data['llm']['model'] = model
            config_data['llm']['temperature'] = temperature
            config_data['llm']['top_p'] = top_p
            config_data['llm']['max_tokens'] = max_tokens
            
            # Write back to config file
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
                
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Could not update config.yaml: {e}")
    
    return {
        "success": True,
        "message": "Ollama configured successfully",
        "model": model
    }


@router.post("/llm/openai/configure")
async def configure_openai(body: dict):
    """Configure OpenAI.
    
    Args:
        body: Request body with OpenAI configuration
        
    Returns:
        Configuration result
    """
    import os
    import yaml
    from pathlib import Path
    
    api_key = body.get("api_key")
    model = body.get("model", "gpt-4o")
    base_url = body.get("base_url", "https://api.openai.com/v1")
    temperature = body.get("temperature", 0.7)



    top_p = body.get("top_p", 1.0)
    max_tokens = body.get("max_tokens", 4096)
    
    if not api_key:
        return {
            "success": False,
            "error": "api_key is required"
        }
    
    # Validate API key format
    if not api_key.startswith("sk-"):
        return {
            "success": False,
            "error": "Invalid API key format. Should start with 'sk-'"
        }
    
    # Validate model
    valid_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    if model not in valid_models:
        return {
            "success": False,
            "error": f"Invalid model. Valid models: {', '.join(valid_models)}"
        }
    
    # Validate parameters
    if not (0 <= temperature <= 2):
        return {
            "success": False,
            "error": "Temperature must be between 0 and 2"
        }
    
    if not (0 <= top_p <= 1):
        return {
            "success": False,
            "error": "Top P must be between 0 and 1"
        }
    
    if max_tokens < 1:
        return {
            "success": False,
            "error": "Max tokens must be at least 1"
        }
    
    # Set environment variables
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_MODEL"] = model
    os.environ["OPENAI_BASE_URL"] = base_url
    os.environ["OPENAI_TEMPERATURE"] = str(temperature)
    os.environ["OPENAI_TOP_P"] = str(top_p)
    os.environ["OPENAI_MAX_TOKENS"] = str(max_tokens)
    
    # Update config.yaml file
    try:
        config_path = Path("configs/config.yaml")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Update LLM configuration
            config_data['llm']['provider'] = 'openai'
            config_data['llm']['base_url'] = base_url
            config_data['llm']['model'] = model
            config_data['llm']['temperature'] = temperature
            config_data['llm']['top_p'] = top_p
            config_data['llm']['max_tokens'] = max_tokens
            
            # Write back to config file
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
                
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Could not update config.yaml: {e}")
    
    return {
        "success": True,
        "message": "OpenAI configured successfully",
        "model": model
    }