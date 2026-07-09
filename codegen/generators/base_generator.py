"""
Base Generator class for code generation components.

This module provides the base functionality for all generators including:
- Common generation patterns
- Configuration management
- Error handling and logging
- File operations and validation
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from ..utils.file_manager import FileManager
from ..utils.template_engine import TemplateEngine
from ..utils.code_formatter import CodeFormatter
from ..processors.spec_parser import SpecParser, EntityConfig

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result of a code generation operation."""
    success: bool
    generated_files: List[Path]
    errors: List[str]
    warnings: List[str]
    summary: str


class BaseGenerator(ABC):
    """
    Base class for all code generators.
    
    Provides common functionality for:
    - Configuration management
    - File operations
    - Template rendering
    - Code formatting
    - Error handling and logging
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        spec_parser: SpecParser,
        file_manager: Optional[FileManager] = None,
        template_engine: Optional[TemplateEngine] = None,
        code_formatter: Optional[CodeFormatter] = None
    ):
        """
        Initialize BaseGenerator.
        
        Args:
            config: Generator configuration dictionary
            spec_parser: Parsed OpenAPI specification
            file_manager: File manager for safe file operations
            template_engine: Template engine for rendering
            code_formatter: Code formatter for Python code
        """
        self.config = config
        self.spec_parser = spec_parser
        self.file_manager = file_manager or FileManager()
        self.template_engine = template_engine or TemplateEngine(
            template_dirs=[Path(__file__).parent.parent / "templates"]
        )
        self.code_formatter = code_formatter or CodeFormatter()
        self._generation_config = config.get("generation", {})
        
        # Initialize logger
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def _emit_review_sidecars(self) -> bool:
        """When True, protected middleware/extension paths write *.generated.py sidecars."""
        return bool(self.config.get("middleware", {}).get("emit_review_sidecars", False))

    def _should_skip_protected_generation(self, output_path: Path) -> bool:
        """Skip writes to protected hand modules when review sidecars are disabled."""
        if self._emit_review_sidecars():
            return False
        if self.file_manager.is_protected(output_path):
            self.logger.info(
                "Skipped generation for protected path %s (emit_review_sidecars=false)",
                output_path.as_posix(),
            )
            return True
        return False

    def _review_sidecar_path(self, output_path: Path) -> Path:
        """When target is protected and sidecars enabled, write a review sidecar instead."""
        if not self.file_manager.is_protected(output_path):
            return output_path
        if not self._emit_review_sidecars():
            return output_path
        suffix = self.config.get("middleware", {}).get("review_sidecar_suffix", ".generated")
        return output_path.with_name(f"{output_path.stem}{suffix}{output_path.suffix}")

    def _write_generated_file(
        self,
        output_path: Path,
        content: str,
        create_backup: bool = True,
        *,
        fail_if_protected: bool = True,
    ) -> Path:
        """Write generated content, honoring incremental merge when configured."""
        output_path = Path(output_path)
        if fail_if_protected and self.file_manager.is_protected(output_path):
            raise RuntimeError(
                f"Refusing to skip write to protected path: {output_path.as_posix()}"
            )
        use_incremental = self._generation_config.get("incremental", False)
        if output_path.name.endswith(".generated.py"):
            use_incremental = False
        if use_incremental:
            return self.file_manager.write_incremental(
                output_path,
                content,
                create_backup=create_backup,
            )
        return self.file_manager.write_file(
            output_path,
            content,
            create_backup=create_backup,
        )
    
    @abstractmethod
    def generate(self) -> GenerationResult:
        """
        Generate code for this generator.
        
        Returns:
            GenerationResult with success status and details
        """
        pass
    
    def validate_configuration(self) -> List[str]:
        """
        Validate generator configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required configuration keys
        required_keys = self.get_required_config_keys()
        for key in required_keys:
            if key not in self.config:
                errors.append(f"Missing required configuration key: {key}")
        
        return errors
    
    @abstractmethod
    def get_required_config_keys(self) -> List[str]:
        """
        Get list of required configuration keys.
        
        Returns:
            List of required configuration key names
        """
        pass
    
    def ensure_output_directory(self, output_path: Union[str, Path]) -> Path:
        """
        Ensure output directory exists.
        
        Args:
            output_path: Output file or directory path
            
        Returns:
            Path to output directory
        """
        output_path = Path(output_path)
        
        if output_path.suffix:
            # It's a file path, get the parent directory
            output_dir = output_path.parent
        else:
            # It's a directory path
            output_dir = output_path
        
        return self.file_manager.ensure_directory(output_dir)
    
    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[Union[str, Path]] = None,
        format_code: bool = True
    ) -> Union[str, Path]:
        """
        Render template and optionally write to file.
        
        Args:
            template_name: Name of template to render
            context: Template context variables
            output_path: Optional output file path
            format_code: Whether to format the generated code
            
        Returns:
            Rendered content (if no output_path) or output file path
        """
        try:
            # Render template
            content = self.template_engine.render_template(template_name, context)
            
            # Format code if requested
            if format_code and template_name.endswith('.py.jinja2'):
                formatting_result = self.code_formatter.format_content(content)
                if formatting_result.success:
                    content = formatting_result.formatted_content
                else:
                    self.logger.warning(f"Code formatting failed: {formatting_result.errors}")
            
            # Write to file if output path provided
            if output_path:
                output_path = Path(output_path)
                self.ensure_output_directory(output_path)
                written_path = self._write_generated_file(output_path, content)
                self.logger.info(f"Generated file: {written_path}")
                return written_path
            else:
                return content
                
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {e}")
            raise
    
    def get_entity_config(self, entity_name: str) -> Optional[EntityConfig]:
        """
        Get entity configuration by name.
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            EntityConfig if found, None otherwise
        """
        return self.spec_parser.get_entity(entity_name)
    
    def get_all_entities(self) -> Dict[str, EntityConfig]:
        """
        Get all entity configurations.
        
        Returns:
            Dictionary of all entity configurations
        """
        return self.spec_parser.get_all_entities()
    
    def get_processing_order(self) -> List[str]:
        """
        Get the order in which entities should be processed.
        
        Returns:
            List of entity names in processing order
        """
        entities = self.get_all_entities()
        if not entities:
            return []
        from ..processors.relationship_resolver import RelationshipResolver

        resolver = RelationshipResolver()
        return resolver.get_processing_order(entities)
    
    def validate_generation_prerequisites(self) -> List[str]:
        """
        Validate prerequisites for code generation.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate configuration
        config_errors = self.validate_configuration()
        errors.extend(config_errors)
        
        # Validate spec parser
        if not self.spec_parser.entities:
            errors.append("No entities found in OpenAPI specification")
        
        # Validate template engine
        if not self.template_engine.list_templates():
            errors.append("No templates found in template directories")
        
        return errors
    
    def log_generation_summary(
        self,
        result: GenerationResult,
        generator_name: str
    ) -> None:
        """
        Log generation summary.
        
        Args:
            result: Generation result
            generator_name: Name of the generator
        """
        if result.success:
            self.logger.info(f"{generator_name} generation completed successfully")
            self.logger.info(f"Generated {len(result.generated_files)} files")
            if result.generated_files:
                for file_path in result.generated_files:
                    self.logger.debug(f"  - {file_path}")
        else:
            self.logger.error(f"{generator_name} generation failed")
            for error in result.errors:
                self.logger.error(f"  - {error}")
        
        if result.warnings:
            for warning in result.warnings:
                self.logger.warning(f"  - {warning}")
    
    def create_generation_result(
        self,
        success: bool,
        generated_files: List[Path],
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        summary: Optional[str] = None
    ) -> GenerationResult:
        """
        Create a GenerationResult object.
        
        Args:
            success: Whether generation was successful
            generated_files: List of generated file paths
            errors: List of error messages
            warnings: List of warning messages
            summary: Summary of generation results
            
        Returns:
            GenerationResult object
        """
        if errors is None:
            errors = []
        if warnings is None:
            warnings = []
        
        if summary is None:
            if success:
                summary = f"Successfully generated {len(generated_files)} files"
            else:
                summary = f"Generation failed with {len(errors)} errors"
        
        return GenerationResult(
            success=success,
            generated_files=generated_files,
            errors=errors,
            warnings=warnings,
            summary=summary
        )
    
    def get_output_directory(self, component: str) -> Path:
        """
        Get output directory for a component.
        
        Args:
            component: Component name (e.g., 'models', 'middleware', 'extensions')
            
        Returns:
            Path to output directory
        """
        output_config = self.config.get('output', {})
        output_path = output_config.get(component)
        
        if not output_path:
            raise ValueError(f"No output directory configured for component: {component}")
        
        return Path(output_path)
    
    def get_template_name(self, template_type: str) -> str:
        """
        Get template name for a template type.
        
        Args:
            template_type: Type of template (e.g., 'model', 'service', 'extension')
            
        Returns:
            Template file name
        """
        return f"{template_type}.py.jinja2"
    
    def prepare_template_context(
        self,
        entity_config: EntityConfig,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare template context for an entity.
        
        Args:
            entity_config: Entity configuration
            additional_context: Additional context variables
            
        Returns:
            Template context dictionary
        """
        context = {
            'model_name': entity_config.name,
            'collection_name': entity_config.model_config.collection_class,
            'items_field': entity_config.model_config.items_field,
            'module_path': entity_config.model_config.module_path,
            'service_path': entity_config.model_config.service_path,
            'extension_path': entity_config.model_config.extension_path,
            'field_mappings': entity_config.field_mappings,
            'expansion_mappings': entity_config.expansion_mappings,
            'parameter_mappings': entity_config.parameter_mappings,
            'extension_methods': entity_config.extension_methods,
            'schemas': entity_config.schemas,
        }
        
        # Add additional context
        if additional_context:
            context.update(additional_context)
        
        return context
    
    def safe_generate_file(
        self,
        output_path: Union[str, Path],
        content: str,
        create_backup: bool = True
    ) -> Path:
        """
        Safely generate a file with backup and error handling.
        
        Args:
            output_path: Output file path
            content: File content
            create_backup: Whether to create backup
            
        Returns:
            Path to generated file
        """
        try:
            output_path = Path(output_path)
            self.ensure_output_directory(output_path)
            
            self._write_generated_file(output_path, content, create_backup=create_backup)
            
            self.logger.info(f"Generated file: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate file {output_path}: {e}")
            raise


