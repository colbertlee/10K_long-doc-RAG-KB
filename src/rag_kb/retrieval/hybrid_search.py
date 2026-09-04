"""Hybrid search combining BM25 sparse search and LightRAG vector search with RRF fusion."""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Optional

from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.retrieval.bm25_index_builder import BM25IndexBuilder
from rag_kb.retrieval.semantic_retrieval import AdvancedSemanticRetrieval, get_semantic_retrieval
from rag_kb.retrieval.vector_retrieval import EnhancedVectorRetrieval, get_vector_retrieval
from rag_kb.utils.performance_tuning import performance_tuner
from rag_kb.utils.retrieval_monitor import get_retrieval_monitor
from rag_kb.graph.graph_integration import get_graph_integration_service


@dataclass
class SearchFilter:
    """Search filter for filtering results by folder, type, or metadata."""
    folder_path: str | None = None
    file_type: str | None = None  # e.g., 'pdf', 'docx', 'md'
    metadata_filters: dict[str, Any] | None = None
    date_range: tuple[str, str] | None = None  # (start_date, end_date)
    
    def __post_init__(self):
        if self.metadata_filters is None:
            self.metadata_filters = {}


@dataclass
class SearchResult:
    """Unified search result from hybrid retrieval."""
    doc_id: str
    content: str
    score: float
    source: str  # 'bm25', 'vector', or 'hybrid'
    metadata: dict[str, Any] | None = None


