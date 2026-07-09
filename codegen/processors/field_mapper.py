"""
Field Mapper for converting OpenAPI schema fields to Python model fields.

This module provides utilities for:
- Mapping OpenAPI field types to Python types
- Generating Pydantic field definitions
- Handling field constraints and validations
- Converting field names and formats
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FieldDefinition:
    """Definition of a Python model field."""
    name: str
    python_type: str
    openapi_type: str
    format_: Optional[str] = None
    description: Optional[str] = None
    default_value: Optional[Any] = None
    is_required: bool = False
    is_optional: bool = False
    is_array: bool = False
    is_object: bool = False
    enum_values: Optional[List[str]] = None
    constraints: Dict[str, Any] = None
    alias: Optional[str] = None
    field_imports: Set[str] = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}
        if self.field_imports is None:
            self.field_imports = set()


class FieldMapper:
    """
    Mapper for converting OpenAPI schema fields to Python model fields.
    
    Features:
    - Type mapping from OpenAPI to Python
    - Pydantic field generation
    - Constraint handling
    - Import statement generation
    """
    
    def __init__(self):
        """Initialize FieldMapper."""
        # OpenAPI to Python type mapping
        self.type_mapping = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict'
        }
        
        # Format to Python type mapping
        self.format_mapping = {
            'date': 'date',
            'date-time': 'datetime',
            'time': 'time',
            'uri': 'str',
            'email': 'str',
            'uuid': 'str',
            'byte': 'bytes',
            'binary': 'bytes',
            'int32': 'int',
            'int64': 'int',
            'float': 'float',
            'double': 'float'
        }
        
        # Special type imports
        self.special_imports = {
            'date': 'from datetime import date',
            'datetime': 'from datetime import datetime',
            'time': 'from datetime import time',
            'uuid': 'import uuid',
            'bytes': None,  # Built-in
        }
    
    def map_field(
        self,
        field_name: str,
        field_schema: Dict[str, Any],
        is_required: bool = False
    ) -> FieldDefinition:
        """
        Map OpenAPI field schema to Python field definition.
        
        Args:
            field_name: Name of the field
            field_schema: OpenAPI field schema
            is_required: Whether the field is required
            
        Returns:
            FieldDefinition object
        """
        # Extract basic information
        openapi_type = field_schema.get('type', 'string')
        format_ = field_schema.get('format')
        description = field_schema.get('description')
        default_value = field_schema.get('default')
        enum_values = field_schema.get('enum')
        
        # Determine Python type
        python_type = self._get_python_type(openapi_type, format_, enum_values)
        
        # Handle special types
        is_array = openapi_type == 'array'
        is_object = openapi_type == 'object'
        is_optional = not is_required and default_value is None
        
        # Generate field imports
        field_imports = self._get_field_imports(python_type, openapi_type, format_)
        
        # Handle constraints
        constraints = self._extract_constraints(field_schema)
        
        # Generate alias if needed
        alias = self._generate_alias(field_name)
        
        # Adjust type for optional fields
        if is_optional:
            python_type = f"Optional[{python_type}]"
            field_imports.add("from typing import Optional")
        
        # Handle arrays
        if is_array:
            items_schema = field_schema.get('items', {})
            item_type = self._get_python_type(
                items_schema.get('type', 'string'),
                items_schema.get('format'),
                items_schema.get('enum')
            )
            python_type = f"list[{item_type}]"
            field_imports.add("from typing import List")
            
            # Add imports for item type
            item_imports = self._get_field_imports(item_type, items_schema.get('type'), items_schema.get('format'))
            field_imports.update(item_imports)
        
        return FieldDefinition(
            name=field_name,
            python_type=python_type,
            openapi_type=openapi_type,
            format_=format_,
            description=description,
            default_value=default_value,
            is_required=is_required,
            is_optional=is_optional,
            is_array=is_array,
            is_object=is_object,
            enum_values=enum_values,
            constraints=constraints,
            alias=alias,
            field_imports=field_imports
        )
    
    def _get_python_type(
        self,
        openapi_type: str,
        format_: Optional[str] = None,
        enum_values: Optional[List[str]] = None
    ) -> str:
        """
        Get Python type from OpenAPI type and format.
        
        Args:
            openapi_type: OpenAPI type
            format_: OpenAPI format
            enum_values: Enum values if applicable
            
        Returns:
            Python type string
        """
        # Handle enums
        if enum_values is not None:
            return "str"  # Enums are handled separately
        
        # Handle format-specific types
        if format_ and format_ in self.format_mapping:
            return self.format_mapping[format_]
        
        # Handle basic types
        if openapi_type in self.type_mapping:
            return self.type_mapping[openapi_type]
        
        # Handle references (objects)
        if openapi_type == 'object' or '$ref' in str(openapi_type):
            return "Any"  # Will be resolved later
        
        # Default fallback
        return "Any"
    
    def _get_field_imports(
        self,
        python_type: str,
        openapi_type: str,
        format_: Optional[str] = None
    ) -> Set[str]:
        """
        Get required imports for a field type.
        
        Args:
            python_type: Python type string
            openapi_type: OpenAPI type
            format_: OpenAPI format
            
        Returns:
            Set of import statements
        """
        imports = set()
        
        # Add imports for special types
        if python_type in self.special_imports:
            import_stmt = self.special_imports[python_type]
            if import_stmt:
                imports.add(import_stmt)
        
        # Add Any import for complex types
        if 'Any' in python_type:
            imports.add("from typing import Any")
        
        return imports
    
    def _extract_constraints(self, field_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract validation constraints from field schema.
        
        Args:
            field_schema: OpenAPI field schema
            
        Returns:
            Dictionary of constraints
        """
        constraints = {}
        
        # Numeric constraints
        if 'minimum' in field_schema:
            constraints['ge'] = field_schema['minimum']
        if 'maximum' in field_schema:
            constraints['le'] = field_schema['maximum']
        if 'exclusiveMinimum' in field_schema:
            constraints['gt'] = field_schema['exclusiveMinimum']
        if 'exclusiveMaximum' in field_schema:
            constraints['lt'] = field_schema['exclusiveMaximum']
        if 'multipleOf' in field_schema:
            constraints['multiple_of'] = field_schema['multipleOf']
        
        # String constraints
        if 'minLength' in field_schema:
            constraints['min_length'] = field_schema['minLength']
        if 'maxLength' in field_schema:
            constraints['max_length'] = field_schema['maxLength']
        if 'pattern' in field_schema:
            constraints['pattern'] = field_schema['pattern']
        
        # Array constraints
        if 'minItems' in field_schema:
            constraints['min_items'] = field_schema['minItems']
        if 'maxItems' in field_schema:
            constraints['max_items'] = field_schema['maxItems']
        
        return constraints
    
    def _generate_alias(self, field_name: str) -> Optional[str]:
        """
        Generate field alias if needed.
        
        Args:
            field_name: Field name
            
        Returns:
            Alias if needed, None otherwise
        """
        # Convert snake_case to camelCase for API compatibility
        if '_' in field_name:
            parts = field_name.split('_')
            camel_case = parts[0] + ''.join(word.capitalize() for word in parts[1:])
            return camel_case
        
        return None
    
    def generate_field_code(self, field_def: FieldDefinition) -> str:
        """
        Generate Python field code from FieldDefinition.
        
        Args:
            field_def: Field definition
            
        Returns:
            Python field code
        """
        lines = []
        
        # Start with field name and type
        line = f"    {field_def.name}: {field_def.python_type}"
        
        # Add Field() with parameters
        field_params = []
        
        # Add default value
        if field_def.default_value is not None:
            if isinstance(field_def.default_value, str):
                field_params.append(f'default="{field_def.default_value}"')
            else:
                field_params.append(f'default={field_def.default_value}')
        elif field_def.is_optional:
            field_params.append('default=None')
        
        # Add alias
        if field_def.alias:
            field_params.append(f'alias="{field_def.alias}"')
        
        # Add description
        if field_def.description:
            # Escape quotes in description
            desc = field_def.description.replace('"', '\\"')
            field_params.append(f'description="{desc}"')
        
        # Add constraints
        for constraint_name, constraint_value in field_def.constraints.items():
            if isinstance(constraint_value, str):
                field_params.append(f'{constraint_name}="{constraint_value}"')
            else:
                field_params.append(f'{constraint_name}={constraint_value}')
        
        # Complete the field definition
        if field_params:
            line += " = Field(\n"
            line += ",\n".join(f"        {param}" for param in field_params)
            line += "\n    )"
        else:
            line += " = Field()"
        
        lines.append(line)
        
        return '\n'.join(lines)
    
    def generate_all_imports(self, field_definitions: List[FieldDefinition]) -> Set[str]:
        """
        Generate all required imports for field definitions.
        
        Args:
            field_definitions: List of field definitions
            
        Returns:
            Set of unique import statements
        """
        all_imports = set()
        
        for field_def in field_definitions:
            all_imports.update(field_def.field_imports)
        
        # Add common imports
        all_imports.add("from pydantic import Field")
        
        return all_imports
    
    def map_schema_fields(
        self,
        schema: Dict[str, Any],
        required_fields: Optional[List[str]] = None
    ) -> List[FieldDefinition]:
        """
        Map all fields in a schema to field definitions.
        
        Args:
            schema: OpenAPI schema
            required_fields: List of required field names
            
        Returns:
            List of field definitions
        """
        if required_fields is None:
            required_fields = []
        
        properties = schema.get('properties', {})
        field_definitions = []
        
        for field_name, field_schema in properties.items():
            is_required = field_name in required_fields
            field_def = self.map_field(field_name, field_schema, is_required)
            field_definitions.append(field_def)
        
        return field_definitions


