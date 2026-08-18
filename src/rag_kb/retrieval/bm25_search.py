"""BM25 sparse search engine for keyword-based retrieval."""

import math
import re
from collections import defaultdict
from typing import List, Dict, Tuple
from pathlib import Path
import json
import pickle


class BM25SearchEngine:
    """BM25 search engine for sparse keyword-based retrieval."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75, cache_dir: Path = None):
        """Initialize BM25 search engine.
        
        Args:
            k1: Term saturation parameter (default: 1.5)
            b: Length normalization parameter (default: 0.75)
            cache_dir: Directory to cache index (default: ./data/bm25_cache)
        """
        self.k1 = k1
        self.b = b
        self.cache_dir = cache_dir or Path('./data/bm25_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Index structures
        self.doc_freqs = defaultdict(int)  # Document frequency for each term
        self.idf = {}  # Inverse document frequency
        self.doc_len = {}  # Document lengths
        self.avg_doc_len = 0  # Average document length
        self.corpus_size = 0  # Total number of documents
        self.documents = {}  # Document ID to text mapping
        self.term_doc_index = defaultdict(list)  # Term to document IDs mapping
        
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Simple tokenization - can be enhanced with better preprocessing
        text = text.lower()
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s\u4e00-\u9fff]', ' ', text)
        tokens = text.split()
        return tokens
    
    def add_document(self, doc_id: str, text: str, metadata: Dict = None):
        """Add a document to the BM25 index.
        
        Args:
            doc_id: Document identifier
            text: Document text content
            metadata: Optional document metadata
        """
        tokens = self.tokenize(text)
        self.documents[doc_id] = {
            'text': text,
            'tokens': tokens,
            'metadata': metadata or {}
        }
        self.doc_len[doc_id] = len(tokens)
        
        # Update term frequencies
        term_counts = defaultdict(int)
        for token in tokens:
            term_counts[token] += 1
        
        # Update document frequency and term-doc index
        for token, count in term_counts.items():
            self.doc_freqs[token] += 1
            self.term_doc_index[token].append(doc_id)
        
        self.corpus_size += 1
        self._update_avg_doc_len()
    
    def _update_avg_doc_len(self):
        """Update average document length."""
        if self.doc_len:
            self.avg_doc_len = sum(self.doc_len.values()) / len(self.doc_len)
    
    def _calculate_idf(self, term: str) -> float:
        """Calculate IDF for a term.
        
        Args:
            term: Term to calculate IDF for
            
        Returns:
            IDF score
        """
        df = self.doc_freqs.get(term, 0)
        if df == 0:
            return 0
        return math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1)
    
    def build_index(self):
        """Build the complete BM25 index after all documents are added."""
        # Pre-calculate IDF for all terms
        for term in self.doc_freqs:
            self.idf[term] = self._calculate_idf(term)
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Search for documents using BM25.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of (doc_id, score) tuples sorted by score descending
        """
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []
        
        scores = defaultdict(float)
        
        for token in query_tokens:
            if token not in self.term_doc_index:
                continue
            
            # Get IDF for the term
            idf = self.idf.get(token, self._calculate_idf(token))
            
            # Calculate BM25 score for each document containing this term
            for doc_id in self.term_doc_index[token]:
                doc_tokens = self.documents[doc_id]['tokens']
                term_freq = doc_tokens.count(token)
                doc_length = self.doc_len[doc_id]
                
                # BM25 formula
                numerator = term_freq * (self.k1 + 1)
                denominator = term_freq + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_len))
                score = idf * (numerator / denominator)
                
                scores[doc_id] += score
        
        # Sort by score descending
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def save_index(self, name: str = 'bm25_index'):
        """Save the BM25 index to disk.
        
        Args:
            name: Name for the index file
        """
        index_data = {
            'doc_freqs': dict(self.doc_freqs),
            'idf': self.idf,
            'doc_len': self.doc_len,
            'avg_doc_len': self.avg_doc_len,
            'corpus_size': self.corpus_size,
            'documents': self.documents,
            'term_doc_index': {k: list(v) for k, v in self.term_doc_index.items()},
            'k1': self.k1,
            'b': self.b
        }
        
        index_file = self.cache_dir / f'{name}.pkl'
        with open(index_file, 'wb') as f:
            pickle.dump(index_data, f)
    
    def load_index(self, name: str = 'bm25_index'):
        """Load the BM25 index from disk.
        
        Args:
            name: Name of the index file
        """
        index_file = self.cache_dir / f'{name}.pkl'
        if not index_file.exists():
            raise FileNotFoundError(f"BM25 index file not found: {index_file}")
        
        with open(index_file, 'rb') as f:
            index_data = pickle.load(f)
        
        self.doc_freqs = defaultdict(int, index_data['doc_freqs'])
        self.idf = index_data['idf']
        self.doc_len = index_data['doc_len']
        self.avg_doc_len = index_data['avg_doc_len']
        self.corpus_size = index_data['corpus_size']
        self.documents = index_data['documents']
        self.term_doc_index = defaultdict(list, index_data['term_doc_index'])
        self.k1 = index_data['k1']
        self.b = index_data['b']
    
    def clear_index(self):
        """Clear the current index."""
        self.doc_freqs.clear()
        self.idf.clear()
        self.doc_len.clear()
        self.avg_doc_len = 0
        self.corpus_size = 0
        self.documents.clear()
        self.term_doc_index.clear()
    
    def get_document(self, doc_id: str) -> Dict:
        """Get document by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document dictionary with text and metadata
        """
        return self.documents.get(doc_id)
    
    def get_statistics(self) -> Dict:
        """Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            'corpus_size': self.corpus_size,
            'avg_doc_len': self.avg_doc_len,
            'total_terms': len(self.doc_freqs),
            'k1': self.k1,
            'b': self.b
        }