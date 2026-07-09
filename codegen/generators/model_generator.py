"""
Model Generator for Pydantic models from OpenAPI schemas.

This module generates Pydantic model classes from OpenAPI schema definitions
with support for custom annotations and field mappings.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .base_generator import BaseGenerator, GenerationResult
from ..processors.field_mapper import FieldMapper, FieldDefinition
from ..processors.spec_parser import EntityConfig

logger = logging.getLogger(__name__)


class ModelGenerator(BaseGenerator):
    """
    Generator for Pydantic model classes.
    
    This generator:
    - Creates Pydantic model classes from OpenAPI schemas
    - Generates collection classes for entity lists
    - Handles field mappings and type conversions
    - Adds proper imports and documentation
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        spec_parser: Any,
        file_manager: Optional[Any] = None,
        template_engine: Optional[Any] = None,
        code_formatter: Optional[Any] = None
    ):
        """
        Initialize ModelGenerator.
        
        Args:
            config: Generator configuration
            spec_parser: Parsed OpenAPI specification
            file_manager: File manager instance
            template_engine: Template engine instance
            code_formatter: Code formatter instance
        """
        super().__init__(config, spec_parser, file_manager, template_engine, code_formatter)
        
        # Model generation configuration
        self.model_config = config.get('models', {})
        self.field_mapper = FieldMapper()
    
    def generate(self) -> GenerationResult:
        """
        Generate Pydantic model classes.
        
        Returns:
            GenerationResult with success status and details
        """
        self.logger.info("Starting model generation...")
        
        try:
            # Validate prerequisites
            errors = self.validate_generation_prerequisites()
            if errors:
                return self.create_generation_result(
                    success=False,
                    generated_files=[],
                    errors=errors,
                    summary="Model generation failed validation"
                )
            
            # Get processing order for entities
            processing_order = self.get_processing_order()
            
            generated_files = []
            all_errors = []
            all_warnings = []
            
            # Generate models for each entity
            for entity_name in processing_order:
                try:
                    entity_files = self._generate_entity_models(entity_name)
                    generated_files.extend(entity_files)
                    self.logger.info(f"Generated models for entity: {entity_name}")
                    
                except Exception as e:
                    error_msg = f"Failed to generate models for entity {entity_name}: {e}"
                    self.logger.error(error_msg)
                    all_errors.append(error_msg)
            
            success = len(all_errors) == 0
            
            summary = f"Generated {len(generated_files)} model files"
            if all_errors:
                summary += f" with {len(all_errors)} errors"
            
            return self.create_generation_result(
                success=success,
                generated_files=generated_files,
                errors=all_errors,
                warnings=all_warnings,
                summary=summary
            )
            
        except Exception as e:
            self.logger.error(f"Model generation failed: {e}")
            return self.create_generation_result(
                success=False,
                generated_files=[],
                errors=[str(e)],
                summary="Model generation failed with exception"
            )
    
    def get_required_config_keys(self) -> List[str]:
        """
        Get list of required configuration keys.
        
        Returns:
            List of required configuration key names
        """
        return ['output', 'models']
    
    def _generate_entity_models(self, entity_name: str) -> List[Path]:
        """
        Generate model files for a specific entity.
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            List of generated file paths
        """
        entity_config = self.get_entity_config(entity_name)
        if not entity_config:
            raise ValueError(f"Entity configuration not found: {entity_name}")
        
        generated_files = []
        
        output_path = self._resolve_model_output_path(entity_config)
        if self.file_manager.is_protected(output_path):
            self.logger.info("Skipped protected model path: %s", output_path)
            return []

        model_file = self._generate_model_file(entity_config, output_path)
        if model_file:
            generated_files.append(model_file)

        return generated_files

    def _resolve_model_output_path(self, entity_config: EntityConfig) -> Path:
        """Resolve hand model file path from entity module_path (e.g. models.communications.house_vote)."""
        models_dir = self.get_output_directory("models")
        module_path = (entity_config.model_config.module_path or "").strip()
        if module_path.startswith("congressgov.models."):
            rel = module_path[len("congressgov.models.") :].replace(".", "/")
            return models_dir / f"{rel}.py"
        if module_path.startswith("models."):
            rel = module_path[len("models.") :].replace(".", "/")
            return models_dir / f"{rel}.py"
        entity_dir = self._get_entity_subdirectory(entity_config.name, models_dir)
        return entity_dir / f"{entity_config.name.lower()}.py"
    
    def _get_entity_subdirectory(self, entity_name: str, models_dir: Path) -> Path:
        """
        Get subdirectory for entity models.
        
        Args:
            entity_name: Name of the entity
            models_dir: Base models directory
            
        Returns:
            Path to entity subdirectory
        """
        # Map entities to subdirectories
        entity_mapping = {
            'Bill': 'entities',
            'Amendment': 'entities',
            'Member': 'entities',
            'Committee': 'committees',
            'Action': 'actions',
            'Vote': 'actions',
            'Calendar': 'actions',
            'Hearing': 'documents',
            'CommitteeReport': 'documents',
            'CommitteePrint': 'documents',
            'CRSReport': 'documents',
            'CongressionalRecord': 'documents',
            'CommitteeMeeting': 'meetings',
            'Nomination': 'nominations',
        }
        
        subdir = entity_mapping.get(entity_name, 'entities')
        entity_dir = models_dir / subdir
        
        # Ensure directory exists
        self.file_manager.ensure_directory(entity_dir)
        
        return entity_dir
    
    def _generate_model_file(self, entity_config: EntityConfig, output_path: Path) -> Optional[Path]:
        """
        Generate model file for an entity.

        Args:
            entity_config: Entity configuration
            output_path: Target model file path

        Returns:
            Path to generated file, or None if generation failed
        """
        try:
            entity_schema = self._get_entity_schema(entity_config)
            if not entity_schema:
                raise ValueError(f"No schema found for entity: {entity_config.name}")

            context = self._prepare_model_context(entity_config, entity_schema)
            self.file_manager.ensure_directory(output_path.parent)

            self.render_template(
                "model.py.jinja2",
                context,
                output_path,
            )

            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate model file for {entity_config.name}: {e}")
            return None
    
    def _get_entity_schema(self, entity_config: EntityConfig) -> Optional[Dict[str, Any]]:
        """
        Get schema for an entity.
        
        Args:
            entity_config: Entity configuration
            
        Returns:
            Schema dictionary if found, None otherwise
        """
        # Look for schema in entity schemas
        schemas = entity_config.schemas
        if schemas:
            entity_name = entity_config.name
            if entity_name in schemas:
                return schemas[entity_name]

            collection_name = entity_config.model_config.collection_class
            if collection_name and collection_name in schemas:
                return schemas[collection_name]

            # Prefer entity body schemas over *Response wrappers
            non_response = {
                name: schema
                for name, schema in schemas.items()
                if not name.endswith("Response")
            }
            if non_response:
                return next(iter(non_response.values()))

            return next(iter(schemas.values()))
        
        # Fallback to spec parser schemas
        return self.spec_parser.get_schema(entity_config.name)
    
    def _prepare_model_context(
        self,
        entity_config: EntityConfig,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare template context for model generation.
        
        Args:
            entity_config: Entity configuration
            schema: Entity schema
            
        Returns:
            Template context dictionary
        """
        # Map schema fields to field definitions
        fields = self._map_schema_fields(schema, entity_config)
        
        # Generate imports
        imports = self._generate_imports(fields, entity_config)
        
        # Get types for imports
        types = self._extract_types(fields)
        
        # Get enums
        enums = self._extract_enums(fields, entity_config)
        
        context = {
            'model_name': entity_config.name,
            'collection_class': entity_config.model_config.collection_class,
            'items_field': entity_config.model_config.items_field,
            'description': schema.get('description', f"{entity_config.name} entity from the Congress.gov API"),
            'fields': fields,
            'imports': imports,
            'types': types,
            'enums': enums,
            'expansion_mappings': entity_config.expansion_mappings,
        }
        
        return context
    
    def _map_schema_fields(
        self,
        schema: Dict[str, Any],
        entity_config: EntityConfig
    ) -> List[Dict[str, Any]]:
        """
        Map schema fields to field definitions.
        
        Args:
            schema: Entity schema
            entity_config: Entity configuration
            
        Returns:
            List of field definition dictionaries
        """
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        fields = []
        for field_name, field_schema in properties.items():
            is_required = field_name in required_fields
            field_def = self.field_mapper.map_field(field_name, field_schema, is_required)
            
            # Convert to dictionary for template
            field_dict = {
                'name': field_def.name,
                'python_type': field_def.python_type,
                'openapi_type': field_def.openapi_type,
                'format_': field_def.format_,
                'description': field_def.description,
                'default_value': field_def.default_value,
                'is_required': field_def.is_required,
                'is_optional': field_def.is_optional,
                'is_array': field_def.is_array,
                'is_object': field_def.is_object,
                'enum_values': field_def.enum_values,
                'constraints': field_def.constraints,
                'alias': field_def.alias,
                'example': self._generate_field_example(field_def),
            }
            
            fields.append(field_dict)
        
        return fields
    
    def _generate_field_example(self, field_def: FieldDefinition) -> str:
        """
        Generate example value for a field.
        
        Args:
            field_def: Field definition
            
        Returns:
            Example value string
        """
        if field_def.enum_values:
            return field_def.enum_values[0]
        elif field_def.python_type == 'str':
            return 'example'
        elif field_def.python_type == 'int':
            return '1'
        elif field_def.python_type == 'float':
            return '1.0'
        elif field_def.python_type == 'bool':
            return 'True'
        else:
            return 'None'
    
    def _generate_imports(self, fields: List[Dict[str, Any]], entity_config: EntityConfig) -> Set[str]:
        """
        Generate import statements for fields and entity.
        
        Args:
            fields: List of field definitions
            entity_config: Entity configuration
            
        Returns:
            Set of import statements
        """
        imports = set()
        
        # Add base imports
        imports.add("from __future__ import annotations")
        imports.add("from typing import Any, Optional, Union")
        imports.add("from datetime import date as DateType, datetime")
        imports.add("from pydantic import Field, AliasChoices")
        imports.add("from ..base.model import Model")
        
        # Add field-specific imports
        field_definitions = [
            FieldDefinition(**{k: v for k, v in field.items() if k != "example"})
            for field in fields
        ]
        field_imports = self.field_mapper.generate_all_imports(field_definitions)
        imports.update(field_imports)
        
        # Add enum imports
        for field in fields:
            if field.get('enum_values'):
                # Add enum import based on field name or type
                enum_name = self._infer_enum_name(field['name'])
                if enum_name:
                    imports.add(f"from ..base.enums import {enum_name}")
        
        return sorted(imports)
    
    def _infer_enum_name(self, field_name: str) -> Optional[str]:
        """
        Infer enum name from field name.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Inferred enum name or None
        """
        # Simple mapping of field names to enum names
        enum_mapping = {
            'type': 'LegislationType',
            'billType': 'LegislationType',
            'originChamber': 'Chamber',
            'chamber': 'Chamber',
            'state': 'StateCode',
            'party': 'PartyCode',
            'amendmentType': 'AmendmentType',
        }
        
        return enum_mapping.get(field_name)
    
    def _extract_types(self, fields: List[Dict[str, Any]]) -> Set[str]:
        """
        Extract unique types from fields.
        
        Args:
            fields: List of field definitions
            
        Returns:
            Set of unique type names
        """
        types = set()
        
        for field in fields:
            python_type = field['python_type']
            
            # Extract types from complex type hints
            if 'Optional[' in python_type:
                inner_type = python_type.replace('Optional[', '').replace(']', '')
                types.add(inner_type)
            elif 'list[' in python_type:
                inner_type = python_type.replace('list[', '').replace(']', '')
                types.add(inner_type)
            else:
                types.add(python_type)
        
        # Remove common types that don't need imports
        types.discard('str')
        types.discard('int')
        types.discard('float')
        types.discard('bool')
        
        return types
    
    def _extract_enums(self, fields: List[Dict[str, Any]], entity_config: EntityConfig) -> Set[str]:
        """
        Extract enum names from fields and field mappings.
        
        Args:
            fields: List of field definitions
            entity_config: Entity configuration
            
        Returns:
            Set of enum names
        """
        enums = set()
        
        # Add enums from field mappings
        for field_name, field_mapping in entity_config.field_mappings.items():
            if field_mapping.enum:
                enums.add(field_mapping.enum)
        
        # Add enums from field definitions
        for field in fields:
            if field.get('enum_values'):
                enum_name = self._infer_enum_name(field['name'])
                if enum_name:
                    enums.add(enum_name)
        
        return sorted(enums)