class HybridSearchEngine:
    """Advanced hybrid search engine with intelligent fusion and multi-strategy retrieval."""
    
    def __init__(self, working_dir: str | None = None, use_performance_tuning: bool = True, enable_graph_integration: bool = False, enable_advanced_retrieval: bool = True):
        """Initialize advanced hybrid search engine.
        
        Args:
            working_dir: Working directory for LightRAG storage
            use_performance_tuning: Whether to use performance tuning settings
            enable_graph_integration: Whether to enable knowledge graph integration
            enable_advanced_retrieval: Whether to enable advanced semantic and vector retrieval
        """
        self.lightrag_adapter = LightRAGAdapter(working_dir)
        self.bm25_index_builder = BM25IndexBuilder(working_dir)
        self.use_performance_tuning = use_performance_tuning
        self.enable_graph_integration = enable_graph_integration
        self.enable_advanced_retrieval = enable_advanced_retrieval
        
        # Initialize graph integration service if enabled
        if self.enable_graph_integration:
            self.graph_service = get_graph_integration_service(enable_llm=False)
        else:
            self.graph_service = None
        
        # Initialize advanced retrieval systems if enabled
        if enable_advanced_retrieval:
            self.semantic_retrieval = get_semantic_retrieval(self.lightrag_adapter)
            self.vector_retrieval = get_vector_retrieval(self.lightrag_adapter)
        else:
            self.semantic_retrieval = None
            self.vector_retrieval = None
        
        # Initialize retrieval monitor
        self.retrieval_monitor = get_retrieval_monitor()
        self.enable_monitoring = True
        
        # Load performance tuning settings
        if use_performance_tuning:
            rrf_config = performance_tuner.get_rrf_config()
            self.rrf_k = rrf_config['k']
            self.rrf_weight_bm25 = rrf_config['weight_bm25']
            self.rrf_weight_vector = rrf_config['weight_vector']
        else:
            self.rrf_k = 60  # Default RRF constant
            # Improved default weights for better balance
            self.rrf_weight_bm25 = 0.35  # Slightly reduced for better semantic focus
            self.rrf_weight_vector = 0.65  # Increased for better semantic understanding
        
        # Advanced fusion strategies
        self.fusion_strategies = ['rrf', 'weighted', 'learning_to_rank', 'ensemble']
        self.current_fusion_strategy = 'rrf'
        
        # Dynamic weight adjustment based on query characteristics
        self.query_complexity_threshold = 15  # Characters
        self.use_adaptive_weights = True
        
        # Performance monitoring
        self.performance_metrics = {
            'total_searches': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'bm25_time': 0.0,
            'vector_time': 0.0,
            'semantic_time': 0.0,
            'fusion_time': 0.0
        }
        
    async def initialize(self):
        """Initialize both search engines and advanced retrieval systems."""
        await self.lightrag_adapter.ensure_initialized()
        # Try to load existing BM25 index
        await self.bm25_index_builder.load_index()
        
        # Initialize advanced retrieval systems if enabled
        if self.enable_advanced_retrieval:
            if self.semantic_retrieval:
                # Semantic retrieval doesn't need explicit initialization
                pass
            if self.vector_retrieval:
                await self.vector_retrieval.initialize()
    
    async def search(
        self, 
        query: str, 
        top_k: int = 10,
        mode: str = "hybrid",
        use_reranking: bool = True,  # Enable reranking by default for better precision
        search_filter: SearchFilter | None = None,
        use_advanced_retrieval: bool = None
    ) -> list[SearchResult]:
        """Perform advanced hybrid search with intelligent fusion.
        
        Args:
            query: Search query
            top_k: Number of results to return
            mode: Search mode - 'bm25', 'vector', 'semantic', 'hybrid', or 'advanced'
            use_reranking: Whether to apply reranking
            search_filter: Optional search filter for folder/type/metadata filtering
            use_advanced_retrieval: Whether to use advanced semantic and vector retrieval
            
        Returns:
            List of search results
        """
        start_time = time.time()
        
        # Start monitoring if enabled
        operation_id = None
        if self.enable_monitoring:
            operation_id = self.retrieval_monitor.start_operation(
                operation_type=mode,
                query=query,
                top_k=top_k,
                mode=mode
            )
        
        # Determine whether to use advanced retrieval
        use_advanced = use_advanced_retrieval if use_advanced_retrieval is not None else self.enable_advanced_retrieval
        
        if mode == "bm25":
            results = await self._bm25_search(query, top_k)
        elif mode == "vector":
            if use_advanced and self.vector_retrieval:
                results = await self._advanced_vector_search(query, top_k)
            else:
                results = await self._vector_search(query, top_k)
        elif mode == "semantic":
            if use_advanced and self.semantic_retrieval:
                results = await self._advanced_semantic_search(query, top_k)
            else:
                results = await self._vector_search(query, top_k)  # Fallback to vector
        elif mode == "hybrid":
            results = await self._hybrid_search(query, top_k, use_advanced)
        elif mode == "advanced":
            results = await self._advanced_hybrid_search(query, top_k)
        else:
            raise ValueError(f"Unknown search mode: {mode}")
        
        # Apply filters if provided
        if search_filter:
            results = self._apply_filters(results, search_filter)
        
        # Apply reranking if requested
        if use_reranking and results:
            try:
                results = await self._apply_reranking(query, results)
            except Exception as e:
                print(f"Reranking failed: {e}, using unranked results", flush=True)
        
        # Apply graph integration if enabled
        if self.enable_graph_integration and self.graph_service and results:
            results = self._apply_graph_integration(query, results)
        
        # Update performance metrics
        search_time = time.time() - start_time
        self.performance_metrics['total_searches'] += 1
        self.performance_metrics['total_time'] += search_time
        self.performance_metrics['avg_time'] = (
            self.performance_metrics['total_time'] / self.performance_metrics['total_searches']
        )
        
        # End monitoring if enabled
        if self.enable_monitoring and operation_id:
            # Calculate score distribution
            score_distribution = {}
            if results:
                scores = [result.score for result in results]
                score_distribution = {
                    'min': min(scores),
                    'max': max(scores),
                    'mean': sum(scores) / len(scores)
                }
            
            # Calculate source distribution
            source_distribution = {}
            if results:
                for result in results:
                    source = result.source
                    source_distribution[source] = source_distribution.get(source, 0) + 1
            
            self.retrieval_monitor.end_operation(
                operation_id=operation_id,
                results_count=len(results),
                success=len(results) > 0,
                cache_hit=False,  # TODO: Implement cache hit detection
                fusion_strategy=self.current_fusion_strategy if mode == 'advanced' else None,
                score_distribution=score_distribution,
                source_distribution=source_distribution
            )
        
        return results
    
    async def _bm25_search(self, query: str, top_k: int) -> list[SearchResult]:
        """BM25 sparse search."""
        try:
            # Use BM25IndexBuilder for search
            bm25_results = await self.bm25_index_builder.search(query, top_k=top_k)
            
            # If BM25 returns no results, try to provide a fallback
            if not bm25_results:
                print(f"BM25 search returned no results for query: {query}", flush=True)
                # Try to provide a simple text-based fallback
                return []
            
            return [
                SearchResult(
                    doc_id=result.get('id', f"bm25_{i}"),
                    content=result.get('text', ''),
                    score=result.get('score', 0.0),
                    source='bm25',
                    metadata=result.get('metadata', {})
                )
                for i, result in enumerate(bm25_results)
            ]
        except Exception as e:
            print(f"BM25 search error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return []
    
    async def _vector_search(self, query: str, top_k: int) -> list[SearchResult]:
        """LightRAG vector search with improved result parsing."""
        try:
            # Use LightRAG naive mode for more reliable results
            vector_results = await self.lightrag_adapter.query(
                query, 
                mode="naive"
            )
            
            # Parse LightRAG results with better content extraction
            results = []
            if vector_results and isinstance(vector_results, str):
                # If the result is a direct answer, treat it as a single search result
                if len(vector_results.strip()) > 50:  # Substantial content
                    results.append(SearchResult(
                        doc_id=f"vector_response_{len(results)}",
                        content=vector_results.strip(),
                        score=1.0,  # High score for direct response
                        source='vector',
                        metadata={'query': query, 'response_type': 'direct_answer'}
                    ))
                else:
                    # Try to extract actual document content from the response
                    # LightRAG returns formatted text, we need to parse it properly
                    lines = vector_results.split('\n')
                    current_content = []
                    current_doc_id = None
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            if current_content:
                                content = '\n'.join(current_content).strip()
                                if content and len(content) > 20:  # Filter out very short content
                                    results.append(SearchResult(
                                        doc_id=current_doc_id or f"vector_{len(results)}",
                                        content=content,
                                        score=1.0 - (len(results) / (top_k + 1)),  # Better scoring
                                        source='vector',
                                        metadata={}
                                    ))
                                current_content = []
                                current_doc_id = None
                        elif line.startswith('[doc_id=') or line.startswith('文档') or line.startswith('[source='):
                            # This looks like a document identifier
                            if current_content:
                                content = '\n'.join(current_content).strip()
                                if content and len(content) > 20:
                                    results.append(SearchResult(
                                        doc_id=current_doc_id or f"vector_{len(results)}",
                                        content=content,
                                        score=1.0 - (len(results) / (top_k + 1)),
                                        source='vector',
                                        metadata={}
                                    ))
                            current_content = []
                            current_doc_id = line
                        else:
                            current_content.append(line)
                    
                    # Don't forget the last content
                    if current_content:
                        content = '\n'.join(current_content).strip()
                        if content and len(content) > 20:
                            results.append(SearchResult(
                                doc_id=current_doc_id or f"vector_{len(results)}",
                                content=content,
                                score=1.0 - (len(results) / (top_k + 1)),
                                source='vector',
                                metadata={}
                            ))
            
            # If no results from parsing, use the raw response as a fallback
            if not results and vector_results:
                # Handle both string and dict responses
                if isinstance(vector_results, str) and len(vector_results.strip()) > 10:
                    results.append(SearchResult(
                        doc_id=f"vector_fallback",
                        content=vector_results.strip(),
                        score=0.8,  # Lower score for fallback
                        source='vector',
                        metadata={'query': query, 'response_type': 'fallback'}
                    ))
                elif isinstance(vector_results, dict) and 'answer' in vector_results:
                    answer = vector_results['answer']
                    if isinstance(answer, str) and len(answer.strip()) > 10:
                        results.append(SearchResult(
                            doc_id=f"vector_fallback",
                            content=answer.strip(),
                            score=0.8,  # Lower score for fallback
                            source='vector',
                            metadata={'query': query, 'response_type': 'fallback_dict'}
                        ))
            
            return results[:top_k] if results else []
        except Exception as e:
            print(f"Vector search error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return []
    
    async def _advanced_semantic_search(self, query: str, top_k: int) -> list[SearchResult]:
        """Advanced semantic search using the semantic retrieval system."""
        if not self.semantic_retrieval:
            return await self._vector_search(query, top_k)
        
        try:
            semantic_results = await self.semantic_retrieval.semantic_search(
                query, 
                top_k=top_k,
                use_expansion=True,
                enable_reranking=False  # We'll apply reranking later
            )
            
            # Convert semantic results to standard search results
            search_results = []
            for result in semantic_results:
                search_result = SearchResult(
                    doc_id=result.doc_id,
                    content=result.content,
                    score=result.score,
                    source='semantic',
                    metadata={
                        **(result.metadata or {}),
                        'semantic_score': result.semantic_score,
                        'relevance_score': result.relevance_score,
                        'expansion_used': result.expansion_used,
                        'query_match_details': result.query_match_details
                    }
                )
                search_results.append(search_result)
            
            return search_results
        except Exception as e:
            print(f"Advanced semantic search error: {e}", flush=True)
            return await self._vector_search(query, top_k)  # Fallback
    
    async def _advanced_vector_search(self, query: str, top_k: int) -> list[SearchResult]:
        """Advanced vector search using the vector retrieval system."""
        if not self.vector_retrieval:
            return await self._vector_search(query, top_k)
        
        try:
            vector_results = await self.vector_retrieval.vector_search(
                query,
                top_k=top_k,
                use_multi_vector=True,
                similarity_metric='cosine'
            )
            
            # Convert vector results to standard search results
            search_results = []
            for result in vector_results:
                search_result = SearchResult(
                    doc_id=result.doc_id,
                    content=result.content,
                    score=result.similarity_score,
                    source='vector_advanced',
                    metadata={
                        **(result.metadata or {}),
                        'embedding_distance': result.embedding_distance,
                        'vector_metrics': result.vector_metrics,
                        'embedding_model': result.embedding_model
                    }
                )
                search_results.append(search_result)
            
            return search_results
        except Exception as e:
            print(f"Advanced vector search error: {e}", flush=True)
            return await self._vector_search(query, top_k)  # Fallback
    
    async def _advanced_hybrid_search(self, query: str, top_k: int) -> list[SearchResult]:
        """Advanced hybrid search combining all retrieval methods with intelligent fusion."""
        start_time = time.time()
        
        # Run all retrieval methods in parallel
        tasks = []
        
        # BM25 search
        tasks.append(self._bm25_search(query, top_k * 2))
        
        # Advanced vector search
        if self.vector_retrieval:
            tasks.append(self._advanced_vector_search(query, top_k * 2))
        else:
            tasks.append(self._vector_search(query, top_k * 2))
        
        # Advanced semantic search
        if self.semantic_retrieval:
            tasks.append(self._advanced_semantic_search(query, top_k * 2))
        
        # Execute all searches with timeout
        try:
            results_list = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=15.0  # 15 second total timeout
            )
        except asyncio.TimeoutError:
            print("Advanced hybrid search timeout, using partial results", flush=True)
            results_list = []
            for task in tasks:
                if task.done():
                    try:
                        results_list.append(task.result())
                    except:
                        results_list.append([])
                else:
                    results_list.append([])
        
        # Separate results by type
        bm25_results = results_list[0] if len(results_list) > 0 and not isinstance(results_list[0], Exception) else []
        vector_results = results_list[1] if len(results_list) > 1 and not isinstance(results_list[1], Exception) else []
        semantic_results = results_list[2] if len(results_list) > 2 and not isinstance(results_list[2], Exception) else []
        
        # Apply intelligent fusion based on current strategy
        if self.current_fusion_strategy == 'rrf':
            fused_results = self._advanced_rrf_fusion(bm25_results, vector_results, semantic_results, top_k)
        elif self.current_fusion_strategy == 'weighted':
            fused_results = self._weighted_fusion(bm25_results, vector_results, semantic_results, top_k)
        elif self.current_fusion_strategy == 'ensemble':
            fused_results = self._ensemble_fusion(bm25_results, vector_results, semantic_results, top_k)
        else:
            fused_results = self._advanced_rrf_fusion(bm25_results, vector_results, semantic_results, top_k)
        
        fusion_time = time.time() - start_time
        self.performance_metrics['fusion_time'] = fusion_time
        
        return fused_results
    
    async def _hybrid_search(self, query: str, top_k: int, use_advanced: bool = True) -> list[SearchResult]:
        """Optimized hybrid search with parallel execution and timeout control."""
        # Adjust weights based on query characteristics
        if self.use_adaptive_weights:
            self._adjust_weights_for_query(query)
        
        # Run both searches in parallel with individual timeout control
        try:
            bm25_task = asyncio.create_task(asyncio.wait_for(
                self._bm25_search(query, top_k * 2), 
                timeout=3.0  # 3 second timeout for BM25
            ))
            vector_task = asyncio.create_task(asyncio.wait_for(
                self._vector_search(query, top_k * 2), 
                timeout=5.0  # 5 second timeout for vector search
            ))
            
            # Use asyncio.wait with timeout for overall control
            done, pending = await asyncio.wait(
                [bm25_task, vector_task],
                timeout=8.0,  # 8 second total timeout
                return_when=asyncio.ALL_COMPLETED
            )
            
            # Cancel any pending tasks
            for task in pending:
                task.cancel()
            
            # Get results from completed tasks
            bm25_results = []
            vector_results = []
            
            for task in done:
                try:
                    result = task.result()
                    # Simple task identification based on task naming
                    if task == bm25_task:
                        bm25_results = result
                    else:
                        vector_results = result
                except Exception as e:
                    print(f"Search task error: {e}", flush=True)
            
            # Apply RRF fusion
            fused_results = self._rrf_fusion(bm25_results, vector_results, top_k)
            
            return fused_results
            
        except asyncio.TimeoutError:
            print(f"Hybrid search timeout, using partial results", flush=True)
            # Try to get whatever results we have
            partial_results = []
            try:
                if 'bm25_task' in locals() and bm25_task.done():
                    partial_results.extend(bm25_task.result())
                if 'vector_task' in locals() and vector_task.done():
                    partial_results.extend(vector_task.result())
            except:
                pass
            
            # If we have some results, return them
            if partial_results:
                return partial_results[:top_k]
            
            # Fallback to BM25 only
            return await self._bm25_search(query, top_k)
    
    def _adjust_weights_for_query(self, query: str):
        """Dynamically adjust retrieval weights based on query characteristics."""
        query_length = len(query)
        
        # For short, specific queries, favor BM25 for exact matching
        if query_length <= self.query_complexity_threshold:
            self.rrf_weight_bm25 = 0.5  # Increase BM25 weight for exact matches
            self.rrf_weight_vector = 0.5
        # For longer, complex queries, favor vector search for semantic understanding
        elif query_length > 30:
            self.rrf_weight_bm25 = 0.3  # Decrease BM25 weight
            self.rrf_weight_vector = 0.7  # Increase vector weight
        # For medium queries, use balanced weights
        else:
            self.rrf_weight_bm25 = 0.35
            self.rrf_weight_vector = 0.65
    
    def _rrf_fusion(
        self, 
        bm25_results: list[SearchResult], 
        vector_results: list[SearchResult],
        top_k: int
    ) -> list[SearchResult]:
        """Enhanced Reciprocal Rank Fusion with score normalization and dynamic weighting."""
        # Normalize BM25 scores to 0-1 range (Min-Max normalization)
        if bm25_results:
            bm25_raw_scores = [result.score for result in bm25_results]
            bm25_min, bm25_max = min(bm25_raw_scores), max(bm25_raw_scores)
            if bm25_max > bm25_min:
                for result in bm25_results:
                    result.score = (result.score - bm25_min) / (bm25_max - bm25_min)
        
        # Normalize vector scores to 0-1 range
        if vector_results:
            vector_raw_scores = [result.score for result in vector_results]
            vector_min, vector_max = min(vector_raw_scores), max(vector_raw_scores)
            if vector_max > vector_min:
                for result in vector_results:
                    result.score = (result.score - vector_min) / (vector_max - vector_min)
        
        # Create RRF score maps with normalized scores
        bm25_scores = {result.doc_id: (1.0 / (self.rrf_k + i + 1)) * self.rrf_weight_bm25 * result.score
                      for i, result in enumerate(bm25_results)}
        vector_scores = {result.doc_id: (1.0 / (self.rrf_k + i + 1)) * self.rrf_weight_vector * result.score
                        for i, result in enumerate(vector_results)}
        
        # Combine scores with dynamic weighting based on result quality
        combined_scores = {}
        all_doc_ids = set(bm25_scores.keys()) | set(vector_scores.keys())
        
        for doc_id in all_doc_ids:
            bm25_score = bm25_scores.get(doc_id, 0)
            vector_score = vector_scores.get(doc_id, 0)
            
            # Dynamic boost for documents appearing in both results
            boost = 1.2 if doc_id in bm25_scores.keys() and doc_id in vector_scores.keys() else 1.0
            
            combined_scores[doc_id] = (bm25_score + vector_score) * boost
        
        # Sort by combined score
        sorted_doc_ids = sorted(combined_scores.keys(), 
                               key=lambda x: combined_scores[x], 
                               reverse=True)
        
        # Build final results with enhanced metadata
        final_results = []
        for doc_id in sorted_doc_ids[:top_k]:
            # Prefer BM25 result if available, otherwise vector
            bm25_result = next((r for r in bm25_results if r.doc_id == doc_id), None)
            vector_result = next((r for r in vector_results if r.doc_id == doc_id), None)
            
            base_result = bm25_result or vector_result
            if base_result:
                # Enhance metadata with fusion information
                enhanced_metadata = (base_result.metadata or {}).copy()
                enhanced_metadata.update({
                    'fusion_score': combined_scores[doc_id],
                    'bm25_rank': next((i for i, r in enumerate(bm25_results) if r.doc_id == doc_id), -1),
                    'vector_rank': next((i for i, r in enumerate(vector_results) if r.doc_id == doc_id), -1),
                    'is_cross_source': doc_id in bm25_scores.keys() and doc_id in vector_scores.keys()
                })
                
                final_results.append(SearchResult(
                    doc_id=doc_id,
                    content=base_result.content,
                    score=combined_scores[doc_id],
                    source='hybrid',
                    metadata=enhanced_metadata
                ))
        
        return final_results
    
    def _advanced_rrf_fusion(
        self, 
        bm25_results: list[SearchResult], 
        vector_results: list[SearchResult],
        semantic_results: list[SearchResult],
        top_k: int
    ) -> list[SearchResult]:
        """Advanced RRF fusion with three-way combination and dynamic weighting."""
        # Normalize all result scores to 0-1 range
        def normalize_results(results):
            if not results:
                return []
            scores = [result.score for result in results]
            min_score, max_score = min(scores), max(scores)
            if max_score > min_score:
                for result in results:
                    result.score = (result.score - min_score) / (max_score - min_score)
            return results
        
        bm25_results = normalize_results(bm25_results)
        vector_results = normalize_results(vector_results)
        semantic_results = normalize_results(semantic_results)
        
        # Create RRF score maps with dynamic weights
        bm25_weight = self.rrf_weight_bm25
        vector_weight = self.rrf_weight_vector * 0.6  # Reduced due to semantic addition
        semantic_weight = self.rrf_weight_vector * 0.4  # New semantic weight
        
        bm25_scores = {result.doc_id: (1.0 / (self.rrf_k + i + 1)) * bm25_weight * result.score
                      for i, result in enumerate(bm25_results)}
        vector_scores = {result.doc_id: (1.0 / (self.rrf_k + i + 1)) * vector_weight * result.score
                        for i, result in enumerate(vector_results)}
        semantic_scores = {result.doc_id: (1.0 / (self.rrf_k + i + 1)) * semantic_weight * result.score
                          for i, result in enumerate(semantic_results)}
        
        # Combine scores with multi-source boost
        combined_scores = {}
        all_doc_ids = set(bm25_scores.keys()) | set(vector_scores.keys()) | set(semantic_scores.keys())
        
        for doc_id in all_doc_ids:
            bm25_score = bm25_scores.get(doc_id, 0)
            vector_score = vector_scores.get(doc_id, 0)
            semantic_score = semantic_scores.get(doc_id, 0)
            
            # Calculate source count for boost
            source_count = sum([
                1 if doc_id in bm25_scores else 0,
                1 if doc_id in vector_scores else 0,
                1 if doc_id in semantic_scores else 0
            ])
            
            # Dynamic boost based on source count
            boost = 1.0 + (source_count - 1) * 0.15  # 15% boost per additional source
            
            combined_scores[doc_id] = (bm25_score + vector_score + semantic_score) * boost
        
        # Sort by combined score
        sorted_doc_ids = sorted(combined_scores.keys(), 
                               key=lambda x: combined_scores[x], 
                               reverse=True)
        
        # Build final results with enhanced metadata
        final_results = []
        for doc_id in sorted_doc_ids[:top_k]:
            # Prefer result from most reliable source
            base_result = (
                next((r for r in semantic_results if r.doc_id == doc_id), None) or
                next((r for r in vector_results if r.doc_id == doc_id), None) or
                next((r for r in bm25_results if r.doc_id == doc_id), None)
            )
            
            if base_result:
                enhanced_metadata = (base_result.metadata or {}).copy()
                enhanced_metadata.update({
                    'fusion_score': combined_scores[doc_id],
                    'bm25_rank': next((i for i, r in enumerate(bm25_results) if r.doc_id == doc_id), -1),
                    'vector_rank': next((i for i, r in enumerate(vector_results) if r.doc_id == doc_id), -1),
                    'semantic_rank': next((i for i, r in enumerate(semantic_results) if r.doc_id == doc_id), -1),
                    'source_count': source_count,
                    'fusion_strategy': 'advanced_rrf'
                })
                
                final_results.append(SearchResult(
                    doc_id=doc_id,
                    content=base_result.content,
                    score=combined_scores[doc_id],
                    source='hybrid_advanced',
                    metadata=enhanced_metadata
                ))
        
        return final_results
    
    def _weighted_fusion(
        self,
        bm25_results: list[SearchResult],
        vector_results: list[SearchResult],
        semantic_results: list[SearchResult],
        top_k: int
    ) -> list[SearchResult]:
        """Weighted fusion with query-dependent weight adjustment."""
        # Adjust weights based on query characteristics
        query_length = len(bm25_results[0].metadata.get('query', '')) if bm25_results else 0
        
        if query_length <= 10:
            # Short queries: favor BM25
            weights = {'bm25': 0.5, 'vector': 0.3, 'semantic': 0.2}
        elif query_length > 30:
            # Long queries: favor semantic understanding
            weights = {'bm25': 0.2, 'vector': 0.3, 'semantic': 0.5}
        else:
            # Medium queries: balanced approach
            weights = {'bm25': 0.3, 'vector': 0.4, 'semantic': 0.3}
        
        # Normalize and weight scores
        def normalize_and_weight(results, weight):
            if not results:
                return {}
            scores = [result.score for result in results]
            min_score, max_score = min(scores), max(scores)
            if max_score > min_score:
                return {result.doc_id: ((result.score - min_score) / (max_score - min_score)) * weight
                       for result in results}
            return {result.doc_id: result.score * weight for result in results}
        
        bm25_scores = normalize_and_weight(bm25_results, weights['bm25'])
        vector_scores = normalize_and_weight(vector_results, weights['vector'])
        semantic_scores = normalize_and_weight(semantic_results, weights['semantic'])
        
        # Combine scores
        combined_scores = {}
        all_doc_ids = set(bm25_scores.keys()) | set(vector_scores.keys()) | set(semantic_scores.keys())
        
        for doc_id in all_doc_ids:
            combined_scores[doc_id] = (
                bm25_scores.get(doc_id, 0) +
                vector_scores.get(doc_id, 0) +
                semantic_scores.get(doc_id, 0)
            )
        
        # Sort and build results
        sorted_doc_ids = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)
        
        final_results = []
        for doc_id in sorted_doc_ids[:top_k]:
            base_result = (
                next((r for r in semantic_results if r.doc_id == doc_id), None) or
                next((r for r in vector_results if r.doc_id == doc_id), None) or
                next((r for r in bm25_results if r.doc_id == doc_id), None)
            )
            
            if base_result:
                enhanced_metadata = (base_result.metadata or {}).copy()
                enhanced_metadata.update({
                    'fusion_score': combined_scores[doc_id],
                    'weights_used': weights,
                    'fusion_strategy': 'weighted'
                })
                
                final_results.append(SearchResult(
                    doc_id=doc_id,
                    content=base_result.content,
                    score=combined_scores[doc_id],
                    source='hybrid_weighted',
                    metadata=enhanced_metadata
                ))
        
        return final_results
    
    def _ensemble_fusion(
        self,
        bm25_results: list[SearchResult],
        vector_results: list[SearchResult],
        semantic_results: list[SearchResult],
        top_k: int
    ) -> list[SearchResult]:
        """Ensemble fusion combining multiple fusion strategies."""
        # Get results from different fusion strategies
        rrf_results = self._advanced_rrf_fusion(bm25_results, vector_results, semantic_results, top_k * 2)
        weighted_results = self._weighted_fusion(bm25_results, vector_results, semantic_results, top_k * 2)
        
        # Combine ensemble results
        ensemble_scores = {}
        all_doc_ids = set()
        
        # Add RRF scores
        for result in rrf_results:
            all_doc_ids.add(result.doc_id)
            ensemble_scores[result.doc_id] = ensemble_scores.get(result.doc_id, 0) + result.score * 0.5
        
        # Add weighted scores
        for result in weighted_results:
            all_doc_ids.add(result.doc_id)
            ensemble_scores[result.doc_id] = ensemble_scores.get(result.doc_id, 0) + result.score * 0.5
        
        # Sort by ensemble score
        sorted_doc_ids = sorted(all_doc_ids, key=lambda x: ensemble_scores[x], reverse=True)
        
        # Build final results
        final_results = []
        for doc_id in sorted_doc_ids[:top_k]:
            # Find the result with highest metadata quality
            base_result = (
                next((r for r in rrf_results if r.doc_id == doc_id), None) or
                next((r for r in weighted_results if r.doc_id == doc_id), None) or
                next((r for r in semantic_results if r.doc_id == doc_id), None) or
                next((r for r in vector_results if r.doc_id == doc_id), None) or
                next((r for r in bm25_results if r.doc_id == doc_id), None)
            )
            
            if base_result:
                enhanced_metadata = (base_result.metadata or {}).copy()
                enhanced_metadata.update({
                    'ensemble_score': ensemble_scores[doc_id],
                    'fusion_strategy': 'ensemble',
                    'rrf_contribution': next((r.score for r in rrf_results if r.doc_id == doc_id), 0) * 0.5,
                    'weighted_contribution': next((r.score for r in weighted_results if r.doc_id == doc_id), 0) * 0.5
                })
                
                final_results.append(SearchResult(
                    doc_id=doc_id,
                    content=base_result.content,
                    score=ensemble_scores[doc_id],
                    source='hybrid_ensemble',
                    metadata=enhanced_metadata
                ))
        
        return final_results
    
    async def search_with_reranking(
        self,
        query: str,
        top_k: int = 10,
        reranker: Any | None = None
    ) -> list[SearchResult]:
        """Search with reranking for improved precision."""
        # First get hybrid results
        hybrid_results = await self._hybrid_search(query, top_k * 2)
        
        if not reranker:
            return hybrid_results[:top_k]
        
        # Apply reranking
        reranked_results = await reranker.rerank(query, hybrid_results)
        
        return reranked_results[:top_k]
    
    async def build_bm25_index(self, documents: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Build BM25 index for hybrid search.
        
        Args:
            documents: Optional list of documents (will load from registry if not provided)
            
        Returns:
            Index building results
        """
        if documents:
            return await self.bm25_index_builder.build_index_from_documents(documents)
        else:
            return await self.bm25_index_builder.build_index_from_registry()
    
    def get_bm25_stats(self) -> dict[str, Any]:
        """Get BM25 index statistics."""
        return self.bm25_index_builder.get_index_stats()
    
    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        return self.performance_metrics.copy()
    
    def reset_performance_metrics(self):
        """Reset performance metrics."""
        self.performance_metrics = {
            'total_searches': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'bm25_time': 0.0,
            'vector_time': 0.0,
            'semantic_time': 0.0,
            'fusion_time': 0.0
        }
    
    def set_fusion_strategy(self, strategy: str):
        """Set the fusion strategy."""
        if strategy in self.fusion_strategies:
            self.current_fusion_strategy = strategy
            print(f"Fusion strategy set to: {strategy}", flush=True)
        else:
            print(f"Invalid fusion strategy: {strategy}. Available: {self.fusion_strategies}", flush=True)
    
    def get_fusion_strategy(self) -> str:
        """Get current fusion strategy."""
        return self.current_fusion_strategy
    
    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics from all retrieval systems."""
        cache_stats = {
            'semantic_cache': {},
            'vector_cache': {},
            'total_cache_size': 0
        }
        
        if self.semantic_retrieval:
            cache_stats['semantic_cache'] = self.semantic_retrieval.get_cache_stats()
            cache_stats['total_cache_size'] += cache_stats['semantic_cache'].get('cache_size', 0)
        
        if self.vector_retrieval:
            cache_stats['vector_cache'] = self.vector_retrieval.get_cache_stats()
            cache_stats['total_cache_size'] += cache_stats['vector_cache'].get('cache_entries', 0)
        
        return cache_stats
    
    def clear_all_caches(self):
        """Clear all caches."""
        if self.semantic_retrieval:
            self.semantic_retrieval.clear_cache()
        
        if self.vector_retrieval:
            self.vector_retrieval.clear_cache()
        
        print("All caches cleared", flush=True)
    
    def _apply_filters(self, results: list[SearchResult], search_filter: SearchFilter) -> list[SearchResult]:
        """Apply search filters to results.
        
        Args:
            results: Search results to filter
            search_filter: Filter criteria
            
        Returns:
            Filtered search results
        """
        if not results:
            return results
        
        filtered_results = []
        
        for result in results:
            metadata = result.metadata or {}
            
            # Check folder path filter
            if search_filter.folder_path:
                source_file = metadata.get('source_file', '')
                if not source_file.startswith(search_filter.folder_path):
                    continue
            
            # Check file type filter
            if search_filter.file_type:
                source_file = metadata.get('source_file', '')
                if not source_file.endswith(f'.{search_filter.file_type}'):
                    continue
            
            # Check metadata filters
            if search_filter.metadata_filters:
                match = True
                for key, value in search_filter.metadata_filters.items():
                    if metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            # Check date range filter
            if search_filter.date_range:
                start_date, end_date = search_filter.date_range
                upload_date = metadata.get('upload_date', '')
                if upload_date:
                    if not (start_date <= upload_date <= end_date):
                        continue
            
            filtered_results.append(result)
        
        return filtered_results
    
    async def _apply_reranking(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        """Apply reranking to search results.
        
        Args:
            query: Original search query
            results: Search results to rerank
            
        Returns:
            Reranked search results
        """
        try:
            from rag_kb.retrieval.reranker import RuleBasedReranker
            
            reranker = RuleBasedReranker()
            await reranker.initialize()
            
            # Apply reranking directly on SearchResult objects
            reranked_results = await reranker.rerank(query, results)
            
            return reranked_results
            
            return results
        except Exception as e:
            print(f"Reranking error: {e}", flush=True)
            # Return original results if reranking fails
            return results
    
    def _apply_graph_integration(
        self, 
        query: str, 
        results: list[SearchResult]
    ) -> list[SearchResult]:
        """Apply knowledge graph integration to search results.
        
        Args:
            query: Search query
            results: Search results to enhance
            
        Returns:
            Graph-enhanced search results
        """
        if not self.graph_service or not results:
            return results
        
        try:
            # Convert search results to chunk format
            chunks = []
            for result in results:
                chunk = Chunk(
                    chunk_id=result.doc_id,
                    doc_id=result.doc_id,
                    text=result.content,
                    level=0,
                    section_path=[],
                    token_count=len(result.content.split()),
                    metadata=result.metadata or {},
                    source_file=result.metadata.get('source_file', '') if result.metadata else '',
                    section_title=result.metadata.get('section_title', '') if result.metadata else ''
                )
                chunks.append(chunk)
            
            # Enhance chunks with graph information
            enhanced_results = self.graph_service.enhance_search_results(
                [r.__dict__ for r in results],
                chunks
            )
            
            # Convert back to SearchResult format
            graph_enhanced_results = []
            for enhanced_result in enhanced_results:
                graph_enhanced_results.append(SearchResult(
                    doc_id=enhanced_result.get('doc_id', ''),
                    content=enhanced_result.get('content', ''),
                    score=enhanced_result.get('score', 0.0),
                    source=enhanced_result.get('source', 'hybrid'),
                    metadata=enhanced_result.get('metadata', {})
                ))
            
            return graph_enhanced_results
            
        except Exception as e:
            print(f"Graph integration failed: {e}, returning original results")
            return results


class QueryParam:
    """Query parameters for LightRAG."""
    def __init__(self, mode: str = "hybrid", only_need_context: bool = False):
        self.mode = mode
        self.only_need_context = only_need_context