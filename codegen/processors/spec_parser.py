"""
OpenAPI Specification Parser with Custom Annotations.

This module provides utilities for:
- Parsing OpenAPI specifications (YAML/JSON)
- Extracting custom x-* annotations
- Building entity relationship graphs
- Validating configuration consistency
"""

from __future__ import annotations

import json
import re
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class FieldMapping:
    """Configuration for field mapping with enum support."""
    enum: Optional[str] = None
    shorthand: bool = False
    variations: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class ExpansionMapping:
    """Configuration for entity expansion mappings."""
    endpoint: str
    api_function: str
    model: str
    description: Optional[str] = None


@dataclass
class ExtensionMethod:
    """Configuration for extension methods."""
    name: str
    filter: Optional[Dict[str, Any]] = None
    param: Optional[str] = None
    filter_field: Optional[str] = None
    description: Optional[str] = None


@dataclass
class EndpointConfig:
    """Primary or list endpoint metadata for middleware codegen."""
    role: str  # primary | list
    api_function: str
    path: str
    python_params: List[str] = field(default_factory=list)


@dataclass
class ModelConfig:
    """Configuration for model generation."""
    base_class: str = "Model"
    collection_class: Optional[str] = None
    items_field: Optional[str] = None
    module_path: Optional[str] = None
    service_path: Optional[str] = None
    extension_path: Optional[str] = None


@dataclass
class EntityConfig:
    """Complete configuration for an entity."""
    name: str
    model_config: ModelConfig
    field_mappings: Dict[str, FieldMapping] = field(default_factory=dict)
    expansion_mappings: Dict[str, ExpansionMapping] = field(default_factory=dict)
    parameter_mappings: Dict[str, Union[str, List[str]]] = field(default_factory=dict)
    extension_methods: List[ExtensionMethod] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    schemas: Dict[str, Any] = field(default_factory=dict)
    primary_endpoint: Optional[EndpointConfig] = None
    list_endpoint: Optional[EndpointConfig] = None
    service_codegen: Dict[str, Any] = field(default_factory=dict)


