"""
Provides baseline financial data and company description from the 2018 10-K.
"""

from bfc_reports.config import BASELINE_DATA

def get_baseline_data():
    """
    Returns the baseline financial data for BFC.
    """
    return BASELINE_DATA

def get_company_overview():
    """
    Returns a brief company description based on the 2018 10-K.
    """
    overview = (
        "Beauty First Cosmetics (BFC) is a leading U.S.-based cosmetics company with operations across multiple segments "
        "including Cosmetics, Hair, Fragrances, Skin Care, and Beauty Tools. With a 7% market share in a $52B industry, "
        "BFC employs approximately 11,000 people and maintains strong operational and financial fundamentals."
    )
    return overview
