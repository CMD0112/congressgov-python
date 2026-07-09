"""
Validation utilities with fuzzy matching for parameter suggestions.

This module provides validation functions that can suggest corrections
for invalid parameter values using fuzzy string matching.
"""

import difflib


def suggest_similar(
    invalid_value: str,
    valid_values: list[str],
    max_suggestions: int = 3,
    cutoff: float = 0.6
) -> list[str]:
    """
    Suggest similar valid values using fuzzy matching.
    
    Args:
        invalid_value: The invalid value provided
        valid_values: List of valid values
        max_suggestions: Maximum suggestions to return
        cutoff: Similarity threshold (0-1)
    
    Returns:
        List of suggested corrections
    
    Example:
        >>> suggest_similar("hr", ["hr", "s", "hjres"], max_suggestions=2)
        ['hr']
        >>> suggest_similar("house", ["hr", "s", "hjres"], max_suggestions=2)
        ['hr']
    """
    matches = difflib.get_close_matches(
        invalid_value.lower(),
        [v.lower() for v in valid_values],
        n=max_suggestions,
        cutoff=cutoff
    )
    
    # Map back to original casing
    result = []
    for match in matches:
        for valid in valid_values:
            if valid.lower() == match:
                result.append(valid)
                break
    
    return result


def validate_bill_type(bill_type: str) -> None:
    """
    Validate bill type and provide helpful error.
    
    Args:
        bill_type: The bill type to validate
        
    Raises:
        ValidationError: If bill type is invalid, with suggestions
        
    Example:
        >>> validate_bill_type("hr")  # Valid
        >>> validate_bill_type("invalid")  # Raises ValidationError with suggestions
    """
    valid_types = ['hr', 's', 'hjres', 'sjres', 'hconres', 'sconres', 'hres', 'sres']
    
    if bill_type.lower() not in valid_types:
        suggestions = suggest_similar(bill_type, valid_types)
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Invalid bill type: '{bill_type}'",
            parameter="bill_type",
            value=bill_type,
            suggestions=suggestions,
            valid_values=valid_types
        )


def validate_amendment_type(amendment_type: str) -> None:
    """
    Validate amendment type and provide helpful error.
    
    Args:
        amendment_type: The amendment type to validate
        
    Raises:
        ValidationError: If amendment type is invalid, with suggestions
    """
    valid_types = ['hamdt', 'samdt']
    
    if amendment_type.lower() not in valid_types:
        suggestions = suggest_similar(amendment_type, valid_types)
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Invalid amendment type: '{amendment_type}'",
            parameter="amendment_type",
            value=amendment_type,
            suggestions=suggestions,
            valid_values=valid_types
        )


def validate_chamber(chamber: str) -> None:
    """
    Validate chamber and provide helpful error.
    
    Args:
        chamber: The chamber to validate
        
    Raises:
        ValidationError: If chamber is invalid, with suggestions
    """
    valid_chambers = ['house', 'senate', 'h', 's', 'house of representatives']
    
    if chamber.lower() not in valid_chambers:
        suggestions = suggest_similar(chamber, valid_chambers)
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Invalid chamber: '{chamber}'",
            parameter="chamber",
            value=chamber,
            suggestions=suggestions,
            valid_values=valid_chambers
        )


def validate_congress(congress: int) -> None:
    """
    Validate congress number and provide helpful error.
    
    Args:
        congress: The congress number to validate
        
    Raises:
        ValidationError: If congress number is invalid
    """
    if not isinstance(congress, int):
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Congress must be an integer, got {type(congress).__name__}",
            parameter="congress",
            value=congress,
            constraint="Must be an integer"
        )
    
    if congress < 1 or congress > 150:  # Reasonable range
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Congress number {congress} is outside valid range",
            parameter="congress",
            value=congress,
            constraint="Must be between 1 and 150"
        )


def validate_bioguide_id(bioguide_id: str) -> None:
    """
    Validate Bioguide ID format and provide helpful error.
    
    Args:
        bioguide_id: The Bioguide ID to validate
        
    Raises:
        ValidationError: If Bioguide ID is invalid
    """
    if not isinstance(bioguide_id, str):
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Bioguide ID must be a string, got {type(bioguide_id).__name__}",
            parameter="bioguide_id",
            value=bioguide_id,
            constraint="Must be a string"
        )
    
    if not bioguide_id or len(bioguide_id) < 5:
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Bioguide ID '{bioguide_id}' is too short",
            parameter="bioguide_id",
            value=bioguide_id,
            constraint="Must be at least 5 characters"
        )


def validate_committee_code(committee_code: str) -> None:
    """
    Validate committee code format and provide helpful error.
    
    Args:
        committee_code: The committee code to validate
        
    Raises:
        ValidationError: If committee code is invalid
    """
    if not isinstance(committee_code, str):
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Committee code must be a string, got {type(committee_code).__name__}",
            parameter="committee_code",
            value=committee_code,
            constraint="Must be a string"
        )
    
    if not committee_code or len(committee_code) < 2:
        from congressgov.services.exceptions import ValidationError
        raise ValidationError(
            f"Committee code '{committee_code}' is too short",
            parameter="committee_code",
            value=committee_code,
            constraint="Must be at least 2 characters"
        )
