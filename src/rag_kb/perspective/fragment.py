"""Similarity fragment perspective for enhanced retrieval analysis."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class MatchType(Enum):
    """Types of retrieval matches."""
    VECTOR = "vector"           # Vector similarity match
    GRAPH_NODE = "graph_node"   # Graph node match
    KEYWORD = "keyword"         # Keyword/BM25 match
    HYBRID = "hybrid"           # Hybrid combination match


@dataclass
class SimilarFragment:
    """Similar fragment data structure."""
    fragment_id: str
    text: str
    similarity_score: float
    match_type: MatchType
    source_doc_id: str
    source_title: str
    page_number: Optional[int] = None
    chunk_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'fragment_id': self.fragment_id,
            'text': self.text,
            'similarity_score': self.similarity_score,
            'match_type': self.match_type.value,
            'source_doc_id': self.source_doc_id,
            'source_title': self.source_title,
            'page_number': self.page_number,
            'chunk_id': self.chunk_id,
            'metadata': self.metadata
        }


class FragmentPerspective:
    """Manager for similarity fragment perspective and analysis."""
    
    def __init__(self):
        """Initialize fragment perspective manager."""
        from rag_kb.config import settings
        self.perspective_file = settings.data_dir / 'fragment_perspective.json'
        self.fragment_cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load fragment cache from file."""
        if self.perspective_file.exists():
            try:
                with open(self.perspective_file, 'r', encoding='utf-8') as f:
                    self.fragment_cache = json.load(f)
            except Exception as e:
                print(f"Error loading fragment cache: {e}")
    
    def _save_cache(self):
        """Save fragment cache to file."""
        try:
            with open(self.perspective_file, 'w', encoding='utf-8') as f:
                json.dump(self.fragment_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving fragment cache: {e}")
    
    def analyze_similar_fragments(self, query: str, retrieval_results: List[Dict[str, Any]], 
                                 top_k: int = 10) -> List[SimilarFragment]:
        """Analyze and enhance similar fragments from retrieval results.
        
        Args:
            query: Original query
            retrieval_results: Raw retrieval results
            top_k: Number of top fragments to return
            
        Returns:
            Enhanced similar fragments with detailed analysis
        """
        enhanced_fragments = []
        
        for i, result in enumerate(retrieval_results[:top_k]):
            # Determine match type
            match_type = self._determine_match_type(result)
            
            # Calculate enhanced similarity score
            similarity_score = self._calculate_enhanced_similarity(query, result, match_type)
            
            # Extract metadata
            metadata = result.get('metadata', {})
            
            fragment = SimilarFragment(
                fragment_id=f"frag_{i}",
                text=result.get('text', '')[:500],  # Limit text length
                similarity_score=similarity_score,
                match_type=match_type,
                source_doc_id=result.get('doc_id', result.get('id', '')),
                source_title=result.get('title', 'Unknown'),
                page_number=metadata.get('page_number'),
                chunk_id=metadata.get('chunk_id'),
                metadata={
                    'original_score': result.get('score', 0.0),
                    'entities': result.get('entities', []),
                    'context': self._extract_context(result.get('text', ''))
                }
            )
            
            enhanced_fragments.append(fragment)
        
        # Sort by enhanced similarity score
        enhanced_fragments.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return enhanced_fragments
    
    def _determine_match_type(self, result: Dict[str, Any]) -> MatchType:
        """Determine the type of match for a result.
        
        Args:
            result: Retrieval result
            
        Returns:
            Match type
        """
        metadata = result.get('metadata', {})
        
        # Check for graph node match
        if metadata.get('graph_node') or metadata.get('entity_match'):
            return MatchType.GRAPH_NODE
        
        # Check for keyword match
        if metadata.get('keyword_match') or metadata.get('bm25_match'):
            return MatchType.KEYWORD
        
        # Check for hybrid match
        if metadata.get('hybrid_match') or metadata.get('combined_score'):
            return MatchType.HYBRID
        
        # Default to vector match
        return MatchType.VECTOR
    
    def _calculate_enhanced_similarity(self, query: str, result: Dict[str, Any], 
                                      match_type: MatchType) -> float:
        """Calculate enhanced similarity score.
        
        Args:
            query: Original query
            result: Retrieval result
            match_type: Type of match
            
        Returns:
            Enhanced similarity score (0-1)
        """
        base_score = result.get('score', 0.0)
        
        # Normalize base score to 0-1 range
        normalized_score = min(base_score, 1.0)
        
        # Apply match type weighting
        type_weights = {
            MatchType.VECTOR: 1.0,
            MatchType.GRAPH_NODE: 1.2,  # Boost graph node matches
            MatchType.KEYWORD: 0.9,
            MatchType.HYBRID: 1.1
        }
        
        weighted_score = normalized_score * type_weights.get(match_type, 1.0)
        
        # Check for entity overlap
        text = result.get('text', '')
        query_terms = set(query.lower().split())
        text_terms = set(text.lower().split())
        
        entity_overlap = len(query_terms & text_terms) / max(len(query_terms), 1)
        
        # Combine scores
        enhanced_score = weighted_score * 0.7 + entity_overlap * 0.3
        
        return min(enhanced_score, 1.0)
    
    def _extract_context(self, text: str, context_length: int = 100) -> str:
        """Extract context from text.
        
        Args:
            text: Full text
            context_length: Length of context to extract
            
        Returns:
            Context string
        """
        if len(text) <= context_length:
            return text
        
        return text[:context_length] + "..."
    
    def compare_fragments(self, fragment1: SimilarFragment, 
                        fragment2: SimilarFragment) -> Dict[str, Any]:
        """Compare two similar fragments.
        
        Args:
            fragment1: First fragment
            fragment2: Second fragment
            
        Returns:
            Comparison result
        """
        # Calculate text similarity
        text_similarity = self._calculate_text_similarity(
            fragment1.text, fragment2.text
        )
        
        # Compare match types
        same_match_type = fragment1.match_type == fragment2.match_type
        
        # Compare sources
        same_source = fragment1.source_doc_id == fragment2.source_doc_id
        
        return {
            'fragment1_id': fragment1.fragment_id,
            'fragment2_id': fragment2.fragment_id,
            'text_similarity': text_similarity,
            'same_match_type': same_match_type,
            'same_source': same_source,
            'score_difference': abs(fragment1.similarity_score - fragment2.similarity_score),
            'recommendation': self._generate_comparison_recommendation(
                fragment1, fragment2, text_similarity
            )
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple overlap.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_comparison_recommendation(self, fragment1: SimilarFragment,
                                         fragment2: SimilarFragment,
                                         similarity: float) -> str:
        """Generate comparison recommendation.
        
        Args:
            fragment1: First fragment
            fragment2: Second fragment
            similarity: Text similarity
            
        Returns:
            Recommendation text
        """
        if similarity > 0.8:
            return "Fragments are very similar, consider using the higher scored one"
        elif similarity > 0.5:
            return "Fragments are moderately similar, both may provide useful context"
        else:
            return "Fragments are distinct, both provide unique information"
    
    def get_fragment_perspective_view(self, query: str, 
                                     retrieval_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get comprehensive fragment perspective view.
        
        Args:
            query: Original query
            retrieval_results: Retrieval results
            
        Returns:
            Comprehensive perspective view
        """
        # Analyze fragments
        fragments = self.analyze_similar_fragments(query, retrieval_results)
        
        # Group by match type
        fragments_by_type = {}
        for fragment in fragments:
            match_type = fragment.match_type.value
            if match_type not in fragments_by_type:
                fragments_by_type[match_type] = []
            fragments_by_type[match_type].append(fragment)
        
        # Calculate statistics
        total_fragments = len(fragments)
        avg_similarity = sum(f.similarity_score for f in fragments) / total_fragments if total_fragments > 0 else 0.0
        
        type_distribution = {
            match_type: len(fragments)
            for match_type, fragments in fragments_by_type.items()
        }
        
        return {
            'query': query,
            'total_fragments': total_fragments,
            'average_similarity': avg_similarity,
            'type_distribution': type_distribution,
            'fragments_by_type': {
                match_type: [f.to_dict() for f in fragments]
                for match_type, fragments in fragments_by_type.items()
            },
            'top_fragments': [f.to_dict() for f in fragments[:5]],
            'recommendations': self._generate_perspective_recommendations(fragments)
        }
    
    def _generate_perspective_recommendations(self, fragments: List[SimilarFragment]) -> List[str]:
        """Generate perspective recommendations.
        
        Args:
            fragments: List of fragments
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not fragments:
            return ["No fragments available for analysis"]
        
        # Check for high-quality matches
        high_quality = [f for f in fragments if f.similarity_score > 0.8]
        if high_quality:
            recommendations.append(f"Found {len(high_quality)} high-quality matches (similarity > 0.8)")
        
        # Check for diverse match types
        match_types = set(f.match_type for f in fragments)
        if len(match_types) > 1:
            recommendations.append(f"Retrieval used multiple match types: {', '.join(t.value for t in match_types)}")
        
        # Check for source diversity
        sources = set(f.source_doc_id for f in fragments)
        if len(sources) > 1:
            recommendations.append(f"Results span {len(sources)} different documents")
        
        if not recommendations:
            recommendations.append("Consider refining query for better results")
        
        return recommendations


# Global instance
fragment_perspective = FragmentPerspective()