"""Advanced graph analysis for knowledge graph insights."""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class AnalysisType(Enum):
    """Types of graph analysis."""
    NEIGHBORHOOD = "neighborhood"  # Node neighborhood analysis
    PATH = "path"  # Path analysis between nodes
    CENTRALITY = "centrality"  # Centrality measures
    COMMUNITY = "community"  # Community detection
    CONNECTIVITY = "connectivity"  # Connectivity analysis


@dataclass
class GraphNode:
    """Graph node data structure."""
    node_id: str
    label: str
    node_type: str
    degree: int = 0
    betweenness: float = 0.0
    closeness: float = 0.0
    pagerank: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'node_id': self.node_id,
            'label': self.label,
            'node_type': self.node_type,
            'degree': self.degree,
            'betweenness': self.betweenness,
            'closeness': self.closeness,
            'pagerank': self.pagerank,
            'metadata': self.metadata
        }


@dataclass
class GraphPath:
    """Graph path data structure."""
    path_id: str
    source_node: str
    target_node: str
    path_nodes: List[str]
    path_length: int
    path_weight: float
    intermediate_nodes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'path_id': self.path_id,
            'source_node': self.source_node,
            'target_node': self.target_node,
            'path_nodes': self.path_nodes,
            'path_length': self.path_length,
            'path_weight': self.path_weight,
            'intermediate_nodes': self.intermediate_nodes
        }


