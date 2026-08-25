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
            # Ingest documents into LightRAG (this triggers graph extraction)
            success = await self.rag.ingest(documents)
            
            if not success:
                return {
                    'success': False,
                    'error': 'Document ingestion failed',
                    'nodes': [],
                    'edges': [],
                    'node_count': 0,
                    'edge_count': 0
                }
            
            # Extract graph data from LightRAG
            graph_data = await self._extract_graph_data()
            
            return {
                'success': True,
                **graph_data
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
    
    async def _extract_graph_data(self) -> Dict[str, Any]:
        """Extract graph data from LightRAG storage"""
        try:
            # Read entity and relation data
            entities_file = Path(settings.lightrag_working_dir) / 'kv_store_full_entities.json'
            relations_file = Path(settings.lightrag_working_dir) / 'kv_store_full_relations.json'
            
            entities = []
            edges = []
            
            if entities_file.exists():
                with open(entities_file, 'r', encoding='utf-8') as f:
                    entity_data = json.load(f)
                    for entity_id, entity_info in entity_data.items():
                        entities.append({
                            'id': entity_id,
                            'name': entity_info.get('entity_name', entity_id),
                            'type': entity_info.get('entity_type', 'unknown'),
                            'description': entity_info.get('description', ''),
                            'metadata': entity_info
                        })
            
            if relations_file.exists():
                with open(relations_file, 'r', encoding='utf-8') as f:
                    relation_data = json.load(f)
                    for relation_id, relation_info in relation_data.items():
                        edges.append({
                            'id': relation_id,
                            'source': relation_info.get('source', ''),
                            'target': relation_info.get('target', ''),
                            'type': relation_info.get('relation_type', 'related_to'),
                            'description': relation_info.get('description', ''),
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
    
    async def _create_simple_graph(self) -> Dict[str, Any]:
        """Create a simple document-based graph when LightRAG graph extraction fails"""
        try:
            # Load document registry
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
            
            # Create simple document nodes
            nodes = []
            edges = []
            
            for doc_id, doc_data in registry.items():
                title = doc_data.get('title', doc_id)
                nodes.append({
                    'id': doc_id,
                    'name': title,
                    'type': 'document',
                    'description': f'Document: {title}',
                    'metadata': doc_data
                })
            
            # Create simple edges between documents (if multiple)
            if len(nodes) > 1:
                for i in range(len(nodes) - 1):
                    edges.append({
                        'id': f"edge_{i}",
                        'source': nodes[i]['id'],
                        'target': nodes[i + 1]['id'],
                        'type': 'related',
                        'description': 'Document relationship',
                        'metadata': {}
                    })
            
            return {
                'nodes': nodes,
                'edges': edges,
                'node_count': len(nodes),
                'edge_count': len(edges),
                'message': f'Simple graph created with {len(nodes)} documents'
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
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