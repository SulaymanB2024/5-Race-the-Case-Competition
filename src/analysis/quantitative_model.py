"""
Quantitative analysis model for financial metrics and market performance.
"""

from typing import Dict, List, Union, Optional
import numpy as np
from ..core.baseline import get_baseline_data, validate_baseline_data

class FinancialMetrics:
    """Handles calculation and analysis of financial metrics."""
    
    def __init__(self, data: Dict[str, Union[float, int]]):
        """
        Initialize with financial data.
        
        Args:
            data: Dictionary containing financial metrics
        
        Raises:
            ValueError: If data validation fails
        """
        if not validate_baseline_data(data):
            raise ValueError("Invalid financial data format")
        self.data = data
        
    def calculate_roi(self) -> float:
        """
        Calculate Return on Investment.
        
        Returns:
            float: ROI as a percentage
        """
        try:
            net_income = self.data.get('net_income', 0)
            total_investment = self.data.get('total_investment', 1)  # Default to 1 to avoid division by zero
            return (net_income / total_investment) * 100
        except Exception as e:
            raise ValueError(f"Error calculating ROI: {str(e)}")
    
    def calculate_market_growth(self, years: int = 5) -> float:
        """
        Calculate projected market growth.
        
        Args:
            years: Number of years for projection
            
        Returns:
            float: Projected growth rate as a percentage
        """
        try:
            current_share = self.data['market_share']
            growth_rate = self.data.get('growth_rate', 0.05)  # Default 5% if not specified
            return current_share * (1 + growth_rate) ** years
        except Exception as e:
            raise ValueError(f"Error calculating market growth: {str(e)}")
    
    def get_performance_indicators(self) -> Dict[str, float]:
        """
        Generate key performance indicators.
        
        Returns:
            Dict[str, float]: Dictionary of KPIs
        """
        return {
            'roi': self.calculate_roi(),
            'market_growth': self.calculate_market_growth(),
            'operating_margin': self.data.get('operating_margin', 0),
            'revenue_growth': self.data.get('revenue_growth', 0)
        }

def analyze_metrics(baseline_data: Optional[Dict[str, Union[float, int]]] = None) -> Dict[str, float]:
    """
    Perform comprehensive financial analysis.
    
    Args:
        baseline_data: Optional dictionary of financial data. If None, uses default baseline data.
    
    Returns:
        Dict[str, float]: Analysis results
    """
    if baseline_data is None:
        baseline_data = get_baseline_data()
    
    metrics = FinancialMetrics(baseline_data)
    return metrics.get_performance_indicators()

