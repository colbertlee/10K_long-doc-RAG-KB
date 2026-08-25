"""
Knowledge Graph Generator
Simplified implementation for generating knowledge graphs from uploaded documents
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from rag_kb.lightrag.adapter import LightRAGAdapter
from rag_kb.config import settings


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
    
    async def generate_graph_from_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate knowledge graph from uploaded documents
        
        Args:
            documents: List of document dictionaries with 'doc_id', 'content', and 'metadata'
            
        Returns:
            Knowledge graph data with nodes and edges
        """
        await self.initialize()
        
        try:
            import sys
            print(f"Starting graph generation from {len(documents)} documents", file=sys.stderr, flush=True)
            
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
    
    async def _extract_graph_data(self) -> Dict[str, Any]:
        """Extract graph data from LightRAG storage"""
        try:
            # Read entity and relation data
            entities_file = Path(settings.lightrag_working_dir) / 'kv_store_full_entities.json'
            relations_file = Path(settings.lightrag_working_dir) / 'kv_store_full_relations.json'
            
            # Also read document registry for name mapping
            registry_file = Path(settings.data_dir) / 'document_registry.json'
            doc_name_mapping = {}
            
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                    for doc_id, doc_data in registry.items():
                        metadata = doc_data.get('metadata', {})
                        title = metadata.get('title', metadata.get('filename', doc_id))
                        doc_name_mapping[doc_id] = title
            
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
                            # Fallback to document name mapping or use ID
                            entity_name = doc_name_mapping.get(entity_id, entity_id)
                        
                        # Clean up the name
                        if entity_name.startswith('doc-'):
                            # Try to get the actual document name
                            entity_name = doc_name_mapping.get(entity_id, entity_name)
                        
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
                        
                        # Map IDs to names
                        source_name = doc_name_mapping.get(source, source)
                        target_name = doc_name_mapping.get(target, target)
                        
                        edges.append({
                            'id': relation_id,
                            'source': source,
                            'source_name': source_name,
                            'target': target,
                            'target_name': target_name,
                            'type': relation_info.get('relation_type', 'related_to'),
                            'description': relation_info.get('description', f'{source_name} -> {target_name}'),
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
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            # Fallback to simple graph
            return await self._create_simple_graph()
    
    async def _create_simple_graph(self, documents: List[Dict[str, Any]] = None) -> Dict[str, Any]:
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
                        'metadata': doc_data.get('metadata', {})
                    })
            
            # Create simple document nodes
            nodes = []
            edges = []
            
            for doc in documents:
                doc_id = doc.get('doc_id', '')
                metadata = doc.get('metadata', {})
                
                # Try multiple sources for a meaningful name
                title = (
                    metadata.get('title') or 
                    metadata.get('filename') or 
                    metadata.get('source') or 
                    doc_id
                )
                
                # Clean up the title - remove common prefixes
                if title.startswith('doc-'):
                    title = title[4:]  # Remove 'doc-' prefix
                
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
            
            # Create simple edges between documents (if multiple)
            if len(nodes) > 1:
                for i in range(len(nodes) - 1):
                    source_node = nodes[i]
                    target_node = nodes[i + 1]
                    edges.append({
                        'id': f"edge_{i}",
                        'source': source_node['id'],
                        'source_name': source_node['name'],
                        'target': target_node['id'],
                        'target_name': target_node['name'],
                        'type': 'related',
                        'description': f'{source_node["name"]} -> {target_node["name"]}',
                        'metadata': {}
                    })
            
            print(f"Simple graph created with {len(nodes)} documents", file=sys.stderr, flush=True)
            
            return {
                'success': True,
                'nodes': nodes,
                'edges': edges,
                'node_count': len(nodes),
                'edge_count': len(edges),
                'message': f'Simple graph created with {len(nodes)} documents'
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
                'message': f'Graph creation failed: {str(e)}'
            }
    
    async def get_entity_subgraph(self, entity_name: str, depth: int = 2) -> Dict[str, Any]:
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
    
    def _extract_entities_from_response(self, response: str) -> List[Dict[str, Any]]:
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
                    'description': f'Extracted from response'
                })
        
        return entities[:10]  # Limit to top 10
    
    def _extract_relations_from_response(self, response: str) -> List[Dict[str, Any]]:
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
                    'description': f'Extracted relationship'
                })
        
        return relations[:10]  # Limit to top 10
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
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
    
    async def rebuild_graph(self) -> Dict[str, Any]:
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
                    'metadata': doc_data.get('metadata', {})
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