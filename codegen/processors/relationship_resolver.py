"""
Relationship Resolver for OpenAPI entity relationships.

This module provides utilities for:
- Resolving entity relationships from OpenAPI schemas
- Building dependency graphs
- Detecting circular dependencies
- Generating relationship mappings
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source_entity: str
    target_entity: str
    relationship_type: str  # 'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'
    field_name: str
    target_field: Optional[str] = None
    is_required: bool = False
    description: Optional[str] = None


@dataclass
class EntityDependency:
    """Represents an entity dependency."""
    entity_name: str
    depends_on: Set[str] = field(default_factory=set)
    depended_by: Set[str] = field(default_factory=set)
    depth: int = 0


class RelationshipResolver:
    """
    Resolver for entity relationships and dependencies.
    
    Features:
    - Resolve relationships from schemas
    - Build dependency graphs
    - Detect circular dependencies
    - Generate processing order
    """
    
    def __init__(self):
        """Initialize RelationshipResolver."""
        self.relationships: List[Relationship] = []
        self.entity_dependencies: Dict[str, EntityDependency] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependency_graph: Dict[str, Set[str]] = defaultdict(set)
    
    def resolve_relationships(
        self,
        entities: Dict[str, Any],
        schemas: Dict[str, Any]
    ) -> List[Relationship]:
        """
        Resolve relationships between entities from schemas.
        
        Args:
            entities: Dictionary of entity configurations
            schemas: Dictionary of OpenAPI schemas
            
        Returns:
            List of relationships
        """
        self.relationships.clear()
        
        for entity_name, entity_config in entities.items():
            # Get schemas for this entity
            entity_schemas = entity_config.get('schemas', {})
            
            for schema_name, schema in entity_schemas.items():
                self._resolve_schema_relationships(
                    entity_name,
                    schema_name,
                    schema,
                    schemas
                )
        
        logger.info(f"Resolved {len(self.relationships)} relationships")
        return self.relationships.copy()
    
    def _resolve_schema_relationships(
        self,
        entity_name: str,
        schema_name: str,
        schema: Dict[str, Any],
        all_schemas: Dict[str, Any]
    ) -> None:
        """
        Resolve relationships within a single schema.
        
        Args:
            entity_name: Name of the entity
            schema_name: Name of the schema
            schema: Schema definition
            all_schemas: All available schemas
        """
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        for field_name, field_schema in properties.items():
            # Check for direct references
            if '$ref' in field_schema:
                ref_path = field_schema['$ref']
                target_entity = self._resolve_reference(ref_path, all_schemas)
                if target_entity:
                    self._add_relationship(
                        entity_name,
                        target_entity,
                        'one_to_one',
                        field_name,
                        is_required=field_name in required_fields
                    )
            
            # Check for array references
            elif field_schema.get('type') == 'array':
                items = field_schema.get('items', {})
                if '$ref' in items:
                    ref_path = items['$ref']
                    target_entity = self._resolve_reference(ref_path, all_schemas)
                    if target_entity:
                        self._add_relationship(
                            entity_name,
                            target_entity,
                            'one_to_many',
                            field_name,
                            is_required=field_name in required_fields
                        )
            
            # Check for embedded objects
            elif field_schema.get('type') == 'object':
                # Check if this is a reference to another entity
                target_entity = self._infer_entity_from_object(field_name, field_schema)
                if target_entity:
                    self._add_relationship(
                        entity_name,
                        target_entity,
                        'one_to_one',
                        field_name,
                        is_required=field_name in required_fields
                    )
    
    def _resolve_reference(
        self,
        ref_path: str,
        schemas: Dict[str, Any]
    ) -> Optional[str]:
        """
        Resolve a $ref to an entity name.
        
        Args:
            ref_path: Reference path (e.g., '#/components/schemas/User')
            schemas: All available schemas
            
        Returns:
            Entity name if resolved, None otherwise
        """
        # Extract schema name from reference
        if ref_path.startswith('#/components/schemas/'):
            schema_name = ref_path.split('/')[-1]
            if schema_name in schemas:
                # Try to infer entity name from schema name
                return self._infer_entity_name(schema_name)
        
        return None
    
    def _infer_entity_name(self, schema_name: str) -> str:
        """
        Infer entity name from schema name.
        
        Args:
            schema_name: Schema name
            
        Returns:
            Inferred entity name
        """
        # Remove common suffixes
        suffixes_to_remove = ['Ref', 'Response', 'Request', 'Model', 'Schema']
        
        for suffix in suffixes_to_remove:
            if schema_name.endswith(suffix):
                schema_name = schema_name[:-len(suffix)]
        
        return schema_name
    
    def _infer_entity_from_object(
        self,
        field_name: str,
        field_schema: Dict[str, Any]
    ) -> Optional[str]:
        """
        Infer entity name from object field.
        
        Args:
            field_name: Field name
            field_schema: Field schema
            
        Returns:
            Inferred entity name
        """
        # Try to infer from field name
        if field_name.endswith('Ref'):
            return field_name[:-3]  # Remove 'Ref' suffix
        
        # Check for common patterns
        if field_name in ['user', 'member', 'bill', 'amendment', 'committee']:
            return field_name.capitalize()
        
        return None
    
    def _add_relationship(
        self,
        source_entity: str,
        target_entity: str,
        relationship_type: str,
        field_name: str,
        is_required: bool = False
    ) -> None:
        """
        Add a relationship between entities.
        
        Args:
            source_entity: Source entity name
            target_entity: Target entity name
            relationship_type: Type of relationship
            field_name: Field name in source entity
            is_required: Whether the relationship is required
        """
        relationship = Relationship(
            source_entity=source_entity,
            target_entity=target_entity,
            relationship_type=relationship_type,
            field_name=field_name,
            is_required=is_required
        )
        
        self.relationships.append(relationship)
        
        # Update dependency graphs
        self.dependency_graph[source_entity].add(target_entity)
        self.reverse_dependency_graph[target_entity].add(source_entity)
        
        logger.debug(f"Added relationship: {source_entity}.{field_name} -> {target_entity} ({relationship_type})")
    
    def build_dependency_graph(self, entities: Dict[str, Any]) -> Dict[str, EntityDependency]:
        """
        Build dependency graph for entities.
        
        Args:
            entities: Dictionary of entity configurations
            
        Returns:
            Dictionary mapping entity names to dependency information
        """
        self.entity_dependencies.clear()
        
        # Initialize dependencies for all entities
        for entity_name in entities.keys():
            self.entity_dependencies[entity_name] = EntityDependency(entity_name=entity_name)
        
        # Build dependencies from relationships
        for relationship in self.relationships:
            source = relationship.source_entity
            target = relationship.target_entity
            
            if source in self.entity_dependencies and target in self.entity_dependencies:
                self.entity_dependencies[source].depends_on.add(target)
                self.entity_dependencies[target].depended_by.add(source)
        
        # Calculate dependency depths
        self._calculate_dependency_depths()
        
        logger.info(f"Built dependency graph for {len(self.entity_dependencies)} entities")
        return self.entity_dependencies.copy()
    
    def _calculate_dependency_depths(self) -> None:
        """Calculate dependency depths for all entities."""
        # Use topological sort to calculate depths
        visited = set()
        visiting = set()
        
        def dfs(entity_name: str, depth: int = 0) -> None:
            if entity_name in visiting:
                # Circular dependency detected
                logger.warning(f"Circular dependency detected involving {entity_name}")
                return
            
            if entity_name in visited:
                return
            
            visiting.add(entity_name)
            
            # Update depth
            if entity_name in self.entity_dependencies:
                self.entity_dependencies[entity_name].depth = max(
                    self.entity_dependencies[entity_name].depth,
                    depth
                )
            
            # Visit dependencies
            for dependency in self.dependency_graph.get(entity_name, set()):
                dfs(dependency, depth + 1)
            
            visiting.remove(entity_name)
            visited.add(entity_name)
        
        # Process all entities
        for entity_name in self.entity_dependencies.keys():
            dfs(entity_name)
    
    def get_processing_order(self, entities: Dict[str, Any]) -> List[str]:
        """
        Get the order in which entities should be processed.
        
        Entities are ordered by dependency depth, with entities that have
        no dependencies processed first.
        
        Args:
            entities: Dictionary of entity configurations
            
        Returns:
            List of entity names in processing order
        """
        if not self.entity_dependencies:
            self.build_dependency_graph(entities)
        
        # Sort entities by depth (ascending)
        sorted_entities = sorted(
            self.entity_dependencies.items(),
            key=lambda x: x[1].depth
        )
        
        processing_order = [entity_name for entity_name, _ in sorted_entities]
        
        logger.debug(f"Processing order: {processing_order}")
        return processing_order
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in the relationship graph.
        
        Returns:
            List of circular dependency chains
        """
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    circular_deps.append(cycle)
            
            rec_stack.remove(node)
        
        for entity in self.entity_dependencies.keys():
            if entity not in visited:
                dfs(entity, [])
        
        if circular_deps:
            logger.warning(f"Detected {len(circular_deps)} circular dependencies")
            for cycle in circular_deps:
                logger.warning(f"Circular dependency: {' -> '.join(cycle)}")
        
        return circular_deps
    
    def get_entity_relationships(self, entity_name: str) -> List[Relationship]:
        """
        Get all relationships for a specific entity.
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            List of relationships involving the entity
        """
        return [
            rel for rel in self.relationships
            if rel.source_entity == entity_name or rel.target_entity == entity_name
        ]
    
    def get_incoming_relationships(self, entity_name: str) -> List[Relationship]:
        """
        Get relationships where the entity is the target.
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            List of incoming relationships
        """
        return [
            rel for rel in self.relationships
            if rel.target_entity == entity_name
        ]
    
    def get_outgoing_relationships(self, entity_name: str) -> List[Relationship]:
        """
        Get relationships where the entity is the source.
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            List of outgoing relationships
        """
        return [
            rel for rel in self.relationships
            if rel.source_entity == entity_name
        ]
    
    def validate_relationships(self) -> List[str]:
        """
        Validate all relationships for consistency.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        for relationship in self.relationships:
            # Check if source and target entities exist
            if relationship.source_entity not in self.entity_dependencies:
                errors.append(f"Relationship references unknown source entity: {relationship.source_entity}")
            
            if relationship.target_entity not in self.entity_dependencies:
                errors.append(f"Relationship references unknown target entity: {relationship.target_entity}")
            
            # Check for self-references
            if relationship.source_entity == relationship.target_entity:
                errors.append(f"Self-referencing relationship: {relationship.source_entity}.{relationship.field_name}")
        
        # Check for circular dependencies
        circular_deps = self.detect_circular_dependencies()
        for cycle in circular_deps:
            errors.append(f"Circular dependency: {' -> '.join(cycle)}")
        
        if errors:
            logger.warning(f"Relationship validation found {len(errors)} errors")
        else:
            logger.info("Relationship validation passed")
        
        return errors


