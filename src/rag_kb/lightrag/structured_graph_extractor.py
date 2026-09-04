"""Enhanced knowledge graph extractor with structured entity and relationship parsing."""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class Entity:
    """Knowledge graph entity."""
    name: str
    entity_type: str
    description: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'type': self.entity_type,
            'description': self.description
        }


@dataclass
class Relationship:
    """Knowledge graph relationship."""
    source: str
    target: str
    rel_type: str
    description: str
    strength: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'source': self.source,
            'target': self.target,
            'type': self.rel_type,
            'description': self.description,
            'strength': self.strength
        }


class StructuredGraphExtractor:
    """Extract structured entities and relationships from LLM output."""
    
    def __init__(self):
        self.entities: List[Entity] = []
        self.relationships: List[Relationship] = []
    
    def parse_llm_output(self, llm_output: str) -> Tuple[List[Entity], List[Relationship]]:
        """Parse LLM output in the specified format.
        
        Args:
            llm_output: LLM response text
            
        Returns:
            Tuple of (entities, relationships)
        """
        self.entities = []
        self.relationships = []
        
        # Check if output contains the expected format
        if '[Entities]' not in llm_output or '[Relationships]' not in llm_output:
            # Fallback: try to extract from JSON format
            return self._parse_fallback_format(llm_output)
        
        # Extract entities section
        entities_section = self._extract_section(llm_output, '[Entities]', '[Relationships]')
        if entities_section:
            self._parse_entities(entities_section)
        
        # Extract relationships section
        relationships_section = self._extract_section(llm_output, '[Relationships]', '<|COMPLETE|>')
        if relationships_section:
            self._parse_relationships(relationships_section)
        
        return self.entities, self.relationships
    
    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """Extract text between markers.
        
        Args:
            text: Full text
            start_marker: Section start marker
            end_marker: Section end marker
            
        Returns:
            Extracted section text
        """
        start_idx = text.find(start_marker)
        if start_idx == -1:
            return ""
        
        end_idx = text.find(end_marker, start_idx)
        if end_idx == -1:
            return text[start_idx + len(start_marker):]
        
        return text[start_idx + len(start_marker):end_idx].strip()
    
    def _parse_entities(self, entities_text: str):
        """Parse entities from text.
        
        Args:
            entities_text: Entities section text
        """
        # Split by ##
        entity_records = entities_text.split('##')
        
        for record in entity_records:
            record = record.strip()
            if not record or record.startswith('['):
                continue
            
            # Parse the format: ("entity"<|>entity_name<|>entity_type<|>entity_description)
            match = re.search(r'\("entity"<\|>([^<|]+)<\|>([^<|]+)<\|>([^<|]+)\)', record)
            if match:
                entity_name = match.group(1).strip()
                entity_type = match.group(2).strip()
                entity_description = match.group(3).strip()
                
                self.entities.append(Entity(
                    name=entity_name,
                    entity_type=entity_type,
                    description=entity_description
                ))
    
    def _parse_relationships(self, relationships_text: str):
        """Parse relationships from text.
        
        Args:
            relationships_text: Relationships section text
        """
        # Split by ##
        relationship_records = relationships_text.split('##')
        
        for record in relationship_records:
            record = record.strip()
            if not record or record.startswith('['):
                continue
            
            # Parse the format: ("relationship"<|>src_id<|>tgt_id<|>rel_type<|>rel_description<|>rel_strength)
            match = re.search(
                r'\("relationship"<\|>([^<|]+)<\|>([^<|]+)<\|>([^<|]+)<\|>([^<|]+)<\|>(\d+)\)',
                record
            )
            if match:
                src_id = match.group(1).strip()
                tgt_id = match.group(2).strip()
                rel_type = match.group(3).strip()
                rel_description = match.group(4).strip()
                rel_strength = int(match.group(5))
                
                self.relationships.append(Relationship(
                    source=src_id,
                    target=tgt_id,
                    rel_type=rel_type,
                    description=rel_description,
                    strength=rel_strength
                ))
    
    def _parse_fallback_format(self, llm_output: str) -> Tuple[List[Entity], List[Relationship]]:
        """Fallback parser for non-standard formats.
        
        Args:
            llm_output: LLM response text
            
        Returns:
            Tuple of (entities, relationships)
        """
        # Try to parse as JSON
        import json
        try:
            data = json.loads(llm_output)
            
            if isinstance(data, dict):
                # Extract entities
                if 'entities' in data:
                    for entity_data in data['entities']:
                        if isinstance(entity_data, dict):
                            self.entities.append(Entity(
                                name=entity_data.get('name', entity_data.get('id', '')),
                                entity_type=entity_data.get('type', 'entity'),
                                description=entity_data.get('description', '')
                            ))
                
                # Extract relationships
                if 'relationships' in data:
                    for rel_data in data['relationships']:
                        if isinstance(rel_data, dict):
                            self.relationships.append(Relationship(
                                source=rel_data.get('source', rel_data.get('src_id', '')),
                                target=rel_data.get('target', rel_data.get('tgt_id', '')),
                                rel_type=rel_data.get('type', rel_data.get('rel_type', 'related_to')),
                                description=rel_data.get('description', ''),
                                strength=rel_data.get('strength', 5)
                            ))
            
            return self.entities, self.relationships
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return empty results
            return [], []
    
    def get_entity_types(self) -> Dict[str, int]:
        """Get count of entities by type.
        
        Returns:
            Dictionary mapping entity types to counts
        """
        type_counts = {}
        for entity in self.entities:
            type_counts[entity.entity_type] = type_counts.get(entity.entity_type, 0) + 1
        return type_counts
    
    def get_relationship_types(self) -> Dict[str, int]:
        """Get count of relationships by type.
        
        Returns:
            Dictionary mapping relationship types to counts
        """
        type_counts = {}
        for rel in self.relationships:
            type_counts[rel.rel_type] = type_counts.get(rel.rel_type, 0) + 1
        return type_counts
    
    def get_entity_by_name(self, name: str) -> Entity:
        """Get entity by name.
        
        Args:
            name: Entity name
            
        Returns:
            Entity object or None
        """
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None
    
    def get_relationships_for_entity(self, entity_name: str) -> List[Relationship]:
        """Get all relationships involving an entity.
        
        Args:
            entity_name: Entity name
            
        Returns:
            List of relationships
        """
        return [
            rel for rel in self.relationships
            if rel.source == entity_name or rel.target == entity_name
        ]
    
    def to_networkx_format(self):
        """Convert to NetworkX format.
        
        Returns:
            Dictionary with nodes and edges for NetworkX
        """
        nodes = []
        edges = []
        
        # Convert entities to nodes
        for entity in self.entities:
            nodes.append({
                'id': entity.name,
                'label': entity.name,
                'type': entity.entity_type,
                'description': entity.description
            })
        
        # Convert relationships to edges
        for rel in self.relationships:
            edges.append({
                'source': rel.source,
                'target': rel.target,
                'label': rel.rel_type,
                'type': rel.rel_type,
                'weight': rel.strength,
                'description': rel.description
            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def validate_consistency(self) -> List[str]:
        """Validate entity and relationship consistency.
        
        Returns:
            List of validation errors
        """
        errors = []
        entity_names = {entity.name for entity in self.entities}
        
        # Check relationship references
        for rel in self.relationships:
            if rel.source not in entity_names:
                errors.append(f"Relationship references unknown source entity: {rel.source}")
            if rel.target not in entity_names:
                errors.append(f"Relationship references unknown target entity: {rel.target}")
        
        # Check relationship strength
        for rel in self.relationships:
            if rel.strength < 1 or rel.strength > 10:
                errors.append(f"Invalid relationship strength for {rel.source}->{rel.target}: {rel.strength}")
        
        return errors