def calculate_dcf_valuation(
    initial_revenue: float,
    growth_rates: List[float],
    ebitda_margins: List[float],
    wacc: float = 0.09,
    terminal_growth: float = 0.02,
    tax_rate: float = 0.25
) -> Dict[str, float]:
    """
    Calculate Discounted Cash Flow valuation
    """
    periods = len(growth_rates)
    revenues = [initial_revenue]
    for i in range(periods):
        revenues.append(revenues[-1] * (1 + growth_rates[i]))
    
    ebitda = [rev * margin for rev, margin in zip(revenues, ebitda_margins)]
    nopat = [ebit * (1 - tax_rate) for ebit in ebitda]
    
    # Simplified FCF calculation
    fcf = [pat * 0.8 for pat in nopat]  # Assuming 80% conversion of NOPAT to FCF
    
    # Terminal value calculation
    terminal_value = fcf[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    
    # Discount factors
    discount_factors = [(1 + wacc) ** -(i+1) for i in range(periods)]
    
    # PV of FCFs
    pv_fcf = sum(cf * df for cf, df in zip(fcf, discount_factors))
    pv_terminal = terminal_value * discount_factors[-1]
    
    enterprise_value = pv_fcf + pv_terminal
    
    return {
        'enterprise_value': enterprise_value,
        'present_value_fcf': pv_fcf,
        'present_value_terminal': pv_terminal,
        'terminal_value': terminal_value,
        'projected_revenues': revenues,
        'projected_ebitda': ebitda,
        'free_cash_flows': fcf
    }

def calculate_market_share_projection(
    initial_share: float,
    market_growth: float,
    company_growth: float,
    periods: int
) -> List[float]:
    """
    Project market share evolution
    """
    market_size = [1.0]  # Normalized to 1
    company_size = [initial_share]
    
    for _ in range(periods):
        market_size.append(market_size[-1] * (1 + market_growth))
        company_size.append(company_size[-1] * (1 + company_growth))
    
    market_shares = [comp / mkt for comp, mkt in zip(company_size, market_size)]
    return market_shares

def calculate_financial_ratios(
    financials: Dict[str, float],
    historical: Dict[str, float]
) -> Dict[str, Dict[str, float]]:
    """Calculate detailed financial ratios and their trends"""
    ratios = {
        'profitability': {
            'gross_margin': financials['gross_profit'] / financials['revenue'],
            'operating_margin': financials['operating_income'] / financials['revenue'],
            'net_margin': financials['net_income'] / financials['revenue'],
            'roce': financials['operating_income'] / (financials['equity'] + financials['long_term_debt']),
        },
        'efficiency': {
            'asset_turnover': financials['revenue'] / financials['assets'],
            'inventory_turnover': financials['cost_of_sales'] / financials['inventory'],
            'receivables_turnover': financials['revenue'] / financials['receivables'],
        },
        'liquidity': {
            'current_ratio': financials['current_assets'] / financials['current_liabilities'],
            'quick_ratio': (financials['current_assets'] - financials['inventory']) / financials['current_liabilities'],
            'cash_ratio': financials['cash'] / financials['current_liabilities'],
        },
        'solvency': {
            'debt_to_equity': financials['long_term_debt'] / financials['equity'],
            'interest_coverage': financials['operating_income'] / financials['interest_expense'],
            'debt_to_ebitda': financials['long_term_debt'] / financials['ebitda'],
        }
    }
    
    # Calculate year-over-year changes
    changes = {}
    for category, metrics in ratios.items():
        changes[category] = {}
        for metric, value in metrics.items():
            if historical.get(category, {}).get(metric):
                changes[category][metric] = (value / historical[category][metric]) - 1
    
    return {
        'current': ratios,
        'changes': changes
    }

def monte_carlo_simulation(
    base_revenue: float,
    growth_mean: float,
    growth_std: float,
    margin_mean: float,
    margin_std: float,
    num_simulations: int = 1000,
    periods: int = 5
) -> Dict[str, List[float]]:
    """
    Perform Monte Carlo simulation for revenue and profit projections
    """
    np.random.seed(42)  # For reproducibility
    
    # Generate random growth rates and margins
    growth_rates = np.random.normal(growth_mean, growth_std, (num_simulations, periods))
    margins = np.random.normal(margin_mean, margin_std, (num_simulations, periods))
    
    # Initialize arrays for results
    revenues = np.zeros((num_simulations, periods + 1))
    revenues[:, 0] = base_revenue
    
    # Calculate revenue trajectories
    for t in range(periods):
        revenues[:, t+1] = revenues[:, t] * (1 + growth_rates[:, t])
    
    # Calculate profits
    profits = revenues[:, 1:] * margins
    
    # Calculate percentiles for confidence intervals
    revenue_percentiles = {
        'p10': np.percentile(revenues, 10, axis=0),
        'p50': np.percentile(revenues, 50, axis=0),
        'p90': np.percentile(revenues, 90, axis=0)
    }
    
    profit_percentiles = {
        'p10': np.percentile(profits, 10, axis=0),
        'p50': np.percentile(profits, 50, axis=0),
        'p90': np.percentile(profits, 90, axis=0)
    }
    
    return {
        'revenue_scenarios': revenue_percentiles,
        'profit_scenarios': profit_percentiles,
        'simulation_count': num_simulations
    }

def calculate_market_penetration_metrics(
    target_share: float,
    current_share: float,
    time_periods: int,
    marketing_spend: float,
    channel_efficiency: float
) -> Dict[str, List[float]]:
    """
    Calculate market penetration metrics and required marketing spend
    """
    # S-curve penetration model
    k = 0.5  # steepness factor
    midpoint = time_periods / 2
    
    # Calculate penetration curve
    t = np.linspace(0, time_periods, time_periods + 1)
    share_trajectory = current_share + (target_share - current_share) / (1 + np.exp(-k * (t - midpoint)))
    
    # Calculate required marketing spend per period
    share_gains = np.diff(share_trajectory)
    marketing_required = share_gains * marketing_spend / channel_efficiency
    
    # Calculate cumulative metrics
    cumulative_spend = np.cumsum(marketing_required)
    roi_trajectory = share_gains / (marketing_required / 100)  # ROI in percentage points per 100 currency units
    
    return {
        'market_share_trajectory': share_trajectory.tolist(),
        'required_marketing_spend': marketing_required.tolist(),
        'cumulative_spend': cumulative_spend.tolist(),
        'marketing_roi': roi_trajectory.tolist()
    }

def project_digital_transformation_impact(
    base_metrics: Dict[str, float],
    adoption_rate: float,
    efficiency_gain: float,
    investment_required: float,
    periods: int
) -> Dict[str, List[float]]:
    """
    Project the impact of digital transformation initiatives
    """
    # Initialize metrics
    revenue_impact = []
    cost_savings = []
    customer_satisfaction = []
    roi = []
    
    cumulative_adoption = 0
    cumulative_investment = 0
    
    for t in range(periods):
        # Calculate adoption using S-curve
        period_adoption = adoption_rate * (1 - cumulative_adoption)
        cumulative_adoption += period_adoption
        
        # Calculate period metrics
        revenue_lift = base_metrics['revenue'] * period_adoption * efficiency_gain
        cost_reduction = base_metrics['costs'] * period_adoption * efficiency_gain
        satisfaction_improvement = min(100, base_metrics['satisfaction'] * (1 + period_adoption * 0.2))
        
        # Calculate investment and ROI
        period_investment = investment_required * (1 - t/periods)  # Decreasing investment over time
        cumulative_investment += period_investment
        period_roi = (revenue_lift + cost_reduction) / period_investment if period_investment > 0 else 0
        
        # Append results
        revenue_impact.append(revenue_lift)
        cost_savings.append(cost_reduction)
        customer_satisfaction.append(satisfaction_improvement)
        roi.append(period_roi)
    
    return {
        'revenue_impact': revenue_impact,
        'cost_savings': cost_savings,
        'customer_satisfaction': customer_satisfaction,
        'roi': roi,
        'cumulative_adoption': cumulative_adoption,
        'total_investment': cumulative_investment
    }