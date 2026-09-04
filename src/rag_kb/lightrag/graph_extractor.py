"""LightRAG knowledge graph extraction and visualization utilities."""

import json
from collections import defaultdict
from pathlib import Path

import networkx as nx


class LightRAGGraphExtractor:
    """Extract and process knowledge graph data from LightRAG storage."""
    
    def __init__(self, working_dir: Path):
        """Initialize graph extractor.
        
        Args:
            working_dir: LightRAG working directory
        """
        self.working_dir = Path(working_dir)
        self.graph_data = None
        self._load_graph_data()
    
    def _load_graph_data(self):
        """Load graph data from LightRAG storage files."""
        self.graph_data = {
            'nodes': [],
            'edges': [],
            'metadata': {}
        }
        
        # Try to load from various LightRAG storage formats
        vdb_dir = self.working_dir / 'vdb'
        kv_dir = self.working_dir / 'kv_store'
        graph_dir = self.working_dir / 'graph'
        
        # Try to parse LightRAG's JSON-based storage
        for data_dir in [vdb_dir, kv_dir, graph_dir]:
            if data_dir.exists():
                self._parse_directory(data_dir)
        
        # If no data found, try to extract from LightRAG's internal format
        if not self.graph_data['nodes'] and not self.graph_data['edges']:
            self._extract_from_lightrag_format()
    
    def _parse_directory(self, directory: Path):
        """Parse JSON files in a directory for graph data.
        
        Args:
            directory: Directory to parse
        """
        for json_file in directory.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._extract_entities_and_relations(data, str(json_file))
            except Exception as e:
                print(f"Error parsing {json_file}: {e}")
    
    def _extract_entities_and_relations(self, data: dict, source: str):
        """Extract entities and relations from LightRAG data.
        
        Args:
            data: JSON data from LightRAG
            source: Source file path
        """
        # LightRAG stores entities and relations in various formats
        # This is a generalized parser that handles common patterns
        
        if isinstance(data, dict):
            # Extract entities
            if 'entities' in data:
                for entity_id, entity_data in data['entities'].items():
                    self._add_entity(entity_id, entity_data, source)
            
            # Extract relations
            if 'relations' in data:
                for relation_data in data['relations']:
                    self._add_relation(relation_data, source)
            
            # Try to extract from nested structures
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self._extract_entities_and_relations(value, source)
        
        elif isinstance(data, list):
            for item in data:
                self._extract_entities_and_relations(item, source)
    
    def _add_entity(self, entity_id: str, entity_data: dict, source: str):
        """Add an entity to the graph data.
        
        Args:
            entity_id: Entity identifier
            entity_data: Entity data dictionary
            source: Source file
        """
        # Check if entity already exists
        existing = next((n for n in self.graph_data['nodes'] if n['id'] == entity_id), None)
        
        if existing:
            # Update existing entity
            existing['metadata'].update(entity_data)
            existing['sources'].add(source)
        else:
            # Add new entity
            self.graph_data['nodes'].append({
                'id': entity_id,
                'label': entity_data.get('name', entity_id),
                'type': entity_data.get('type', 'entity'),
                'metadata': entity_data,
                'sources': {source},
                'degree': 0
            })
    
    def _add_relation(self, relation_data: dict, source: str):
        """Add a relation to the graph data.
        
        Args:
            relation_data: Relation data dictionary
            source: Source file
        """
        # Extract source and target entities
        source_entity = relation_data.get('source')
        target_entity = relation_data.get('target')
        relation_type = relation_data.get('relation', 'related_to')
        
        if not source_entity or not target_entity:
            return
        
        # Check if relation already exists
        existing = next(
            (e for e in self.graph_data['edges'] 
             if e['source'] == source_entity and e['target'] == target_entity),
            None
        )
        
        if existing:
            # Update existing relation
            existing['sources'].add(source)
            existing['weight'] += 1
        else:
            # Add new relation
            self.graph_data['edges'].append({
                'source': source_entity,
                'target': target_entity,
                'label': relation_type,
                'type': relation_type,
                'weight': 1,
                'metadata': relation_data,
                'sources': {source}
            })
    
    def _extract_from_lightrag_format(self):
        """Extract graph data from LightRAG's internal storage format."""
        # LightRAG uses NetworkX for graph storage
        try:
            import networkx as nx
            
            # Try to load NetworkX graph files
            graph_files = list(self.working_dir.glob('*.graphml'))
            if not graph_files:
                graph_files = list(self.working_dir.glob('*.gml'))
            
            for graph_file in graph_files:
                try:
                    if graph_file.suffix == '.graphml':
                        G = nx.read_graphml(graph_file)
                    else:
                        G = nx.read_gml(graph_file)
                    
                    # Convert NetworkX graph to our format
                    for node_id, node_data in G.nodes(data=True):
                        self.graph_data['nodes'].append({
                            'id': str(node_id),
                            'label': node_data.get('name', str(node_id)),
                            'type': node_data.get('type', 'entity'),
                            'metadata': dict(node_data),
                            'sources': {str(graph_file)},
                            'degree': G.degree(node_id)
                        })
                    
                    for source, target, edge_data in G.edges(data=True):
                        self.graph_data['edges'].append({
                            'source': str(source),
                            'target': str(target),
                            'label': edge_data.get('relation', 'related_to'),
                            'type': edge_data.get('type', 'relation'),
                            'weight': edge_data.get('weight', 1),
                            'metadata': dict(edge_data),
                            'sources': {str(graph_file)}
                        })
                        
                except Exception as e:
                    print(f"Error loading graph file {graph_file}: {e}")
                    
        except ImportError:
            print("NetworkX not available for graph extraction")
    
    def get_graph_data(self) -> dict:
        """Get the complete graph data.
        
        Returns:
            Dictionary with nodes, edges, and metadata
        """
        # Convert sets to lists for JSON serialization
        graph_data = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'total_nodes': len(self.graph_data['nodes']),
                'total_edges': len(self.graph_data['edges']),
                'working_dir': str(self.working_dir)
            }
        }
        
        for node in self.graph_data['nodes']:
            node_copy = node.copy()
            node_copy['sources'] = list(node['sources'])
            graph_data['nodes'].append(node_copy)
        
        for edge in self.graph_data['edges']:
            edge_copy = edge.copy()
            edge_copy['sources'] = list(edge['sources'])
            graph_data['edges'].append(edge_copy)
        
        return graph_data
    
    def get_networkx_graph(self) -> nx.Graph:
        """Convert extracted data to NetworkX graph.
        
        Returns:
            NetworkX Graph object
        """
        G = nx.Graph()
        
        # Add nodes
        for node in self.graph_data['nodes']:
            G.add_node(node['id'], **node['metadata'])
        
        # Add edges
        for edge in self.graph_data['edges']:
            G.add_edge(edge['source'], edge['target'], **edge['metadata'])
        
        return G
    
    def get_statistics(self) -> dict:
        """Get graph statistics.
        
        Returns:
            Dictionary with graph statistics
        """
        if not self.graph_data['nodes']:
            return {
                'total_nodes': 0,
                'total_edges': 0,
                'node_types': {},
                'relation_types': {},
                'avg_degree': 0,
                'connected_components': 0
            }
        
        # Calculate statistics
        node_types = defaultdict(int)
        for node in self.graph_data['nodes']:
            node_types[node['type']] += 1
        
        relation_types = defaultdict(int)
        for edge in self.graph_data['edges']:
            relation_types[edge['type']] += 1
        
        degrees = [node['degree'] for node in self.graph_data['nodes']]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        
        try:
            G = self.get_networkx_graph()
            connected_components = nx.number_connected_components(G)
        except:
            connected_components = 0
        
        return {
            'total_nodes': len(self.graph_data['nodes']),
            'total_edges': len(self.graph_data['edges']),
            'node_types': dict(node_types),
            'relation_types': dict(relation_types),
            'avg_degree': avg_degree,
            'connected_components': connected_components
        }
    
    def filter_by_entity_type(self, entity_type: str) -> dict:
        """Filter graph data by entity type.
        
        Args:
            entity_type: Entity type to filter by
            
        Returns:
            Filtered graph data
        """
        filtered_nodes = [n for n in self.graph_data['nodes'] if n['type'] == entity_type]
        node_ids = {n['id'] for n in filtered_nodes}
        filtered_edges = [e for e in self.graph_data['edges'] 
                         if e['source'] in node_ids and e['target'] in node_ids]
        
        return {
            'nodes': filtered_nodes,
            'edges': filtered_edges,
            'metadata': {
                'filter_type': entity_type,
                'total_nodes': len(filtered_nodes),
                'total_edges': len(filtered_edges)
            }
        }
    
    def get_neighborhood(self, entity_id: str, depth: int = 1) -> dict:
        """Get the neighborhood of an entity in the graph.
        
        Args:
            entity_id: Entity identifier
            depth: Neighborhood depth (default: 1)
            
        Returns:
            Graph data for the neighborhood
        """
        try:
            G = self.get_networkx_graph()
            if entity_id not in G:
                return {'nodes': [], 'edges': [], 'metadata': {'error': 'Entity not found'}}
            
            # Get ego graph
            ego_graph = nx.ego_graph(G, entity_id, radius=depth)
            
            # Convert to our format
            nodes = []
            edges = []
            
            for node_id, node_data in ego_graph.nodes(data=True):
                original_node = next((n for n in self.graph_data['nodes'] if n['id'] == node_id), None)
                if original_node:
                    nodes.append(original_node)
            
            for source, target, edge_data in ego_graph.edges(data=True):
                original_edge = next(
                    (e for e in self.graph_data['edges'] 
                     if e['source'] == source and e['target'] == target),
                    None
                )
                if original_edge:
                    edges.append(original_edge)
            
            return {
                'nodes': nodes,
                'edges': edges,
                'metadata': {
                    'center_entity': entity_id,
                    'depth': depth,
                    'total_nodes': len(nodes),
                    'total_edges': len(edges)
                }
            }
            
        except Exception as e:
            return {
                'nodes': [],
                'edges': [],
                'metadata': {'error': str(e)}
            }
    
    def save_graph_data(self, output_file: Path):
        """Save graph data to JSON file.
        
        Args:
            output_file: Output file path
        """
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        graph_data = self.get_graph_data()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)