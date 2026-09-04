"""BM25 sparse search implementation for keyword-based retrieval."""

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


class BM25Search:
    """BM25 sparse search for keyword-based retrieval."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 search.
        
        Args:
            k1: Term frequency saturation parameter
            b: Length normalization parameter
        """
        self.k1 = k1
        self.b = b
        self.documents = []
        self.doc_lengths = []
        self.avg_doc_length = 0
        self.doc_freqs = defaultdict(int)
        self.term_doc_map = defaultdict(list)  # term -> list of (doc_id, term_freq)
        self.total_docs = 0
        
    def add_documents(self, documents: list[dict[str, Any]]):
        """
        Add documents to the BM25 index.
        
        Args:
            documents: List of documents with 'id' and 'text' fields
        """
        self.documents = documents
        self.total_docs = len(documents)
        
        # Calculate document lengths and term frequencies
        self.doc_lengths = []
        for doc in documents:
            text = doc.get('text', '')
            terms = self._tokenize(text)
            self.doc_lengths.append(len(terms))
            
            # Build term-document map
            term_freq = defaultdict(int)
            for term in terms:
                term_freq[term] += 1
            
            for term, freq in term_freq.items():
                self.term_doc_map[term].append((doc['id'], freq))
                self.doc_freqs[term] += 1
        
        # Calculate average document length
        if self.doc_lengths:
            self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths)
    
    def _tokenize(self, text: str) -> list[str]:
        """
        Simple tokenization.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Simple whitespace tokenization (can be enhanced)
        text = text.lower()
        tokens = text.split()
        return tokens
    
    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """
        Search using BM25 algorithm.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of search results with scores
        """
        query_terms = self._tokenize(query)
        scores = defaultdict(float)
        
        for term in query_terms:
            if term not in self.term_doc_map:
                continue
            
            # Calculate IDF
            df = self.doc_freqs[term]
            idf = math.log((self.total_docs - df + 0.5) / (df + 0.5) + 1.0)
            
            # Calculate term frequency scores for each document
            for doc_id, term_freq in self.term_doc_map[term]:
                doc_idx = next(i for i, doc in enumerate(self.documents) if doc['id'] == doc_id)
                doc_length = self.doc_lengths[doc_idx]
                
                # BM25 formula
                numerator = term_freq * (self.k1 + 1)
                denominator = term_freq + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)
                scores[doc_id] += idf * (numerator / denominator)
        
        # Sort by score and return top_k
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        results = []
        for doc_id, score in sorted_results:
            doc = next(doc for doc in self.documents if doc['id'] == doc_id)
            results.append({
                'id': doc_id,
                'score': score,
                'text': doc.get('text', ''),
                'metadata': doc.get('metadata', {})
            })
        
        return results
    
    def save_index(self, index_path: Path):
        """
        Save BM25 index to disk.
        
        Args:
            index_path: Path to save the index
        """
        index_data = {
            'documents': self.documents,
            'doc_lengths': self.doc_lengths,
            'avg_doc_length': self.avg_doc_length,
            'doc_freqs': dict(self.doc_freqs),
            'term_doc_map': {k: v for k, v in self.term_doc_map.items()},
            'total_docs': self.total_docs,
            'k1': self.k1,
            'b': self.b
        }
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def load_index(self, index_path: Path):
        """
        Load BM25 index from disk.
        
        Args:
            index_path: Path to load the index from
        """
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        self.documents = index_data['documents']
        self.doc_lengths = index_data['doc_lengths']
        self.avg_doc_length = index_data['avg_doc_length']
        self.doc_freqs = defaultdict(int, index_data['doc_freqs'])
        self.term_doc_map = defaultdict(list, index_data['term_doc_map'])
        self.total_docs = index_data['total_docs']
        self.k1 = index_data['k1']
        self.b = index_data['b']