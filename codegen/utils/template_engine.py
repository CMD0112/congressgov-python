"""
Template Engine for Jinja2-based code generation.

This module provides utilities for:
- Loading and rendering Jinja2 templates
- Template caching for performance
- Template validation and error handling
- Custom template filters and functions
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from jinja2 import (
    Environment, 
    FileSystemLoader, 
    Template, 
    TemplateNotFound,
    TemplateSyntaxError,
    UndefinedError
)

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Engine for Jinja2 template rendering with caching and custom filters.
    
    Features:
    - Template caching for performance
    - Custom filters for code generation
    - Error handling and validation
    - Support for template inheritance
    """
    
    def __init__(
        self,
        template_dirs: Union[str, Path, list[Union[str, Path]]],
        cache_templates: bool = True,
        auto_reload: bool = False
    ):
        """
        Initialize TemplateEngine.
        
        Args:
            template_dirs: Directory or list of directories containing templates
            cache_templates: Whether to cache compiled templates
            auto_reload: Whether to automatically reload templates on changes
        """
        self.cache_templates = cache_templates
        self.template_cache: Dict[str, Template] = {}
        
        # Convert single directory to list
        if isinstance(template_dirs, (str, Path)):
            template_dirs = [template_dirs]
        
        # Convert to Path objects
        self.template_dirs = [Path(d) for d in template_dirs]
        
        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader([str(d) for d in self.template_dirs]),
            autoescape=False,  # We're generating code, not HTML
            trim_blocks=True,
            lstrip_blocks=True,
            cache_size=100 if cache_templates else 0
        )
        
        # Add custom filters
        self._add_custom_filters()
        
        logger.debug(f"Initialized TemplateEngine with directories: {self.template_dirs}")
    
    def _add_custom_filters(self) -> None:
        """Add custom filters for code generation (Jinja2 3.x: assign via .filters / .globals)."""
        import re
        import textwrap

        def to_snake_case(value: str) -> str:
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
            return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        def to_camel_case(value: str) -> str:
            components = value.split("_")
            return components[0] + "".join(x.capitalize() for x in components[1:])

        def to_pascal_case(value: str) -> str:
            components = value.split("_")
            return "".join(x.capitalize() for x in components)

        def to_plural(value: str) -> str:
            if value.endswith("y"):
                return value[:-1] + "ies"
            if value.endswith(("s", "sh", "ch", "x", "z")):
                return value + "es"
            return value + "s"

        def to_singular(value: str) -> str:
            if value.endswith("ies"):
                return value[:-3] + "y"
            if value.endswith(("ses", "shes", "ches", "xes", "zes")):
                return value[:-2]
            if value.endswith("s") and len(value) > 3:
                return value[:-1]
            return value

        def indent(value: str, spaces: int = 4) -> str:
            if not value:
                return value
            indent_str = " " * spaces
            lines = value.split("\n")
            return "\n".join(indent_str + line if line.strip() else line for line in lines)

        def join_lines(value: list[str], separator: str = "\n") -> str:
            return separator.join(str(item) for item in value if item)

        def wrap_lines(value: str, width: int = 88) -> str:
            lines = value.split("\n")
            wrapped_lines = []
            for line in lines:
                if len(line) <= width:
                    wrapped_lines.append(line)
                else:
                    wrapped_lines.extend(textwrap.wrap(line, width))
            return "\n".join(wrapped_lines)

        def python_type(openapi_type: str, format_: Optional[str] = None) -> str:
            type_mapping = {
                "string": "str",
                "integer": "int",
                "number": "float",
                "boolean": "bool",
                "array": "list",
                "object": "dict",
            }
            base_type = type_mapping.get(openapi_type, "Any")
            if format_:
                format_mapping = {
                    "date": "date",
                    "date-time": "datetime",
                    "time": "time",
                    "uri": "str",
                    "email": "str",
                    "uuid": "str",
                }
                base_type = format_mapping.get(format_, base_type)
            return base_type

        def import_statements(types: list[str]) -> list[str]:
            imports: set[str] = set()
            for type_hint in types:
                if "datetime" in type_hint:
                    imports.add("from datetime import datetime, date")
                elif "List" in type_hint or "list[" in type_hint:
                    imports.add("from typing import List")
                elif "Optional" in type_hint:
                    imports.add("from typing import Optional")
                elif "Union" in type_hint:
                    imports.add("from typing import Union")
                elif "Any" in type_hint:
                    imports.add("from typing import Any")
            return sorted(imports)

        def to_json(value: object) -> str:
            return json.dumps(value)

        self.env.filters.update(
            {
                "to_json": to_json,
                "to_snake_case": to_snake_case,
                "to_camel_case": to_camel_case,
                "to_pascal_case": to_pascal_case,
                "to_plural": to_plural,
                "to_singular": to_singular,
                "indent": indent,
                "join_lines": join_lines,
                "wrap_lines": wrap_lines,
            }
        )
        self.env.globals["python_type"] = python_type
        self.env.globals["import_statements"] = import_statements
    
    def get_template(self, name: str) -> Template:
        """
        Get template by name with caching.
        
        Args:
            name: Template name (relative to template directories)
            
        Returns:
            Jinja2 Template object
            
        Raises:
            TemplateNotFound: If template doesn't exist
            TemplateSyntaxError: If template has syntax errors
        """
        # Check cache first
        if self.cache_templates and name in self.template_cache:
            return self.template_cache[name]
        
        try:
            template = self.env.get_template(name)
            
            # Cache template if caching is enabled
            if self.cache_templates:
                self.template_cache[name] = template
            
            logger.debug(f"Loaded template: {name}")
            return template
            
        except TemplateNotFound:
            logger.error(f"Template not found: {name}")
            raise
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in {name}: {e}")
            raise
    
    def render_template(
        self,
        template_name: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Render template with context.
        
        Args:
            template_name: Name of template to render
            context: Template context dictionary
            **kwargs: Additional context variables
            
        Returns:
            Rendered template content
            
        Raises:
            TemplateNotFound: If template doesn't exist
            TemplateSyntaxError: If template has syntax errors
            UndefinedError: If template references undefined variables
        """
        template = self.get_template(template_name)
        
        # Merge context with kwargs
        render_context = context or {}
        render_context.update(kwargs)
        
        try:
            rendered = template.render(**render_context)
            logger.debug(f"Rendered template: {template_name}")
            return rendered
            
        except UndefinedError as e:
            logger.error(f"Undefined variable in template {template_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise
    
    def render_string(
        self,
        template_string: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Render template from string.
        
        Args:
            template_string: Template content as string
            context: Template context dictionary
            **kwargs: Additional context variables
            
        Returns:
            Rendered template content
        """
        # Merge context with kwargs
        render_context = context or {}
        render_context.update(kwargs)
        
        try:
            template = self.env.from_string(template_string)
            rendered = template.render(**render_context)
            logger.debug("Rendered template from string")
            return rendered
            
        except Exception as e:
            logger.error(f"Error rendering template from string: {e}")
            raise
    
    def list_templates(self, extension: str = '.jinja2') -> list[str]:
        """
        List available templates.
        
        Args:
            extension: Template file extension to filter by
            
        Returns:
            List of template names
        """
        templates = []
        
        for template_dir in self.template_dirs:
            if not template_dir.exists():
                continue
                
            for template_file in template_dir.rglob(f'*{extension}'):
                # Get relative path from template directory
                rel_path = template_file.relative_to(template_dir)
                template_name = str(rel_path)
                templates.append(template_name)
        
        return sorted(templates)
    
    def template_exists(self, name: str) -> bool:
        """
        Check if template exists.
        
        Args:
            name: Template name
            
        Returns:
            True if template exists
        """
        try:
            self.env.get_template(name)
            return True
        except TemplateNotFound:
            return False
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self.template_cache.clear()
        self.env.cache.clear()
        logger.debug("Cleared template cache")
    
    def reload_template(self, name: str) -> Template:
        """
        Force reload template (useful when template has changed).
        
        Args:
            name: Template name
            
        Returns:
            Reloaded template
        """
        # Remove from cache if present
        if name in self.template_cache:
            del self.template_cache[name]
        
        # Clear environment cache for this template
        self.env.cache.clear()
        
        # Reload template
        return self.get_template(name)


