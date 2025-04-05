"""
Provides baseline financial data and company description from the 2018 10-K.

This module handles the retrieval of baseline financial data and company overview
information for Beauty First Cosmetics (BFC).
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from src.core.config import BASELINE_DATA

@dataclass
class ValidationRule:
    """Validation rule for financial data."""
    field: str
    type_check: type
    min_value: float = None
    max_value: float = None
    required: bool = True

class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass

# Define validation rules for financial data
VALIDATION_RULES: List[ValidationRule] = [
    ValidationRule('revenue', float, min_value=0),
    ValidationRule('operating_margin', float, min_value=-1, max_value=1),
    ValidationRule('market_share', float, min_value=0, max_value=1),
    ValidationRule('net_income', float),
    ValidationRule('total_investment', float, min_value=0),
    ValidationRule('assets', float, min_value=0),
    ValidationRule('liabilities', float, min_value=0),
    ValidationRule('current_assets', float, min_value=0),
    ValidationRule('current_liabilities', float, min_value=0)
]

def validate_field(data: Dict[str, Any], rule: ValidationRule) -> None:
    """
    Validate a single field according to its rule.
    
    Args:
        data: The data dictionary containing the field
        rule: The validation rule to apply
        
    Raises:
        DataValidationError: If the field fails validation
    """
    if rule.field not in data:
        if rule.required:
            raise DataValidationError(f"Required field '{rule.field}' is missing")
        return
    
    value = data[rule.field]
    
    # Type checking
    if not isinstance(value, rule.type_check):
        raise DataValidationError(
            f"Field '{rule.field}' must be of type {rule.type_check.__name__}, got {type(value).__name__}"
        )
    
    # Range checking for numeric fields
    if isinstance(value, (int, float)):
        if rule.min_value is not None and value < rule.min_value:
            raise DataValidationError(
                f"Field '{rule.field}' value {value} is below minimum {rule.min_value}"
            )
        if rule.max_value is not None and value > rule.max_value:
            raise DataValidationError(
                f"Field '{rule.field}' value {value} is above maximum {rule.max_value}"
            )

def get_baseline_data() -> Dict[str, Any]:
    """
    Returns the validated baseline financial data for BFC.

    Returns:
        Dict[str, Any]: A dictionary containing financial metrics and their values.
        
    Raises:
        DataValidationError: If the baseline data fails validation
        ValueError: If the baseline data is empty
    """
    if not BASELINE_DATA:
        raise ValueError("Baseline data is empty")
    
    # Validate all fields
    for rule in VALIDATION_RULES:
        validate_field(BASELINE_DATA, rule)
    
    return BASELINE_DATA

def get_company_overview() -> Dict[str, Any]:
    """
    Returns a detailed company overview based on the 2018 10-K.

    Returns:
        Dict[str, Any]: A dictionary containing company overview information
    """
    overview = {
        'description': (
            "Beauty First Cosmetics (BFC) is a leading U.S.-based cosmetics company with operations across multiple segments "
            "including Cosmetics, Hair, Fragrances, Skin Care, and Beauty Tools. With a 7% market share in a $52B industry, "
            "BFC employs approximately 11,000 people and maintains strong operational and financial fundamentals."
        ),
        'key_segments': [
            'Cosmetics',
            'Hair',
            'Fragrances',
            'Skin Care',
            'Beauty Tools'
        ],
        'market_position': {
            'share': BASELINE_DATA['market_share'],
            'industry_size': 52_000_000_000,  # $52B
            'rank': 'Top 5'
        },
        'employees': 11000,
        'headquarters': 'United States',
        'year_founded': 1985
    }
    return overview

def validate_baseline_data(data: Dict[str, Any]) -> bool:
    """
    Validates the structure and content of baseline financial data.

    Args:
        data (Dict[str, Any]): The baseline data to validate.

    Returns:
        bool: True if the data is valid
        
    Raises:
        DataValidationError: If the data fails validation
    """
    try:
        for rule in VALIDATION_RULES:
            validate_field(data, rule)
        return True
    except DataValidationError:
        return False

def check_data_consistency(data: Dict[str, Any]) -> None:
    """
    Performs consistency checks on the financial data.
    
    Args:
        data: The financial data to check
        
    Raises:
        DataValidationError: If consistency checks fail
    """
    # Assets = Liabilities + Equity
    if all(key in data for key in ['assets', 'liabilities', 'equity']):
        if abs(data['assets'] - (data['liabilities'] + data['equity'])) > 0.01:
            raise DataValidationError("Assets must equal liabilities plus equity")
    
    # Current ratio checks
    if all(key in data for key in ['current_assets', 'current_liabilities']):
        if data['current_assets'] < data['current_liabilities']:
            raise DataValidationError("Current ratio is below 1.0, indicating potential liquidity issues")
    
    # Net income validation
    if all(key in data for key in ['revenue', 'net_income']):
        if data['net_income'] > data['revenue']:
            raise DataValidationError("Net income cannot exceed revenue")
