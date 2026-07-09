"""
Registry Generator for model registry.

This module generates the model registry that provides centralized
model resolution and expansion mappings for the middleware layer.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_generator import BaseGenerator, GenerationResult
from ..utils.module_paths import normalize_module_path

logger = logging.getLogger(__name__)


class RegistryGenerator(BaseGenerator):
    """
    Generator for model registry.
    
    This generator:
    - Creates the model registry with all entity mappings
    - Generates expansion mappings for all entities
    - Provides centralized model resolution
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        spec_parser: Any,
        file_manager: Optional[Any] = None,
        template_engine: Optional[Any] = None,
        code_formatter: Optional[Any] = None
    ):
        """Initialize RegistryGenerator."""
        super().__init__(config, spec_parser, file_manager, template_engine, code_formatter)
        self.registry_config = config.get('registry', {})
    
    def generate(self) -> GenerationResult:
        """Generate model registry."""
        self.logger.info("Starting registry generation...")
        
        try:
            # Validate prerequisites
            errors = self.validate_generation_prerequisites()
            if errors:
                return self.create_generation_result(
                    success=False,
                    generated_files=[],
                    errors=errors,
                    summary="Registry generation failed validation"
                )
            
            # Generate registry file
            registry_file = self._generate_registry_file()
            
            if registry_file:
                return self.create_generation_result(
                    success=True,
                    generated_files=[registry_file],
                    summary="Successfully generated model registry"
                )
            else:
                return self.create_generation_result(
                    success=False,
                    generated_files=[],
                    errors=["Failed to generate registry file"],
                    summary="Registry generation failed"
                )
            
        except Exception as e:
            self.logger.error(f"Registry generation failed: {e}")
            return self.create_generation_result(
                success=False,
                generated_files=[],
                errors=[str(e)],
                summary="Registry generation failed with exception"
            )
    
    def get_required_config_keys(self) -> List[str]:
        """Get required configuration keys."""
        return ['registry']
    
    def _generate_registry_file(self) -> Optional[Path]:
        """Generate model registry file."""
        try:
            registry_file = self.registry_config.get(
                'registry_file', 'src/congressgov/services/core/model_registry.py'
            )
            output_path = Path(registry_file)
            
            # Prepare template context
            context = self._prepare_registry_context()
            
            # Render template
            self.render_template(
                'registry.py.jinja2',
                context,
                output_path
            )
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate registry file: {e}")
            return None
    
    def _prepare_registry_context(self) -> Dict[str, Any]:
        """Prepare template context for registry generation."""
        entities = self.get_all_entities()
        entity_models = []
        model_path_entries: list[dict[str, str]] = []
        seen: set[str] = set()

        def add_path(name: str, path: str) -> None:
            normalized = normalize_module_path(path)
            if name and normalized and name not in seen:
                model_path_entries.append({"name": name, "path": normalized})
                seen.add(name)

        for entity_name, entity_config in entities.items():
            model_config = entity_config.model_config
            raw_path = (
                model_config.module_path
                if model_config and model_config.module_path
                else f"congressgov.models.entities.{entity_name.lower()}"
            )
            module_path = normalize_module_path(raw_path)
            entity_models.append({
                "name": entity_config.name,
                "model_name": entity_config.name,
                "collection_name": model_config.collection_class if model_config else None,
                "module_path": module_path,
            })
            add_path(entity_config.name, module_path)
            if model_config and model_config.collection_class:
                add_path(model_config.collection_class, module_path)

        return {
            "entity_models": entity_models,
            "model_path_entries": sorted(model_path_entries, key=lambda e: e["name"]),
        }


