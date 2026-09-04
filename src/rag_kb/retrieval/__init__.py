"""Retrieval module for advanced search capabilities."""

from rag_kb.retrieval.hybrid_search import HybridSearchEngine, QueryParam, SearchResult, SearchFilter
from rag_kb.retrieval.query_rewriter import QueryRewriter, RewriteContext, RewriteResult, get_query_rewriter
from rag_kb.retrieval.conversation_manager import ConversationManager, ConversationTurn, ConversationSession, get_conversation_manager
from rag_kb.retrieval.answer_linker import AnswerLinker, SourceLocation, AnswerWithSource, get_answer_linker

# Conditional import for reranker to handle missing dependencies
try:
    from rag_kb.retrieval.reranker import BGEReranker, RerankerFactory, RuleBasedReranker
    _reranker_available = True
except ImportError:
    _reranker_available = False
    BGEReranker = None
    RerankerFactory = None
    RuleBasedReranker = None

__all__ = [
    'HybridSearchEngine',
    'QueryParam',
    'SearchResult',
    'SearchFilter',
    'QueryRewriter',
    'RewriteContext',
    'RewriteResult',
    'get_query_rewriter',
    'ConversationManager',
    'ConversationTurn',
    'ConversationSession',
    'get_conversation_manager',
    'AnswerLinker',
    'SourceLocation',
    'AnswerWithSource',
    'get_answer_linker'
]

# Only add reranker components if available
if _reranker_available:
    __all__.extend(['BGEReranker', 'RerankerFactory', 'RuleBasedReranker'])