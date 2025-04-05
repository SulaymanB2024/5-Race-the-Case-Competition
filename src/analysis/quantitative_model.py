"""
Simplified quantitative model focused on calculating projections for 10-K reports.
(Version 3 - Refined Docs & Calc Clarity)
"""

from typing import Dict, Any, Union, Optional # Added Optional, Union
import logging

logger = logging.getLogger(__name__) # Logger for this module

# Helper to safely get numeric values
def _safe_get_numeric(data: Dict, key: str, default: float = 0.0) -> float:
    """Safely retrieves a numeric value from a dictionary, logging warnings."""
    val = data.get(key)
    if val is None:
        # logger.debug(f"Key '{key}' not found in data. Using default {default}.") # Debug level maybe
        return default
    if not isinstance(val, (int, float)):
        logger.warning(f"Non-numeric value ('{val}' type: {type(val).__name__}) for key '{key}'. Using default {default}.")
        return default
    return float(val)

def _calculate_cagr(start_val: Optional[Union[int, float]],
                    end_val: Optional[Union[int, float]],
                    num_years: int) -> Union[float, str]:
    """
    Calculates Compound Annual Growth Rate (CAGR) as a percentage.

    Handles edge cases like zero/negative base values or zero years.

    Args:
        start_val: The starting value.
        end_val: The ending value.
        num_years: The number of years between start and end values.

    Returns:
        The CAGR as a float (percentage), or a string indicating why it couldn't be calculated.
    """
    if not isinstance(num_years, int) or num_years <= 0:
        return "N/A (Invalid Years)"
    if not all(isinstance(v, (int, float)) for v in [start_val, end_val]):
        return "N/A (Invalid Values)"
    if start_val == 0:
        # Cannot calculate CAGR if starting from zero
        return "N/A (Zero Base)"
    # Meaningful CAGR typically requires positive start/end values
    if start_val < 0 or end_val < 0:
        # logger.warning(f"CAGR calculation with negative values ({start_val} -> {end_val}) is generally not meaningful.")
        return "N/A (Negative Value)"

    try:
        # Calculate CAGR: ((End / Start) ^ (1 / Years)) - 1
        cagr = ((end_val / start_val)**(1.0 / num_years) - 1) * 100.0
        # Check for potential complex results (e.g., negative base with non-integer power)
        if isinstance(cagr, complex):
             logger.error(f"Complex number resulted from CAGR calculation: {start_val}, {end_val}, {num_years}")
             return "N/A (Calculation Error)"
        return cagr
    except (ValueError, OverflowError, ZeroDivisionError) as e:
         logger.error(f"Error calculating CAGR ({start_val=}, {end_val=}, {num_years=}): {e}")
         return "N/A (Calculation Error)"


