"""RAG workflow manager for complete three-stage implementation."""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


class WorkflowStage(Enum):
    """RAG workflow stages."""
    INGESTION = "ingestion"
    RETRIEVAL = "retrieval"
    GENERATION = "generation"
    CITATION = "citation"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result of a workflow stage execution."""
    stage: WorkflowStage
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'stage': self.stage.value,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'data': self.data,
            'errors': self.errors,
            'metrics': self.metrics
        }


@dataclass
class WorkflowContext:
    """Context for workflow execution."""
    query: str
    user_id: str
    kb_name: str
    product_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    stage_results: Dict[WorkflowStage, StageResult] = field(default_factory=dict)
    
    def get_stage_result(self, stage: WorkflowStage) -> Optional[StageResult]:
        """Get result for a specific stage."""
        return self.stage_results.get(stage)
    
    def set_stage_result(self, result: StageResult):
        """Set result for a specific stage."""
        self.stage_results[result.stage] = result


class RAGWorkflowManager:
    """Manager for complete RAG three-stage workflow."""
    
    def __init__(self):
        """Initialize workflow manager."""
        self.stage_handlers = {
            WorkflowStage.INGESTION: self._handle_ingestion,
            WorkflowStage.RETRIEVAL: self._handle_retrieval,
            WorkflowStage.GENERATION: self._handle_generation,
            WorkflowStage.CITATION: self._handle_citation
        }
        self.quality_checks = {
            WorkflowStage.INGESTION: self._check_ingestion_quality,
            WorkflowStage.RETRIEVAL: self._check_retrieval_quality,
            WorkflowStage.GENERATION: self._check_generation_quality,
            WorkflowStage.CITATION: self._check_citation_quality
        }
    
    async def execute_workflow(self, context: WorkflowContext, 
                             stages: List[WorkflowStage] = None) -> Dict[str, Any]:
        """Execute complete RAG workflow.
        
        Args:
            context: Workflow context
            stages: Stages to execute (default: all stages)
            
        Returns:
            Complete workflow results
        """
        if stages is None:
            stages = [WorkflowStage.INGESTION, WorkflowStage.RETRIEVAL, 
                     WorkflowStage.GENERATION, WorkflowStage.CITATION]
        
        workflow_start = datetime.now()
        results = {
            'workflow_id': self._generate_workflow_id(),
            'context': {
                'query': context.query,
                'user_id': context.user_id,
                'kb_name': context.kb_name,
                'product_id': context.product_id
            },
            'stages': [],
            'overall_status': WorkflowStatus.PENDING.value,
            'start_time': workflow_start.isoformat(),
            'end_time': None,
            'total_duration_seconds': 0
        }
        
        overall_success = True
        
        for stage in stages:
            stage_result = await self._execute_stage(stage, context)
            context.set_stage_result(stage_result)
            results['stages'].append(stage_result.to_dict())
            
            if stage_result.status == WorkflowStatus.FAILED:
                overall_success = False
                break
        
        workflow_end = datetime.now()
        results['end_time'] = workflow_end.isoformat()
        results['total_duration_seconds'] = (workflow_end - workflow_start).total_seconds()
        results['overall_status'] = WorkflowStatus.COMPLETED.value if overall_success else WorkflowStatus.FAILED.value
        
        return results
    
    async def _execute_stage(self, stage: WorkflowStage, 
                            context: WorkflowContext) -> StageResult:
        """Execute a single workflow stage.
        
        Args:
            stage: Stage to execute
            context: Workflow context
            
        Returns:
            Stage execution result
        """
        start_time = datetime.now()
        result = StageResult(
            stage=stage,
            status=WorkflowStatus.IN_PROGRESS,
            start_time=start_time
        )
        
        try:
            # Execute stage handler
            handler = self.stage_handlers.get(stage)
            if handler:
                stage_data = await handler(context)
                result.data = stage_data
            
            # Perform quality checks
            quality_check = self.quality_checks.get(stage)
            if quality_check:
                quality_result = quality_check(result.data, context)
                result.metrics['quality_check'] = quality_result
            
            result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.errors.append(str(e))
        
        result.end_time = datetime.now()
        result.metrics['duration_seconds'] = (result.end_time - result.start_time).total_seconds()
        
        return result
    
    async def _handle_ingestion(self, context: WorkflowContext) -> Dict[str, Any]:
        """Handle ingestion stage.
        
        Args:
            context: Workflow context
            
        Returns:
            Ingestion stage data
        """
        from rag_kb.ingest.pipeline import IngestionPipeline
        from rag_kb.config import settings
        
        # Ingestion stage logic
        pipeline = IngestionPipeline()
        
        # Check if ingestion is needed
        ingestion_needed = self._check_ingestion_needed(context)
        
        if not ingestion_needed:
            return {
                'ingestion_performed': False,
                'reason': 'Knowledge base already up to date',
                'document_count': self._get_document_count(context)
            }
        
        # Perform ingestion
        ingestion_result = await pipeline.ingest_documents(
            user_id=context.user_id,
            kb_name=context.kb_name,
            product_id=context.product_id
        )
        
        return {
            'ingestion_performed': True,
            'documents_processed': ingestion_result.get('documents_processed', 0),
            'chunks_created': ingestion_result.get('chunks_created', 0),
            'graph_nodes': ingestion_result.get('graph_nodes', 0),
            'graph_edges': ingestion_result.get('graph_edges', 0),
            'processing_time': ingestion_result.get('processing_time', 0)
        }
    
    async def _handle_retrieval(self, context: WorkflowContext) -> Dict[str, Any]:
        """Handle retrieval stage.
        
        Args:
            context: Workflow context
            
        Returns:
            Retrieval stage data
        """
        from rag_kb.retrieval import BM25Search, HybridSearch
        from rag_kb.lightrag.adapter import LightRAGAdapter
        from rag_kb.multi_kb import multi_kb_manager
        from rag_kb.config import settings
        
        retrieval_mode = context.metadata.get('retrieval_mode', 'hybrid')
        query_mode = context.metadata.get('query_mode', 'hybrid')
        
        # Multi-KB routing
        if context.product_id and context.product_id != 'all':
            kb_result = multi_kb_manager.search_product_kb(
                product_id=context.product_id,
                query=context.query,
                query_mode=query_mode,
                top_k=context.metadata.get('top_k', 8)
            )
            
            if kb_result.get('success'):
                return {
                    'retrieval_mode': 'product_kb',
                    'product_id': context.product_id,
                    'answer': kb_result.get('answer', ''),
                    'sources': kb_result.get('sources', []),
                    'query_mode': query_mode
                }
        
        # Standard retrieval
        if retrieval_mode == 'bm25':
            bm25 = BM25Search()
            bm25_index_path = settings.data_dir / 'bm25_index.json'
            if bm25_index_path.exists():
                bm25.load_index(bm25_index_path)
            
            results = bm25.search(context.query, top_k=context.metadata.get('top_k', 8))
            
            return {
                'retrieval_mode': 'bm25',
                'results': results,
                'result_count': len(results),
                'query': context.query
            }
        
        elif retrieval_mode == 'hybrid':
            rag = LightRAGAdapter()
            bm25 = BM25Search()
            
            bm25_index_path = settings.data_dir / 'bm25_index.json'
            if bm25_index_path.exists():
                bm25.load_index(bm25_index_path)
            
            hybrid = HybridSearch(bm25_search=bm25, lightrag_adapter=rag)
            results = hybrid.search(context.query, top_k=context.metadata.get('top_k', 8))
            
            # Generate answer using LightRAG
            lightrag_answer = rag.query(context.query, mode=query_mode)
            
            return {
                'retrieval_mode': 'hybrid',
                'results': results,
                'result_count': len(results),
                'answer': lightrag_answer,
                'query_mode': query_mode,
                'query': context.query
            }
        
        else:  # lightrag mode
            rag = LightRAGAdapter()
            answer = rag.query(context.query, mode=query_mode)
            
            return {
                'retrieval_mode': 'lightrag',
                'answer': answer,
                'query_mode': query_mode,
                'query': context.query
            }
    
    async def _handle_generation(self, context: WorkflowContext) -> Dict[str, Any]:
        """Handle generation stage.
        
        Args:
            context: Workflow context
            
        Returns:
            Generation stage data
        """
        # Get retrieval results from previous stage
        retrieval_result = context.get_stage_result(WorkflowStage.RETRIEVAL)
        
        if not retrieval_result or retrieval_result.status != WorkflowStatus.COMPLETED:
            raise Exception("Retrieval stage must be completed before generation")
        
        retrieval_data = retrieval_result.data
        
        # If answer already generated in retrieval stage, use it
        if 'answer' in retrieval_data and retrieval_data['answer']:
            return {
                'answer': retrieval_data['answer'],
                'answer_length': len(retrieval_data['answer']),
                'generation_mode': 'integrated_with_retrieval'
            }
        
        # Otherwise, generate answer from retrieval results
        from rag_kb.lightrag.adapter import LightRAGAdapter
        
        rag = LightRAGAdapter()
        query_mode = context.metadata.get('query_mode', 'hybrid')
        answer = rag.query(context.query, mode=query_mode)
        
        return {
            'answer': answer,
            'answer_length': len(answer),
            'generation_mode': 'standalone',
            'query_mode': query_mode
        }
    
    async def _handle_citation(self, context: WorkflowContext) -> Dict[str, Any]:
        """Handle citation stage.
        
        Args:
            context: Workflow context
            
        Returns:
            Citation stage data
        """
        from rag_kb.api.main import _get_search_sources
        from rag_kb.lightrag.adapter import LightRAGAdapter
        
        # Get generation result from previous stage
        generation_result = context.get_stage_result(WorkflowStage.GENERATION)
        
        if not generation_result or generation_result.status != WorkflowStatus.COMPLETED:
            raise Exception("Generation stage must be completed before citation")
        
        # Extract sources
        rag = LightRAGAdapter()
        query_mode = context.metadata.get('query_mode', 'hybrid')
        retrieval_mode = context.metadata.get('retrieval_mode', 'hybrid')
        
        sources = _get_search_sources(rag, context.query, retrieval_mode)
        
        # Format citations with page numbers and chunk IDs
        formatted_citations = []
        for i, source in enumerate(sources[:5], 1):
            doc_id = source.get('doc_id', f"doc_{i}")
            title = source.get('title', f"文档 {i}")
            page_num = source.get('metadata', {}).get('page_number', 'N/A')
            chunk_id = source.get('chunk_id', f"chunk_{i}")
            score = source.get('score', 0.0)
            
            citation = {
                'index': i,
                'doc_id': doc_id,
                'title': title,
                'page_number': page_num,
                'chunk_id': chunk_id,
                'score': score,
                'entities': source.get('entities', [])
            }
            formatted_citations.append(citation)
        
        return {
            'citations': formatted_citations,
            'citation_count': len(formatted_citations),
            'answer_with_citations': self._format_answer_with_citations(
                generation_result.data.get('answer', ''),
                formatted_citations
            )
        }
    
    def _check_ingestion_quality(self, data: Dict[str, Any], 
                                 context: WorkflowContext) -> Dict[str, Any]:
        """Check ingestion quality.
        
        Args:
            data: Ingestion stage data
            context: Workflow context
            
        Returns:
            Quality check results
        """
        quality_metrics = {
            'passed': True,
            'checks': []
        }
        
        if data.get('ingestion_performed'):
            # Check document count
            doc_count = data.get('documents_processed', 0)
            quality_metrics['checks'].append({
                'name': 'document_count',
                'passed': doc_count > 0,
                'value': doc_count,
                'threshold': 1
            })
            
            # Check chunk creation
            chunk_count = data.get('chunks_created', 0)
            quality_metrics['checks'].append({
                'name': 'chunk_creation',
                'passed': chunk_count > 0,
                'value': chunk_count,
                'threshold': 1
            })
            
            # Check graph generation
            graph_nodes = data.get('graph_nodes', 0)
            quality_metrics['checks'].append({
                'name': 'graph_generation',
                'passed': graph_nodes > 0,
                'value': graph_nodes,
                'threshold': 1
            })
        
        quality_metrics['passed'] = all(check['passed'] for check in quality_metrics['checks'])
        
        return quality_metrics
    
    def _check_retrieval_quality(self, data: Dict[str, Any], 
                                context: WorkflowContext) -> Dict[str, Any]:
        """Check retrieval quality.
        
        Args:
            data: Retrieval stage data
            context: Workflow context
            
        Returns:
            Quality check results
        """
        quality_metrics = {
            'passed': True,
            'checks': []
        }
        
        # Check result count
        result_count = data.get('result_count', 0)
        quality_metrics['checks'].append({
            'name': 'result_count',
            'passed': result_count > 0,
            'value': result_count,
            'threshold': 1
        })
        
        # Check answer generation
        answer = data.get('answer', '')
        quality_metrics['checks'].append({
            'name': 'answer_generation',
            'passed': len(answer) > 0,
            'value': len(answer),
            'threshold': 1
        })
        
        quality_metrics['passed'] = all(check['passed'] for check in quality_metrics['checks'])
        
        return quality_metrics
    
    def _check_generation_quality(self, data: Dict[str, Any], 
                                 context: WorkflowContext) -> Dict[str, Any]:
        """Check generation quality.
        
        Args:
            data: Generation stage data
            context: Workflow context
            
        Returns:
            Quality check results
        """
        quality_metrics = {
            'passed': True,
            'checks': []
        }
        
        # Check answer length
        answer_length = data.get('answer_length', 0)
        quality_metrics['checks'].append({
            'name': 'answer_length',
            'passed': answer_length > 50,
            'value': answer_length,
            'threshold': 50
        })
        
        # Check answer relevance (basic check)
        answer = data.get('answer', '')
        query = context.query
        relevance_score = self._calculate_relevance(answer, query)
        quality_metrics['checks'].append({
            'name': 'answer_relevance',
            'passed': relevance_score > 0.3,
            'value': relevance_score,
            'threshold': 0.3
        })
        
        quality_metrics['passed'] = all(check['passed'] for check in quality_metrics['checks'])
        
        return quality_metrics
    
    def _check_citation_quality(self, data: Dict[str, Any], 
                               context: WorkflowContext) -> Dict[str, Any]:
        """Check citation quality.
        
        Args:
            data: Citation stage data
            context: Workflow context
            
        Returns:
            Quality check results
        """
        quality_metrics = {
            'passed': True,
            'checks': []
        }
        
        # Check citation count
        citation_count = data.get('citation_count', 0)
        quality_metrics['checks'].append({
            'name': 'citation_count',
            'passed': citation_count > 0,
            'value': citation_count,
            'threshold': 1
        })
        
        # Check citation completeness
        citations = data.get('citations', [])
        complete_citations = sum(1 for c in citations if c.get('page_number') != 'N/A')
        quality_metrics['checks'].append({
            'name': 'citation_completeness',
            'passed': complete_citations > 0,
            'value': complete_citations,
            'threshold': 1
        })
        
        quality_metrics['passed'] = all(check['passed'] for check in quality_metrics['checks'])
        
        return quality_metrics
    
    def _check_ingestion_needed(self, context: WorkflowContext) -> bool:
        """Check if ingestion is needed.
        
        Args:
            context: Workflow context
            
        Returns:
            True if ingestion is needed
        """
        # Simplified check - in production, implement proper change detection
        return False
    
    def _get_document_count(self, context: WorkflowContext) -> int:
        """Get current document count.
        
        Args:
            context: Workflow context
            
        Returns:
            Document count
        """
        # Simplified implementation
        return 0
    
    def _calculate_relevance(self, answer: str, query: str) -> float:
        """Calculate basic relevance score.
        
        Args:
            answer: Generated answer
            query: Original query
            
        Returns:
            Relevance score (0-1)
        """
        # Simple keyword overlap as basic relevance metric
        query_terms = set(query.lower().split())
        answer_terms = set(answer.lower().split())
        
        if not query_terms:
            return 0.0
        
        overlap = len(query_terms & answer_terms)
        return overlap / len(query_terms)
    
    def _format_answer_with_citations(self, answer: str, 
                                      citations: List[Dict[str, Any]]) -> str:
        """Format answer with citations.
        
        Args:
            answer: Generated answer
            citations: Citation data
            
        Returns:
            Formatted answer with citations
        """
        if not citations:
            return answer
        
        citation_text = "\n\n**参考来源：**\n"
        for citation in citations:
            citation_text += f"{citation['index']}. [{citation['title']}](#doc-{citation['doc_id']}) "
            if citation['page_number'] != 'N/A':
                citation_text += f"(页码: {citation['page_number']}) "
            citation_text += f"[{citation['chunk_id']}]\n"
        
        return answer + citation_text
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID.
        
        Returns:
            Workflow ID
        """
        from datetime import datetime
        return f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"


# Global instance
workflow_manager = RAGWorkflowManager()