"""
Extension Generator for model extension methods.

This module generates extension methods that add query builders,
convenience methods, and domain-specific functionality to models.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_generator import BaseGenerator, GenerationResult
from ..utils.module_paths import (
    normalize_extension_path,
    normalize_module_path,
    normalize_service_path,
)
from ..processors.spec_parser import EntityConfig

logger = logging.getLogger(__name__)


class ExtensionGenerator(BaseGenerator):
    """
    Generator for model extension methods.
    
    This generator:
    - Creates extension files with query builders and convenience methods
    - Generates domain-specific methods from configuration
    - Registers methods dynamically on model classes
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        spec_parser: Any,
        file_manager: Optional[Any] = None,
        template_engine: Optional[Any] = None,
        code_formatter: Optional[Any] = None
    ):
        """Initialize ExtensionGenerator."""
        super().__init__(config, spec_parser, file_manager, template_engine, code_formatter)
        self.extensions_config = config.get('extensions', {})
    
    def generate(self) -> GenerationResult:
        """Generate extension methods for models."""
        self.logger.info("Starting extension generation...")
        
        try:
            # Validate prerequisites
            errors = self.validate_generation_prerequisites()
            if errors:
                return self.create_generation_result(
                    success=False,
                    generated_files=[],
                    errors=errors,
                    summary="Extension generation failed validation"
                )
            
            # Get processing order for entities
            processing_order = self.get_processing_order()
            
            generated_files = []
            all_errors = []
            
            # Generate extensions for each entity
            for entity_name in processing_order:
                try:
                    extension_file = self._generate_extension_file(entity_name)
                    if extension_file:
                        generated_files.append(extension_file)
                        self.logger.info(f"Generated extensions for entity: {entity_name}")
                    
                except Exception as e:
                    error_msg = f"Failed to generate extensions for entity {entity_name}: {e}"
                    self.logger.error(error_msg)
                    all_errors.append(error_msg)
            
            success = len(all_errors) == 0
            summary = f"Generated {len(generated_files)} extension files"
            if all_errors:
                summary += f" with {len(all_errors)} errors"
            
            return self.create_generation_result(
                success=success,
                generated_files=generated_files,
                errors=all_errors,
                summary=summary
            )
            
        except Exception as e:
            self.logger.error(f"Extension generation failed: {e}")
            return self.create_generation_result(
                success=False,
                generated_files=[],
                errors=[str(e)],
                summary="Extension generation failed with exception"
            )
    
    def get_required_config_keys(self) -> List[str]:
        """Get required configuration keys."""
        return ['output', 'extensions']
    
    def _generate_extension_file(self, entity_name: str) -> Optional[Path]:
        """Generate extension file for an entity."""
        entity_config = self.get_entity_config(entity_name)
        if not entity_config:
            return None

        extension_path = entity_config.model_config.extension_path
        if not extension_path:
            self.logger.info("Skipping extensions for %s (no extension_path)", entity_name)
            return None

        extensions_dir = self.get_output_directory("extensions")
        extension_filename = f"{extension_path.rsplit('.', 1)[-1]}.py"
        output_path = extensions_dir / extension_filename
        if self._should_skip_protected_generation(output_path):
            return None
        write_path = self._review_sidecar_path(output_path)
        context = self._prepare_extension_context(entity_config)
        self.render_template('extension.py.jinja2', context, write_path)
        if write_path != output_path:
            self.logger.info(
                "Wrote review sidecar %s (hand-maintained %s is protected)",
                write_path,
                output_path,
            )
        return write_path
    
    def _prepare_extension_context(self, entity_config: EntityConfig) -> Dict[str, Any]:
        """Prepare template context for extension generation."""
        # Extract API functions from expansion mappings
        api_functions = []
        for expansion_mapping in entity_config.expansion_mappings.values():
            api_functions.append(expansion_mapping.api_function)
        
        raw_module = (
            entity_config.model_config.module_path
            or f"congressgov.models.entities.{entity_config.name.lower()}"
        )
        raw_service = (
            entity_config.model_config.service_path
            or f"congressgov.services.{entity_config.name.lower()}"
        )
        raw_extension = entity_config.model_config.extension_path or ""

        context = {
            'model_name': entity_config.name,
            'collection_name': entity_config.model_config.collection_class or f"{entity_config.name}s",
            'items_field': entity_config.model_config.items_field or f"{entity_config.name.lower()}s",
            'module_path': normalize_module_path(raw_module),
            'service_path': normalize_service_path(raw_service),
            'extension_path': normalize_extension_path(raw_extension) if raw_extension else "",
            'entity_path': entity_config.name.lower(),
            'mappings_dict_name': f"{entity_config.name.upper()}_MAPPINGS",
            'parameters_dict_name': f"{entity_config.name.upper()}_PARAMETERS",
            'field_mappings': entity_config.field_mappings,
            'expansion_mappings': entity_config.expansion_mappings,
            'parameter_mappings': entity_config.parameter_mappings,
            'extension_methods': entity_config.extension_methods,
            'api_functions': api_functions,
        }
        
        return context


