"""Intent classifier for automatic query mode selection."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import re


class QueryIntent(Enum):
    """Query intent types."""
    ENTITY_QUESTION = "entity_question"  # Specific entity questions (local mode)
    GLOBAL_SUMMARY = "global_summary"    # Cross-document summary (global mode)
    TROUBLESHOOTING = "troubleshooting"  # Error codes,故障排查 (local mode)
    CONFIGURATION = "configuration"      # Configuration questions (local mode)
    GENERAL_QUESTION = "general_question"  # General questions (hybrid mode)
    KEYWORD_SEARCH = "keyword_search"    # Keyword/parameter search (bm25 mode)


@dataclass
class IntentClassification:
    """Intent classification result."""
    intent: QueryIntent
    confidence: float
    recommended_mode: str
    reasoning: str


class IntentClassifier:
    """Lightweight intent classifier for automatic query mode selection."""
    
    def __init__(self):
        """Initialize intent classifier."""
        self.patterns = {
            QueryIntent.ENTITY_QUESTION: [
                r'什么是.*？',
                r'如何.*？',
                r'.*怎么.*？',
                r'.*如何.*？',
                r'.*是什么.*？',
                r'.*有哪些.*？',
                r'.*包含什么.*？',
                r'.*的功能.*？',
                r'.*的作用.*？'
            ],
            QueryIntent.GLOBAL_SUMMARY: [
                r'总结.*',
                r'概述.*',
                r'整体.*',
                r'架构.*',
                r'系统.*',
                r'全部.*',
                r'所有.*',
                r'跨文档.*',
                r'综合.*',
                r'整体方案.*'
            ],
            QueryIntent.TROUBLESHOOTING: [
                r'错误.*',
                r'故障.*',
                r'问题.*',
                r'异常.*',
                r'失败.*',
                r'无法.*',
                r'不.*',
                r'error',
                r'0x[0-9a-fA-F]+',  # Error codes
                r'报错.*'
            ],
            QueryIntent.CONFIGURATION: [
                r'配置.*',
                r'设置.*',
                r'参数.*',
                r'初始化.*',
                r'安装.*',
                r'部署.*',
                r'环境.*',
                r'网络.*',
                r'连接.*',
                r'端口.*'
            ],
            QueryIntent.KEYWORD_SEARCH: [
                r'[A-Z0-9_]{3,}',  # Product codes, model numbers
                r'\d{3,}',  # Numbers
                r'[A-Z]{2,}\d+',  # Model patterns
                r'[A-Z]+-[A-Z0-9]+',  # Part numbers
                r'[A-Z]+\s+\d+'  # Model numbers
            ]
        }
    
    def classify(self, query: str) -> IntentClassification:
        """Classify query intent.
        
        Args:
            query: User query
            
        Returns:
            Intent classification result
        """
        query_lower = query.lower()
        scores = {}
        
        # Score each intent based on pattern matching
        for intent, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 1
            scores[intent] = score
        
        # Find highest scoring intent
        if not any(scores.values()):
            # Default to general question
            return IntentClassification(
                intent=QueryIntent.GENERAL_QUESTION,
                confidence=0.5,
                recommended_mode='hybrid',
                reasoning='No specific intent detected, using default hybrid mode'
            )
        
        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        # Map intent to recommended mode
        mode_mapping = {
            QueryIntent.ENTITY_QUESTION: 'local',
            QueryIntent.GLOBAL_SUMMARY: 'global',
            QueryIntent.TROUBLESHOOTING: 'local',
            QueryIntent.CONFIGURATION: 'local',
            QueryIntent.GENERAL_QUESTION: 'hybrid',
            QueryIntent.KEYWORD_SEARCH: 'bm25'
        }
        
        recommended_mode = mode_mapping.get(best_intent, 'hybrid')
        
        reasoning = self._generate_reasoning(best_intent, query)
        
        return IntentClassification(
            intent=best_intent,
            confidence=confidence,
            recommended_mode=recommended_mode,
            reasoning=reasoning
        )
    
    def _generate_reasoning(self, intent: QueryIntent, query: str) -> str:
        """Generate reasoning for classification.
        
        Args:
            intent: Classified intent
            query: Original query
            
        Returns:
            Reasoning text
        """
        reasoning_map = {
            QueryIntent.ENTITY_QUESTION: f"Query '{query}' appears to ask about specific entities, using local mode for precise entity relationship queries",
            QueryIntent.GLOBAL_SUMMARY: f"Query '{query}' appears to request summary or overview, using global mode for cross-document synthesis",
            QueryIntent.TROUBLESHOOTING: f"Query '{query}' appears to be troubleshooting-related, using local mode for specific error resolution",
            QueryIntent.CONFIGURATION: f"Query '{query}' appears to be configuration-related, using local mode for specific parameter queries",
            QueryIntent.GENERAL_QUESTION: f"Query '{query}' is a general question, using hybrid mode for balanced retrieval",
            QueryIntent.KEYWORD_SEARCH: f"Query '{query}' contains keywords/codes, using BM25 for precise keyword matching"
        }
        
        return reasoning_map.get(intent, "Using default hybrid mode")


# Global instance
intent_classifier = IntentClassifier()