class SpecParser:
    """
    Parser for OpenAPI specifications with custom annotations.
    
    Features:
    - Parse YAML/JSON OpenAPI specs
    - Extract custom x-* annotations
    - Build entity relationship graphs
    - Validate configuration consistency
    - Generate entity configurations
    """
    
    def __init__(self):
        """Initialize SpecParser."""
        self.spec_data: Dict[str, Any] = {}
        self.entities: Dict[str, EntityConfig] = {}
        self.schemas: Dict[str, Any] = {}
        self.paths: Dict[str, Any] = {}
        self.relationships: Dict[str, Set[str]] = defaultdict(set)
    
    def load_spec(self, spec_path: Union[str, Path]) -> None:
        """
        Load OpenAPI specification from file.
        
        Args:
            spec_path: Path to OpenAPI spec file (YAML or JSON)
            
        Raises:
            FileNotFoundError: If spec file doesn't exist
            ValueError: If spec file format is invalid
        """
        spec_path = Path(spec_path)
        
        if not spec_path.exists():
            raise FileNotFoundError(f"OpenAPI spec file not found: {spec_path}")
        
        try:
            content = spec_path.read_text(encoding='utf-8')
            
            if spec_path.suffix.lower() in ['.yaml', '.yml']:
                self.spec_data = yaml.safe_load(content)
            elif spec_path.suffix.lower() == '.json':
                self.spec_data = json.loads(content)
            else:
                # Try to auto-detect format
                try:
                    self.spec_data = yaml.safe_load(content)
                except yaml.YAMLError:
                    self.spec_data = json.loads(content)
            
            logger.info(f"Loaded OpenAPI spec from: {spec_path}")
            
            # Extract components
            self._extract_components()
            
        except Exception as e:
            raise ValueError(f"Failed to parse OpenAPI spec: {e}")
    
    def _extract_components(self) -> None:
        """Extract components from loaded spec."""
        # Extract paths
        self.paths = self.spec_data.get('paths', {})
        
        # Extract schemas
        components = self.spec_data.get('components', {})
        self.schemas = components.get('schemas', {})
        
        logger.debug(f"Extracted {len(self.paths)} paths and {len(self.schemas)} schemas")
    
    def parse_entities(self) -> Dict[str, EntityConfig]:
        """
        Parse entities from OpenAPI spec with custom annotations.
        
        Returns:
            Dictionary mapping entity names to EntityConfig objects
        """
        self.entities.clear()
        
        for path, path_item in self.paths.items():
            for method, operation in path_item.items():
                if not isinstance(operation, dict) or method not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue
                
                # Check for entity name annotation
                entity_name = operation.get('x-entity-name')
                if not entity_name:
                    continue
                
                logger.debug(f"Found entity: {entity_name} in {method.upper()} {path}")
                
                # Create or update entity config
                if entity_name not in self.entities:
                    self.entities[entity_name] = EntityConfig(
                        name=entity_name,
                        model_config=ModelConfig()
                    )
                
                entity_config = self.entities[entity_name]
                entity_config.paths.append(f"{method.upper()} {path}")
                
                # Parse custom annotations
                self._parse_model_config(operation, entity_config)
                self._parse_field_mappings(operation, entity_config)
                self._parse_expansion_mappings(operation, entity_config)
                self._parse_parameter_mappings(operation, entity_config)
                self._parse_extension_methods(operation, entity_config)
                self._parse_endpoint_role(path, operation, entity_config)
        
        # Parse schemas for each entity
        self._parse_entity_schemas()
        
        # Build relationships
        self._build_relationships()
        
        logger.info(f"Parsed {len(self.entities)} entities")
        return self.entities
    
    def _parse_model_config(self, operation: Dict[str, Any], entity_config: EntityConfig) -> None:
        """Parse x-model-config annotation."""
        model_config_data = operation.get('x-model-config', {})
        
        if model_config_data:
            model_config = entity_config.model_config
            model_config.base_class = model_config_data.get('base-class', model_config.base_class)
            model_config.collection_class = model_config_data.get('collection-class')
            model_config.items_field = model_config_data.get('items-field')
            model_config.module_path = model_config_data.get('module-path')
            model_config.service_path = model_config_data.get('service-path')
            model_config.extension_path = model_config_data.get('extension-path')
    
    def _parse_field_mappings(self, operation: Dict[str, Any], entity_config: EntityConfig) -> None:
        """Parse x-field-mappings annotation."""
        field_mappings_data = operation.get('x-field-mappings', {})
        
        for field_name, mapping_data in field_mappings_data.items():
            field_mapping = FieldMapping()
            
            if isinstance(mapping_data, dict):
                field_mapping.enum = mapping_data.get('enum')
                field_mapping.shorthand = mapping_data.get('shorthand', False)
                field_mapping.variations = mapping_data.get('variations', [])
                field_mapping.description = mapping_data.get('description')
            elif isinstance(mapping_data, str):
                # Simple string mapping to enum
                field_mapping.enum = mapping_data
            
            entity_config.field_mappings[field_name] = field_mapping
    
    def _parse_expansion_mappings(self, operation: Dict[str, Any], entity_config: EntityConfig) -> None:
        """Parse x-expansion-mappings annotation."""
        expansion_mappings_data = operation.get('x-expansion-mappings', {})
        
        for attr_name, mapping_data in expansion_mappings_data.items():
            if isinstance(mapping_data, dict):
                expansion_mapping = ExpansionMapping(
                    endpoint=mapping_data.get('endpoint', ''),
                    api_function=mapping_data.get('api-function', ''),
                    model=mapping_data.get('model', ''),
                    description=mapping_data.get('description')
                )
                entity_config.expansion_mappings[attr_name] = expansion_mapping
    
    def _parse_parameter_mappings(self, operation: Dict[str, Any], entity_config: EntityConfig) -> None:
        """Parse x-parameter-mappings annotation."""
        parameter_mappings_data = operation.get('x-parameter-mappings', {})
        
        for param_name, mapping_data in parameter_mappings_data.items():
            if isinstance(mapping_data, list):
                entity_config.parameter_mappings[param_name] = mapping_data
            else:
                entity_config.parameter_mappings[param_name] = [mapping_data]
    
    def _parse_extension_methods(self, operation: Dict[str, Any], entity_config: EntityConfig) -> None:
        """Parse x-extension-methods annotation."""
        extension_methods_data = operation.get('x-extension-methods', [])
        
        for method_data in extension_methods_data:
            if isinstance(method_data, dict):
                extension_method = ExtensionMethod(
                    name=method_data.get('name', ''),
                    filter=method_data.get('filter'),
                    param=method_data.get('param'),
                    filter_field=method_data.get('filter-field'),
                    description=method_data.get('description')
                )
                entity_config.extension_methods.append(extension_method)

    def _openapi_param_to_python(self, openapi_name: str, entity_config: EntityConfig) -> str:
        """Map OpenAPI path parameter names to Python identifiers."""
        for py_name, mapping in entity_config.parameter_mappings.items():
            if isinstance(mapping, list):
                if openapi_name in mapping:
                    return py_name
            elif mapping == openapi_name:
                return py_name
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", openapi_name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def _resolve_parameter_ref(self, param: Dict[str, Any]) -> Dict[str, Any] | None:
        ref = param.get("$ref")
        if not ref or not ref.startswith("#/components/parameters/"):
            return param if param.get("in") else None
        name = ref.rsplit("/", 1)[-1]
        components = self.spec_data.get("components", {})
        resolved = components.get("parameters", {}).get(name)
        return resolved if isinstance(resolved, dict) else None

    def _path_params_from_operation(
        self,
        path: str,
        operation: Dict[str, Any],
        entity_config: EntityConfig,
    ) -> List[str]:
        params: List[str] = []
        for param in operation.get("parameters", []):
            if not isinstance(param, dict):
                continue
            resolved = self._resolve_parameter_ref(param) or param
            if resolved.get("in") == "path":
                params.append(self._openapi_param_to_python(resolved["name"], entity_config))
        if not params:
            for openapi_name in re.findall(r"\{([^}]+)\}", path):
                params.append(self._openapi_param_to_python(openapi_name, entity_config))
        return params

    def _parse_endpoint_role(
        self, path: str, operation: Dict[str, Any], entity_config: EntityConfig
    ) -> None:
        """Parse x-endpoint-role and x-api-function for middleware templates."""
        role = operation.get("x-endpoint-role")
        api_fn = operation.get("x-api-function")
        if not role or not api_fn:
            return
        python_params = self._path_params_from_operation(path, operation, entity_config)
        endpoint = EndpointConfig(
            role=role,
            api_function=api_fn,
            path=path,
            python_params=python_params,
        )
        if role == "primary":
            entity_config.primary_endpoint = endpoint
        elif role in ("list", "search"):
            entity_config.list_endpoint = endpoint

    def apply_entity_mapping_fallback(self, mappings_path: Path) -> None:
        """Merge entity_mappings.yaml pilot entities when annotations are incomplete."""
        if not mappings_path.is_file():
            return
        data = yaml.safe_load(mappings_path.read_text(encoding="utf-8")) or {}
        raw_entities = data.get("entities", {})
        api_fn_map = data.get("api_function_mappings", {})

        name_map = {
            "bill": "Bill",
            "amendment": "Amendment",
            "member": "Member",
            "committee": "Committee",
            "hearing": "Hearing",
            "nomination": "Nomination",
            "treaty": "Treaty",
            "house_vote": "HouseVote",
            "summaries": "Summaries",
            "crs_report": "CRSReport",
            "house_communication": "HouseCommunication",
            "senate_communication": "SenateCommunication",
            "committee_meeting": "CommitteeMeeting",
            "committee_report": "CommitteeReport",
            "committee_print": "CommitteePrint",
            "congress": "Congress",
            "house_requirement": "HouseRequirement",
            "congressional_record": "CongressionalRecord",
            "daily_congressional_record": "DailyCongressionalRecord",
            "bound_congressional_record": "BoundCongressionalRecord",
        }
        for key, cfg in raw_entities.items():
            entity_name = name_map.get(key, key.title())
            if entity_name not in self.entities:
                self.entities[entity_name] = EntityConfig(
                    name=entity_name,
                    model_config=ModelConfig(),
                )
            entity = self.entities[entity_name]
            mc = entity.model_config
            mc.collection_class = mc.collection_class or cfg.get("collection_name")
            mc.items_field = mc.items_field or cfg.get("items_field")
            mc.module_path = mc.module_path or cfg.get("module_path")
            mc.service_path = mc.service_path or cfg.get("service_path")
            mc.extension_path = mc.extension_path or cfg.get("extension_path")

            fn_cfg = api_fn_map.get(key, {})
            if not entity.primary_endpoint and fn_cfg.get("details"):
                entity.primary_endpoint = EndpointConfig(
                    role="primary",
                    api_function=fn_cfg["details"],
                    path="",
                    python_params=[],
                )
            if not entity.list_endpoint and fn_cfg.get("list"):
                entity.list_endpoint = EndpointConfig(
                    role="list",
                    api_function=fn_cfg.get("list") or fn_cfg.get("list_all", ""),
                    path="",
                    python_params=[],
                )

            hooks = cfg.get("service_codegen") or {}
            if hooks:
                entity.service_codegen = {**entity.service_codegen, **hooks}

            exp_raw = cfg.get("expansion_mappings") or {}
            for attr_name, mapping_data in exp_raw.items():
                if attr_name in entity.expansion_mappings:
                    continue
                if not isinstance(mapping_data, dict):
                    continue
                entity.expansion_mappings[attr_name] = ExpansionMapping(
                    endpoint=mapping_data.get("endpoint", ""),
                    api_function=mapping_data.get("api_function", ""),
                    model=mapping_data.get("model", ""),
                    description=mapping_data.get("description"),
                )
    
    def _parse_entity_schemas(self) -> None:
        """Parse schemas for entities."""
        for entity_name, entity_config in self.entities.items():
            # Look for schemas related to this entity
            entity_schemas = {}
            
            # Check for direct schema match
            if entity_name in self.schemas:
                entity_schemas[entity_name] = self.schemas[entity_name]
            
            # Check for collection schema
            collection_name = entity_config.model_config.collection_class
            if collection_name and collection_name in self.schemas:
                entity_schemas[collection_name] = self.schemas[collection_name]
            
            # Check for related schemas (from expansion mappings)
            for expansion_name, expansion_mapping in entity_config.expansion_mappings.items():
                model_name = expansion_mapping.model
                if model_name in self.schemas:
                    entity_schemas[model_name] = self.schemas[model_name]
            
            entity_config.schemas = entity_schemas
    
    def _build_relationships(self) -> None:
        """Build entity relationship graph."""
        self.relationships.clear()
        
        for entity_name, entity_config in self.entities.items():
            # Add relationships from expansion mappings
            for expansion_name, expansion_mapping in entity_config.expansion_mappings.items():
                related_model = expansion_mapping.model
                self.relationships[entity_name].add(related_model)
                
                # Also add reverse relationship
                self.relationships[related_model].add(entity_name)
        
        logger.debug(f"Built relationships for {len(self.relationships)} entities")
    
    def get_entity(self, entity_name: str) -> Optional[EntityConfig]:
        """
        Get entity configuration by name.
        
        Args:
            entity_name: Name of entity
            
        Returns:
            EntityConfig if found, None otherwise
        """
        return self.entities.get(entity_name)
    
    def _known_related_names(self) -> Set[str]:
        """Names that may appear in the relationship graph (entities, models, schemas)."""
        names: Set[str] = set(self.entities.keys())
        names.update(self.schemas.keys())
        for entity_config in self.entities.values():
            model_config = entity_config.model_config
            if model_config.base_class:
                names.add(model_config.base_class)
            if model_config.collection_class:
                names.add(model_config.collection_class)
            for expansion_mapping in entity_config.expansion_mappings.values():
                if expansion_mapping.model:
                    names.add(expansion_mapping.model)
        return names

    def get_related_entities(self, entity_name: str) -> Set[str]:
        """
        Get entities related to the given entity.
        
        Args:
            entity_name: Name of entity
            
        Returns:
            Set of related entity names
        """
        return self.relationships.get(entity_name, set())
    
    def get_all_entities(self) -> Dict[str, EntityConfig]:
        """
        Get all parsed entities.
        
        Returns:
            Dictionary of all entity configurations
        """
        return self.entities.copy()
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the parsed configuration for consistency.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        for entity_name, entity_config in self.entities.items():
            # Validate model config
            if not entity_config.model_config.base_class:
                errors.append(f"Entity {entity_name}: Missing base class in model config")
            
            # Validate expansion mappings
            for attr_name, expansion_mapping in entity_config.expansion_mappings.items():
                if not expansion_mapping.endpoint:
                    errors.append(f"Entity {entity_name}: Missing endpoint for expansion {attr_name}")
                if not expansion_mapping.api_function:
                    errors.append(f"Entity {entity_name}: Missing api_function for expansion {attr_name}")
                if not expansion_mapping.model:
                    errors.append(f"Entity {entity_name}: Missing model for expansion {attr_name}")
            
            # Validate field mappings
            for field_name, field_mapping in entity_config.field_mappings.items():
                if field_mapping.shorthand and not field_mapping.enum:
                    errors.append(f"Entity {entity_name}: Field {field_name} has shorthand=True but no enum")
            
            # Validate extension methods
            for method in entity_config.extension_methods:
                if not method.name:
                    errors.append(f"Entity {entity_name}: Extension method missing name")
                if not method.filter and not method.param:
                    errors.append(f"Entity {entity_name}: Extension method {method.name} has no filter or param")
        
        # Validate relationships (expansion targets are model/schema names, not entities)
        known_related = self._known_related_names()
        for entity_name, related_entities in self.relationships.items():
            if entity_name not in self.entities:
                continue
            for related_entity in related_entities:
                if related_entity not in known_related:
                    errors.append(
                        f"Entity {entity_name}: References unknown related name {related_entity}"
                    )
        
        if errors:
            logger.warning(f"Configuration validation found {len(errors)} errors")
        else:
            logger.info("Configuration validation passed")
        
        return errors
    
    def get_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """
        Get schema by name.
        
        Args:
            schema_name: Name of schema
            
        Returns:
            Schema definition if found, None otherwise
        """
        return self.schemas.get(schema_name)
    
    def get_paths_for_entity(self, entity_name: str) -> List[str]:
        """
        Get all paths for an entity.
        
        Args:
            entity_name: Name of entity
            
        Returns:
            List of paths for the entity
        """
        entity_config = self.entities.get(entity_name)
        if entity_config:
            return entity_config.paths.copy()
        return []
    
    def export_entity_config(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """
        Export entity configuration as dictionary.
        
        Args:
            entity_name: Name of entity
            
        Returns:
            Entity configuration as dictionary, None if not found
        """
        entity_config = self.entities.get(entity_name)
        if not entity_config:
            return None
        
        return {
            'name': entity_config.name,
            'model_config': {
                'base_class': entity_config.model_config.base_class,
                'collection_class': entity_config.model_config.collection_class,
                'items_field': entity_config.model_config.items_field,
                'module_path': entity_config.model_config.module_path,
                'service_path': entity_config.model_config.service_path,
                'extension_path': entity_config.model_config.extension_path,
            },
            'field_mappings': {
                name: {
                    'enum': mapping.enum,
                    'shorthand': mapping.shorthand,
                    'variations': mapping.variations,
                    'description': mapping.description,
                }
                for name, mapping in entity_config.field_mappings.items()
            },
            'expansion_mappings': {
                name: {
                    'endpoint': mapping.endpoint,
                    'api_function': mapping.api_function,
                    'model': mapping.model,
                    'description': mapping.description,
                }
                for name, mapping in entity_config.expansion_mappings.items()
            },
            'parameter_mappings': entity_config.parameter_mappings,
            'extension_methods': [
                {
                    'name': method.name,
                    'filter': method.filter,
                    'param': method.param,
                    'filter_field': method.filter_field,
                    'description': method.description,
                }
                for method in entity_config.extension_methods
            ],
            'paths': entity_config.paths,
            'schemas': entity_config.schemas,
        }