class AdvancedGraphAnalyzer:
    """Advanced analyzer for knowledge graph insights."""
    
    def __init__(self):
        """Initialize graph analyzer."""
        from rag_kb.config import settings
        self.graph_file = settings.data_dir / 'lightrag_output' / 'graph_index.json'
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[Dict[str, Any]] = []
        self._load_graph()
    
    def _load_graph(self):
        """Load graph data from file."""
        if self.graph_file.exists():
            try:
                with open(self.graph_file, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                    
                    # Load nodes
                    for node_data in graph_data.get('nodes', []):
                        node = GraphNode(
                            node_id=node_data.get('id', ''),
                            label=node_data.get('label', ''),
                            node_type=node_data.get('type', 'default'),
                            metadata=node_data.get('metadata', {})
                        )
                        self.nodes[node.node_id] = node
                    
                    # Load edges
                    self.edges = graph_data.get('edges', [])
                    
                    # Calculate node degrees
                    self._calculate_degrees()
                    
            except Exception as e:
                print(f"Error loading graph: {e}")
    
    def _calculate_degrees(self):
        """Calculate node degrees from edges."""
        for node in self.nodes.values():
            node.degree = 0
        
        for edge in self.edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            
            if source in self.nodes:
                self.nodes[source].degree += 1
            if target in self.nodes:
                self.nodes[target].degree += 1
    
    def get_neighborhood(self, node_id: str, degree: int = 2) -> Dict[str, Any]:
        """Get neighborhood of a node.
        
        Args:
            node_id: Node ID
            degree: Neighborhood degree (1, 2, 3)
            
        Returns:
            Neighborhood analysis
        """
        if node_id not in self.nodes:
            return {
                'error': f'Node {node_id} not found',
                'neighborhood': []
            }
        
        neighborhood = set([node_id])
        current_level = [node_id]
        
        for _ in range(degree):
            next_level = []
            for current_node in current_level:
                # Find neighbors
                neighbors = self._get_direct_neighbors(current_node)
                for neighbor in neighbors:
                    if neighbor not in neighborhood:
                        neighborhood.add(neighbor)
                        next_level.append(neighbor)
            current_level = next_level
        
        neighborhood_nodes = [
            self.nodes[node_id].to_dict()
            for node_id in neighborhood
            if node_id in self.nodes
        ]
        
        return {
            'center_node': node_id,
            'neighborhood_degree': degree,
            'node_count': len(neighborhood),
            'nodes': neighborhood_nodes
        }
    
    def _get_direct_neighbors(self, node_id: str) -> List[str]:
        """Get direct neighbors of a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            List of neighbor node IDs
        """
        neighbors = []
        
        for edge in self.edges:
            if edge.get('source') == node_id:
                neighbors.append(edge.get('target', ''))
            elif edge.get('target') == node_id:
                neighbors.append(edge.get('source', ''))
        
        return neighbors
    
    def find_shortest_path(self, source_node: str, target_node: str) -> Optional[GraphPath]:
        """Find shortest path between two nodes using BFS.
        
        Args:
            source_node: Source node ID
            target_node: Target node ID
            
        Returns:
            Graph path or None
        """
        if source_node not in self.nodes or target_node not in self.nodes:
            return None
        
        # BFS to find shortest path
        from collections import deque
        
        queue = deque([(source_node, [source_node])])
        visited = {source_node}
        
        while queue:
            current_node, path = queue.popleft()
            
            if current_node == target_node:
                return GraphPath(
                    path_id=f"path_{source_node}_{target_node}",
                    source_node=source_node,
                    target_node=target_node,
                    path_nodes=path,
                    path_length=len(path) - 1,
                    path_weight=len(path) - 1,
                    intermediate_nodes=path[1:-1]
                )
            
            for neighbor in self._get_direct_neighbors(current_node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def analyze_entity_relationships(self, entity_id: str, max_degree: int = 3) -> Dict[str, Any]:
        """Analyze relationships for an entity with 2-3 degree connections.
        
        Args:
            entity_id: Entity node ID
            max_degree: Maximum degree to analyze
            
        Returns:
            Relationship analysis
        """
        if entity_id not in self.nodes:
            return {
                'error': f'Entity {entity_id} not found',
                'relationships': []
            }
        
        relationships = []
        
        for degree in range(1, max_degree + 1):
            neighborhood = self.get_neighborhood(entity_id, degree)
            
            for node in neighborhood['nodes']:
                if node['node_id'] != entity_id:
                    relationship = {
                        'degree': degree,
                        'related_entity': node['node_id'],
                        'entity_label': node['label'],
                        'entity_type': node['node_type'],
                        'connection_strength': self._calculate_connection_strength(entity_id, node['node_id'])
                    }
                    relationships.append(relationship)
        
        return {
            'entity_id': entity_id,
            'entity_label': self.nodes[entity_id].label,
            'total_connections': len(relationships),
            'relationships': relationships
        }
    
    def _calculate_connection_strength(self, node1: str, node2: str) -> float:
        """Calculate connection strength between two nodes.
        
        Args:
            node1: First node ID
            node2: Second node ID
            
        Returns:
            Connection strength (0-1)
        """
        # Check if directly connected
        directly_connected = False
        for edge in self.edges:
            if (edge.get('source') == node1 and edge.get('target') == node2) or \
               (edge.get('source') == node2 and edge.get('target') == node1):
                directly_connected = True
                break
        
        if directly_connected:
            return 1.0
        
        # Calculate based on degree and shared neighbors
        neighbors1 = set(self._get_direct_neighbors(node1))
        neighbors2 = set(self._get_direct_neighbors(node2))
        
        shared_neighbors = len(neighbors1 & neighbors2)
        total_neighbors = len(neighbors1 | neighbors2)
        
        if total_neighbors == 0:
            return 0.0
        
        return shared_neighbors / total_neighbors
    
    def find_paths_between_entities(self, entity1: str, entity2: str, 
                                   max_paths: int = 5) -> List[Dict[str, Any]]:
        """Find multiple paths between two entities.
        
        Args:
            entity1: First entity ID
            entity2: Second entity ID
            max_paths: Maximum number of paths to find
            
        Returns:
            List of paths
        """
        paths = []
        
        # Find shortest path
        shortest_path = self.find_shortest_path(entity1, entity2)
        if shortest_path:
            paths.append(shortest_path.to_dict())
        
        # In a real implementation, you'd find alternative paths
        # For now, return just the shortest path
        
        return paths
    
    def get_centrality_measures(self) -> Dict[str, Any]:
        """Calculate centrality measures for all nodes.
        
        Returns:
            Centrality measures
        """
        if not self.nodes:
            return {'nodes': []}
        
        # Calculate degree centrality (normalized)
        max_degree = max(node.degree for node in self.nodes.values()) if self.nodes else 1
        
        for node in self.nodes.values():
            node.degree_centrality = node.degree / max_degree if max_degree > 0 else 0.0
        
        # Calculate PageRank (simplified)
        damping_factor = 0.85
        iterations = 100
        
        # Initialize PageRank
        n = len(self.nodes)
        pagerank = {node_id: 1.0 / n for node_id in self.nodes}
        
        for _ in range(iterations):
            new_pagerank = {}
            for node_id in self.nodes:
                rank_sum = 0.0
                for neighbor in self._get_direct_neighbors(node_id):
                    neighbor_degree = self.nodes[neighbor].degree
                    if neighbor_degree > 0:
                        rank_sum += pagerank[neighbor] / neighbor_degree
                
                new_pagerank[node_id] = (1 - damping_factor) / n + damping_factor * rank_sum
            
            pagerank = new_pagerank
        
        # Update PageRank in nodes
        for node_id, score in pagerank.items():
            if node_id in self.nodes:
                self.nodes[node_id].pagerank = score
        
        return {
            'nodes': [
                {
                    'node_id': node.node_id,
                    'label': node.label,
                    'degree_centrality': node.degree_centrality,
                    'pagerank': node.pagerank
                }
                for node in self.nodes.values()
            ]
        }
    
    def detect_communities(self) -> Dict[str, Any]:
        """Detect communities in the graph (simplified).
        
        Returns:
            Community detection results
        """
        # Simplified community detection based on connectivity
        communities = []
        visited = set()
        
        for node_id in self.nodes:
            if node_id not in visited:
                # Start a new community
                community = [node_id]
                visited.add(node_id)
                
                # BFS to find connected component
                queue = [node_id]
                while queue:
                    current = queue.pop(0)
                    for neighbor in self._get_direct_neighbors(current):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            community.append(neighbor)
                            queue.append(neighbor)
                
                communities.append({
                    'community_id': f"community_{len(communities)}",
                    'nodes': community,
                    'size': len(community)
                })
        
        return {
            'total_communities': len(communities),
            'communities': communities
        }


# Global instance
graph_analyzer = AdvancedGraphAnalyzer()