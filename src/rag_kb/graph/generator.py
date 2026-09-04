"""
Knowledge Graph Generator
Simplified implementation for generating knowledge graphs from uploaded documents
"""

import json
from pathlib import Path
from typing import Any
from difflib import SequenceMatcher
from collections import defaultdict

from rag_kb.config import settings
from rag_kb.lightrag.adapter import LightRAGAdapter


class KnowledgeGraphGenerator:
    """Generate knowledge graphs from documents using LightRAG"""
    
    def __init__(self):
        self.rag = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the knowledge graph generator"""
        if not self._initialized:
            self.rag = LightRAGAdapter()
            await self.rag.ensure_initialized()
            self._initialized = True
    
    async def generate_graph_from_documents(self, documents: list[dict[str, Any]], use_simple_graph: bool = True) -> dict[str, Any]:
        """Generate knowledge graph from uploaded documents.
        
        Args:
            documents: List of document dictionaries with 'doc_id', 'content', and 'metadata'
            use_simple_graph: If True, prefer simple document-based graph with proper naming
            
        Returns:
            Knowledge graph data with nodes and edges
        """
        await self.initialize()
        
        try:
            import sys
            print(f"Starting graph generation from {len(documents)} documents", file=sys.stderr, flush=True)
            
            # If use_simple_graph is True, directly use simple graph with proper naming
            if use_simple_graph:
                print("Using simple document-based graph with proper naming", file=sys.stderr, flush=True)
                return await self._create_simple_graph(documents)
            
            # Otherwise, try LightRAG graph extraction
            # Ingest documents into LightRAG (this triggers graph extraction)
            success = await self.rag.ingest(documents)
            
            print(f"Graph ingestion result: {success}", file=sys.stderr, flush=True)
            
            if not success:
                print("Document ingestion failed, using fallback graph", file=sys.stderr, flush=True)
                # Fallback to simple document-based graph
                return await self._create_simple_graph(documents)
            
            # Extract graph data from LightRAG
            graph_data = await self._extract_graph_data()
            
            print(f"Graph extraction completed: {graph_data.get('node_count', 0)} nodes, {graph_data.get('edge_count', 0)} edges", file=sys.stderr, flush=True)
            
            # If no entities found, use fallback
            if graph_data.get('node_count', 0) == 0:
                print("No entities found, using fallback graph", file=sys.stderr, flush=True)
                return await self._create_simple_graph(documents)
            
            return {
                'success': True,
                **graph_data
            }
            
        except Exception as e:
            import traceback
            print(f"Graph generation error: {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            # Fallback to simple document-based graph
            return await self._create_simple_graph(documents)
    
    async def _extract_graph_data(self) -> dict[str, Any]:
        """Extract graph data from LightRAG storage"""
        try:
            # Read entity and relation data
            entities_file = Path(settings.lightrag_working_dir) / 'kv_store_full_entities.json'
            relations_file = Path(settings.lightrag_working_dir) / 'kv_store_full_relations.json'
            
            # Also read document registry for name mapping
            registry_file = Path(settings.data_dir) / 'document_registry.json'
            doc_name_mapping = {}
            registry = {}
            
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                    for doc_id, doc_data in registry.items():
                        # Try multiple sources for title
                        title = (
                            doc_data.get('title') or  # Top-level title
                            doc_data.get('metadata', {}).get('title') or  # Metadata title
                            doc_data.get('metadata', {}).get('filename') or  # Metadata filename
                            doc_id  # Fallback to doc_id
                        )
                        doc_name_mapping[doc_id] = title
            
            # Also read LightRAG's full_docs for ID mapping via content matching
            full_docs_file = Path(settings.lightrag_working_dir) / 'kv_store_full_docs.json'
            lightrag_id_mapping = {}
            
            if full_docs_file.exists() and registry:
                with open(full_docs_file, 'r', encoding='utf-8') as f:
                    full_docs = json.load(f)
                    # Map LightRAG doc-xxx IDs to original doc IDs via content matching
                    for lightrag_id, doc_data in full_docs.items():
                        content = doc_data.get('content', '')
                        # Find matching document in registry by content
                        for reg_doc_id, reg_data in registry.items():
                            if reg_data.get('content', '') == content:
                                lightrag_id_mapping[lightrag_id] = reg_doc_id
                                break
            
            entities = []
            edges = []
            
            if entities_file.exists():
                with open(entities_file, 'r', encoding='utf-8') as f:
                    entity_data = json.load(f)
                    for entity_id, entity_info in entity_data.items():
                        # Try to get meaningful name
                        entity_names = entity_info.get('entity_names', [])
                        if entity_names:
                            entity_name = entity_names[0]  # Use first entity name
                        else:
                            # Try to map LightRAG ID to original doc ID
                            original_doc_id = lightrag_id_mapping.get(entity_id, entity_id)
                            # Fallback to document name mapping or use ID
                            entity_name = doc_name_mapping.get(original_doc_id, doc_name_mapping.get(entity_id, entity_id))
                        
                        # Clean up the name
                        if entity_name.startswith('doc-'):
                            # Try to get the actual document name
                            original_doc_id = lightrag_id_mapping.get(entity_name, entity_name)
                            entity_name = doc_name_mapping.get(original_doc_id, entity_name)
                        
                        entities.append({
                            'id': entity_id,
                            'name': entity_name,
                            'type': entity_info.get('entity_type', 'document'),
                            'description': entity_info.get('description', f'Document: {entity_name}'),
                            'metadata': entity_info
                        })
            
            if relations_file.exists():
                with open(relations_file, 'r', encoding='utf-8') as f:
                    relation_data = json.load(f)
                    for relation_id, relation_info in relation_data.items():
                        # Get meaningful names for source and target
                        source = relation_info.get('source', '')
                        target = relation_info.get('target', '')
                        
                        # Map LightRAG IDs to original doc IDs
                        source_original = lightrag_id_mapping.get(source, source)
                        target_original = lightrag_id_mapping.get(target, target)
                        
                        # Map to names
                        source_name = doc_name_mapping.get(source_original, doc_name_mapping.get(source, source))
                        target_name = doc_name_mapping.get(target_original, doc_name_mapping.get(target, target))
                        
                        edges.append({
                            'id': relation_id,
                            'source': source,
                            'source_name': source_name if source_name and source_name != source else source,
                            'target': target,
                            'target_name': target_name if target_name and target_name != target else target,
                            'type': relation_info.get('relation_type', 'related_to'),
                            'description': f'{source_name if source_name and source_name != source else source} -> {target_name if target_name and target_name != target else target}',
                            'metadata': relation_info
                        })
            
            # If no entities found, create a simple document-based graph
            if not entities:
                return await self._create_simple_graph()
            
            return {
                'nodes': entities,
                'edges': edges,
                'node_count': len(entities),
                'edge_count': len(edges),
                'message': f'Graph extracted with {len(entities)} entities and {len(edges)} relations'
            }
            
        except Exception:
            import traceback
            traceback.print_exc()
            # Fallback to simple graph
            return await self._create_simple_graph()
    
    async def _create_simple_graph(self, documents: list[dict[str, Any]] = None) -> dict[str, Any]:
        """Create a simple document-based graph when LightRAG graph extraction fails
        
        Args:
            documents: List of document dictionaries (optional, will load from registry if not provided)
            
        Returns:
            Simple graph data with document nodes
        """
        try:
            import sys
            print("Creating simple document-based graph", file=sys.stderr, flush=True)
            
            # Use provided documents or load from registry
            if documents is None:
                registry_file = Path(settings.data_dir) / 'document_registry.json'
                
                if not registry_file.exists():
                    return {
                        'nodes': [],
                        'edges': [],
                        'node_count': 0,
                        'edge_count': 0,
                        'message': 'No documents found for graph generation'
                    }
                
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                
                # Convert to document format
                documents = []
                for doc_id, doc_data in registry.items():
                    documents.append({
                        'doc_id': doc_id,
                        'content': doc_data.get('content', ''),
                        'metadata': doc_data.get('metadata', {}),
                        'title': doc_data.get('title', doc_id)  # Add title at top level
                    })
            
            # Create simple document nodes
            nodes = []
            edges = []
            
            for doc in documents:
                doc_id = doc.get('doc_id', '')
                metadata = doc.get('metadata', {})
                
                # Try multiple sources for a meaningful name
                title = (
                    doc.get('title') or  # Top-level title
                    metadata.get('title') or  # Metadata title
                    metadata.get('filename') or  # Metadata filename
                    metadata.get('source') or  # Source field
                    doc_id  # Fallback to doc_id
                )
                
                # Clean up the title - remove common prefixes
                title = title.removeprefix('doc-')  # Remove 'doc-' prefix
                
                # If still looks like a hash, use a more readable format
                if len(title) == 32 and all(c in '0123456789abcdef' for c in title.lower()):
                    title = f"Document_{title[:8]}"  # Use first 8 chars of hash
                
                nodes.append({
                    'id': doc_id,
                    'name': title,
                    'type': 'document',
                    'description': f'Document: {title}',
                    'metadata': metadata
                })
            
            # Create intelligent edges between documents based on content similarity
            if len(nodes) > 1:
                edges = self._create_smart_edges(documents, nodes)
            
            print(f"Smart graph created with {len(nodes)} documents and {len(edges)} intelligent edges", file=sys.stderr, flush=True)
            
            print(f"Smart graph created with {len(nodes)} documents and {len(edges)} intelligent edges", file=sys.stderr, flush=True)
            
            return {
                'success': True,
                'nodes': nodes,
                'edges': edges,
                'node_count': len(nodes),
                'edge_count': len(edges),
                'message': f'Smart graph created with {len(nodes)} documents and {len(edges)} intelligent edges'
            }
            
        except Exception as e:
            import traceback
            print(f"Simple graph creation failed: {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            return {
                'success': False,
                'nodes': [],
                'edges': [],
                'node_count': 0,
                'edge_count': 0,
                'message': f'Graph creation failed: {e!s}'
            }
    
    def _create_smart_edges(self, documents: list[dict[str, Any]], nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Create intelligent edges between documents based on content similarity.
        
        Args:
            documents: List of document dictionaries
            nodes: List of node dictionaries
            
        Returns:
            List of edge dictionaries with similarity scores
        """
        edges = []
        similarity_threshold = 0.15  # Minimum similarity to create an edge
        max_edges_per_node = 5  # Limit edges per node to avoid clutter
        
        # Calculate pairwise similarity between documents
        similarity_matrix = []
        for i, doc1 in enumerate(documents):
            content1 = doc1.get('content', '')
            similarities = []
            for j, doc2 in enumerate(documents):
                if i == j:
                    similarities.append(0.0)
                    continue
                content2 = doc2.get('content', '')
                similarity = self._calculate_content_similarity(content1, content2)
                similarities.append(similarity)
            similarity_matrix.append(similarities)
        
        # Create edges based on similarity
        edge_count = defaultdict(int)
        
        for i in range(len(documents)):
            # Get top similar documents for this document
            similarities_with_indices = [(j, similarity_matrix[i][j]) for j in range(len(documents)) if i != j]
            similarities_with_indices.sort(key=lambda x: x[1], reverse=True)
            
            # Create edges for top similar documents
            for j, similarity in similarities_with_indices[:max_edges_per_node]:
                if similarity >= similarity_threshold:
                    # Check if edge already exists (avoid duplicates)
                    edge_exists = any(
                        (e['source'] == nodes[i]['id'] and e['target'] == nodes[j]['id']) or
                        (e['source'] == nodes[j]['id'] and e['target'] == nodes[i]['id'])
                        for e in edges
                    )
                    
                    if not edge_exists and edge_count[nodes[i]['id']] < max_edges_per_node:
                        edge_type = self._determine_edge_type(similarity)
                        edges.append({
                            'id': f"edge_{i}_{j}",
                            'source': nodes[i]['id'],
                            'source_name': nodes[i]['name'],
                            'target': nodes[j]['id'],
                            'target_name': nodes[j]['name'],
                            'type': edge_type,
                            'weight': similarity,
                            'description': f'{nodes[i]["name"]} -> {nodes[j]["name"]} (相似度: {similarity:.2f})',
                            'metadata': {
                                'similarity': similarity,
                                'edge_type': edge_type
                            }
                        })
                        edge_count[nodes[i]['id']] += 1
        
        return edges
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate content similarity between two documents using multiple methods.
        
        Args:
            content1: First document content
            content2: Second document content
            
        Returns:
            Similarity score between 0 and 1
        """
        if not content1 or not content2:
            return 0.0
        
        # Method 1: Text similarity using SequenceMatcher
        text_similarity = SequenceMatcher(None, content1, content2).ratio()
        
        # Method 2: Keyword overlap similarity
        keyword_similarity = self._calculate_keyword_overlap(content1, content2)
        
        # Method 3: Jaccard similarity for word sets
        jaccard_similarity = self._calculate_jaccard_similarity(content1, content2)
        
        # Combine multiple similarity measures with weights
        combined_similarity = (
            0.4 * text_similarity +
            0.3 * keyword_similarity +
            0.3 * jaccard_similarity
        )
        
        # Apply normalization to avoid too many weak connections
        if combined_similarity < 0.1:
            return 0.0
        elif combined_similarity > 0.8:
            return 1.0
        else:
            return combined_similarity
    
    def _calculate_keyword_overlap(self, content1: str, content2: str) -> float:
        """Calculate keyword overlap similarity between two documents.
        
        Args:
            content1: First document content
            content2: Second document content
            
        Returns:
            Keyword overlap similarity score
        """
        # Extract keywords (simple approach: words longer than 3 characters)
        words1 = set(word.lower() for word in content1.split() if len(word) > 3)
        words2 = set(word.lower() for word in content2.split() if len(word) > 3)
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate overlap
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_jaccard_similarity(self, content1: str, content2: str) -> float:
        """Calculate Jaccard similarity between two documents.
        
        Args:
            content1: First document content
            content2: Second document content
            
        Returns:
            Jaccard similarity score
        """
        # Split into character n-grams (trigrams)
        def get_ngrams(text, n=3):
            return set(text[i:i+n] for i in range(len(text)-n+1))
        
        ngrams1 = get_ngrams(content1.lower())
        ngrams2 = get_ngrams(content2.lower())
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = ngrams1.intersection(ngrams2)
        union = ngrams1.union(ngrams2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _determine_edge_type(self, similarity: float) -> str:
        """Determine edge type based on similarity score.
        
        Args:
            similarity: Similarity score between 0 and 1
            
        Returns:
            Edge type string
        """
        if similarity >= 0.7:
            return 'strongly_related'
        elif similarity >= 0.4:
            return 'moderately_related'
        elif similarity >= 0.2:
            return 'weakly_related'
        else:
            return 'related'
    
    async def get_entity_subgraph(self, entity_name: str, depth: int = 2) -> dict[str, Any]:
        """Get subgraph centered around a specific entity
        
        Args:
            entity_name: Name of the center entity
            depth: Depth of the subgraph (number of hops)
            
        Returns:
            Subgraph data with nodes and edges
        """
        await self.initialize()
        
        try:
            # Use LightRAG's query to get entity context
            query = f"Tell me about {entity_name} and its relationships"
            result = await self.rag.query(query, mode="local")
            
            # Extract entities and relations from the response
            entities = self._extract_entities_from_response(result)
            relations = self._extract_relations_from_response(result)
            
            return {
                'success': True,
                'center_entity': entity_name,
                'nodes': entities,
                'edges': relations,
                'depth': depth,
                'node_count': len(entities),
                'edge_count': len(relations)
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'center_entity': entity_name,
                'nodes': [],
                'edges': [],
                'depth': depth,
                'node_count': 0,
                'edge_count': 0
            }
    
    def _extract_entities_from_response(self, response: str) -> list[dict[str, Any]]:
        """Extract entities from LLM response"""
        # Simple entity extraction - in production, use more sophisticated NLP
        entities = []
        
        # Look for capitalized words that might be entities
        import re
        potential_entities = re.findall(r'\b[A-Z][a-zA-Z]+\b', response)
        
        for entity in set(potential_entities):
            if len(entity) > 2:  # Filter out short words
                entities.append({
                    'id': f"entity_{entity.lower()}",
                    'name': entity,
                    'type': 'extracted',
                    'description': 'Extracted from response'
                })
        
        return entities[:10]  # Limit to top 10
    
    def _extract_relations_from_response(self, response: str) -> list[dict[str, Any]]:
        """Extract relations from LLM response"""
        relations = []
        
        # Simple relation extraction based on common patterns
        import re
        
        # Look for relationship patterns
        relation_patterns = [
            r'(\w+)\s+(?:is|are|was|were|has|have)\s+(\w+)',
            r'(\w+)\s+(?:related to|connected to|associated with)\s+(\w+)'
        ]
        
        for pattern in relation_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                source, target = match[0], match[1]
                relations.append({
                    'id': f"relation_{source}_{target}",
                    'source': source,
                    'target': target,
                    'type': 'extracted',
                    'description': 'Extracted relationship'
                })
        
        return relations[:10]  # Limit to top 10
    
    async def get_graph_statistics(self) -> dict[str, Any]:
        """Get statistics about the knowledge graph"""
        await self.initialize()
        
        try:
            graph_data = await self._extract_graph_data()
            
            # Calculate additional statistics
            node_types = {}
            for node in graph_data['nodes']:
                node_type = node.get('type', 'unknown')
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            edge_types = {}
            for edge in graph_data['edges']:
                edge_type = edge.get('type', 'unknown')
                edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
            
            return {
                'success': True,
                'node_count': graph_data['node_count'],
                'edge_count': graph_data['edge_count'],
                'node_types': node_types,
                'edge_types': edge_types,
                'message': graph_data['message']
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'node_count': 0,
                'edge_count': 0,
                'node_types': {},
                'edge_types': {}
            }
    
    async def rebuild_graph(self) -> dict[str, Any]:
        """Rebuild the knowledge graph from all documents"""
        await self.initialize()
        
        try:
            # Load all documents from registry
            registry_file = Path(settings.data_dir) / 'document_registry.json'
            
            if not registry_file.exists():
                return {
                    'success': False,
                    'error': 'No document registry found',
                    'nodes': [],
                    'edges': [],
                    'node_count': 0,
                    'edge_count': 0
                }
            
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Convert to document format
            documents = []
            for doc_id, doc_data in registry.items():
                documents.append({
                    'doc_id': doc_id,
                    'content': doc_data.get('content', ''),
                    'metadata': doc_data.get('metadata', {}),
                    'title': doc_data.get('title', doc_id)  # Add title at top level
                })
            
            # Re-ingest documents
            success = await self.rag.ingest(documents)
            
            if success:
                graph_data = await self._extract_graph_data()
                return {
                    'success': True,
                    **graph_data,
                    'message': f'Graph rebuilt from {len(documents)} documents'
                }
            else:
                return {
                    'success': False,
                    'error': 'Document re-ingestion failed',
                    'nodes': [],
                    'edges': [],
                    'node_count': 0,
                    'edge_count': 0
                }
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'nodes': [],
                'edges': [],
                'node_count': 0,
                'edge_count': 0
            }


# Global instance
graph_generator = KnowledgeGraphGenerator()