def calculate_10k_projections(baseline_data: Dict[str, Any], growth_assumptions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates projected financial figures for 1, 5, 10-year horizons.

    Projects Revenue, EBITDA, R&D Spend, and Net Income based on baseline data
    and growth assumptions defined per timeframe. Also calculates implied CAGR
    for each projected metric.

    Args:
        baseline_data: Dictionary of baseline (e.g., 2018) financial figures.
                       Expected keys: 'revenue', 'ebitda', 'ebitda_margin',
                                      'r_and_d_spend', 'net_income'.
        growth_assumptions: Dictionary containing growth factors per timeframe.
                            Keys: 'one_year', 'five_year', 'ten_year'.
                            Each timeframe dict expected keys: 'revenue_growth_pct' or
                            'cumulative_revenue_growth_pct', 'ebitda_margin_improvement',
                            'r_and_d_increase'.

    Returns:
        Dictionary containing baseline data ('baseline' key) and calculated
        projections ('one_year', 'five_year', 'ten_year' keys). Each timeframe
        projection includes 'projected_revenue', 'projected_ebitda',
        'projected_r_and_d_spend', 'projected_net_income', and their '..._cagr'.
    """
    logger.debug("Starting projection calculations...")
    results: Dict[str, Any] = {'baseline': baseline_data.copy()} # Start with baseline copy

    # --- Baseline Figures Extraction ---
    # Use safe_get to handle potential missing keys gracefully
    base_revenue = _safe_get_numeric(baseline_data, 'revenue')
    base_ebitda = _safe_get_numeric(baseline_data, 'ebitda')
    base_ebitda_margin = _safe_get_numeric(baseline_data, 'ebitda_margin')
    base_rnd_spend = _safe_get_numeric(baseline_data, 'r_and_d_spend')
    base_net_income = _safe_get_numeric(baseline_data, 'net_income')
    # Calculate baseline net margin only if needed and possible
    base_net_margin = (base_net_income / base_revenue) if base_revenue != 0 else 0.0
    logger.debug(f"Using Baseline - Revenue: {base_revenue:.1f}M, EBITDA: {base_ebitda:.1f}M, Net Income: {base_net_income:.1f}M, R&D: {base_rnd_spend:.1f}M")

    # --- Projection Loop ---
    for timeframe in ['one_year', 'five_year', 'ten_year']:
        logger.debug(f"Calculating projections for: {timeframe}")
        if timeframe not in growth_assumptions:
            logger.warning(f"Growth assumptions missing for timeframe: {timeframe}. Skipping.")
            results[timeframe] = {} # Store empty dict
            continue

        assumptions: Dict = growth_assumptions[timeframe]
        projections: Dict[str, Any] = {} # Initialize dict for this timeframe's projections
        years: int = {'one_year': 1, 'five_year': 5, 'ten_year': 10}.get(timeframe, 0)

        # --- 1. Revenue Projection ---
        proj_rev: float = 0.0
        if timeframe == 'one_year':
            rev_growth_pct = _safe_get_numeric(assumptions, 'revenue_growth_pct', 0.0)
            proj_rev = base_revenue * (1 + rev_growth_pct / 100.0)
        else:
            # Cumulative growth: Projected = Base * (1 + Cumulative Rate)
            cum_rev_growth_pct = _safe_get_numeric(assumptions, 'cumulative_revenue_growth_pct', 0.0)
            proj_rev = base_revenue * (1 + cum_rev_growth_pct / 100.0)
        projections['projected_revenue'] = proj_rev
        projections['revenue_cagr'] = _calculate_cagr(base_revenue, proj_rev, years)
        logger.debug(f"  {timeframe} Revenue -> {proj_rev:.1f}M (CAGR: {projections['revenue_cagr']})")


        # --- 2. EBITDA Projection ---
        ebitda_margin_improvement_pp = _safe_get_numeric(assumptions, 'ebitda_margin_improvement', 0.0)
        # Ensure projected margin doesn't go below a reasonable floor (e.g., 0) or above ceiling (e.g., 100%)
        proj_ebitda_margin = max(0.0, min(1.0, base_ebitda_margin + (ebitda_margin_improvement_pp / 100.0)))
        proj_ebitda = proj_rev * proj_ebitda_margin
        projections['projected_ebitda'] = proj_ebitda
        projections['projected_ebitda_margin'] = proj_ebitda_margin
        projections['ebitda_cagr'] = _calculate_cagr(base_ebitda, proj_ebitda, years)
        logger.debug(f"  {timeframe} EBITDA -> {proj_ebitda:.1f}M (Margin: {proj_ebitda_margin*100:.1f}%, CAGR: {projections['ebitda_cagr']})")


        # --- 3. R&D Spend Projection ---
        rnd_increase_pct = _safe_get_numeric(assumptions, 'r_and_d_increase', 0.0)
        proj_rnd = base_rnd_spend * (1 + rnd_increase_pct / 100.0)
        projections['projected_r_and_d_spend'] = proj_rnd
        projections['rnd_cagr'] = _calculate_cagr(base_rnd_spend, proj_rnd, years)
        logger.debug(f"  {timeframe} R&D Spend -> {proj_rnd:.1f}M (CAGR: {projections['rnd_cagr']})")


        # --- 4. Net Income Projection ---
        # Simple Assumption: Net Margin improves by *half* the percentage points of EBITDA margin improvement.
        # Example: If EBITDA margin improves by 2.0 p.p., assume Net Margin improves by 1.0 p.p.
        # This is a simplistic approach; real-world requires projecting taxes, interest etc.
        net_margin_improvement_pp = ebitda_margin_improvement_pp / 2.0 # Assumption!
        # Ensure projected margin stays within reasonable bounds (e.g., 0% to 100%)
        proj_net_margin = max(0.0, min(1.0, base_net_margin + (net_margin_improvement_pp / 100.0)))
        proj_net_income = proj_rev * proj_net_margin
        projections['projected_net_income'] = proj_net_income
        projections['projected_net_margin'] = proj_net_margin # Store projected margin
        projections['net_income_cagr'] = _calculate_cagr(base_net_income, proj_net_income, years)
        logger.debug(f"  {timeframe} Net Income -> {proj_net_income:.1f}M (Margin: {proj_net_margin*100:.1f}%, CAGR: {projections['net_income_cagr']})")
        logger.debug(f"  (Net Income projection based on assumed margin improvement: {net_margin_improvement_pp:.2f} p.p.)")


        # --- Store Results ---
        results[timeframe] = projections

    logger.debug("Projection calculations finished.")
    return results