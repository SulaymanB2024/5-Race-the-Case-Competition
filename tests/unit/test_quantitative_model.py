"""Tests for quantitative analysis model."""

import pytest
from src.analysis.quantitative_model import (
    FinancialMetrics,
    calculate_dcf_valuation,
    calculate_market_share_projection,
    calculate_financial_ratios,
    monte_carlo_simulation
)
from src.core.config import BASELINE_DATA

@pytest.fixture
def sample_financial_data():
    """Fixture providing sample financial data for tests."""
    return {
        'net_income': 1000000,
        'total_investment': 5000000,
        'market_share': 0.07,
        'operating_margin': 0.15,
        'revenue': 10000000,
        'assets': 8000000,
        'liabilities': 4000000,
        'current_assets': 3000000,
        'current_liabilities': 2000000,
        'inventory': 1000000,
        'cost_of_sales': 6000000
    }

class TestFinancialMetrics:
    """Test suite for FinancialMetrics class."""
    
    def test_roi_calculation(self, sample_financial_data):
        """Test ROI calculation."""
        metrics = FinancialMetrics(sample_financial_data)
        assert metrics.calculate_roi() == 20.0
    
    def test_market_growth_projection(self, sample_financial_data):
        """Test market growth projection."""
        metrics = FinancialMetrics(sample_financial_data)
        projected_share = metrics.calculate_market_growth(years=5)
        assert 0.089 <= projected_share <= 0.09
    
    @pytest.mark.parametrize("invalid_data,expected_error", [
        ({'market_share': -0.1}, ValueError),
        ({'operating_margin': 1.5}, ValueError),
        ({'revenue': 'invalid'}, TypeError),
        ({'market_share': None}, TypeError)
    ])
    def test_invalid_data_handling(self, invalid_data, expected_error):
        """Test handling of invalid financial data."""
        with pytest.raises(expected_error):
            FinancialMetrics(invalid_data)
    
    def test_financial_ratios(self, sample_financial_data):
        """Test calculation of financial ratios."""
        metrics = FinancialMetrics(sample_financial_data)
        ratios = metrics.calculate_ratios()
        
        assert isinstance(ratios, dict)
        assert 'current_ratio' in ratios
        assert ratios['current_ratio'] == pytest.approx(1.5)
        assert ratios['debt_to_equity'] == pytest.approx(1.0)
        assert ratios['inventory_turnover'] == pytest.approx(6.0)

class TestValuationMethods:
    """Test suite for valuation methods."""
    
    def test_dcf_valuation(self):
        """Test DCF valuation calculation."""
        initial_revenue = 1000000
        growth_rates = [0.05, 0.06, 0.05, 0.04, 0.04]
        ebitda_margins = [0.15, 0.16, 0.16, 0.17, 0.17]
        
        result = calculate_dcf_valuation(
            initial_revenue=initial_revenue,
            growth_rates=growth_rates,
            ebitda_margins=ebitda_margins
        )
        
        assert isinstance(result, dict)
        assert all(key in result for key in ['enterprise_value', 'present_value_fcf'])
        assert result['enterprise_value'] > result['present_value_fcf']
    
    def test_market_share_projection(self):
        """Test market share projection calculation."""
        result = calculate_market_share_projection(
            initial_share=0.07,
            market_growth=0.03,
            company_growth=0.05,
            periods=5
        )
        
        assert isinstance(result, list)
        assert len(result) == 5
        assert all(0 < share < 1 for share in result)
        assert result[-1] > result[0]  # Final share should be higher
    
    @pytest.mark.parametrize("test_input,expected", [
        ((0.07, 0.03, 0.05, 5), 5),  # Normal case
        ((0.07, 0.0, 0.05, 3), 3),   # No market growth
        ((0.07, 0.03, 0.0, 4), 4),   # No company growth
    ])
    def test_market_share_projection_variations(self, test_input, expected):
        """Test market share projection with different inputs."""
        result = calculate_market_share_projection(*test_input)
        assert len(result) == expected

class TestMonteCarloSimulation:
    """Test suite for Monte Carlo simulation."""
    
    def test_monte_carlo_basic(self):
        """Test basic Monte Carlo simulation functionality."""
        result = monte_carlo_simulation(
            base_revenue=1000000,
            growth_mean=0.05,
            growth_std=0.02,
            margin_mean=0.15,
            margin_std=0.03,
            num_sims=100
        )
        
        assert isinstance(result, dict)
        assert all(key in result for key in ['mean_npv', 'percentiles'])
        assert result['mean_npv'] > 0
        assert len(result['percentiles']) == 3  # 10th, 50th, 90th percentiles
    
    def test_monte_carlo_with_baseline_data(self):
        """Test Monte Carlo simulation with baseline data."""
        result = monte_carlo_simulation(
            base_revenue=BASELINE_DATA['revenue'],
            growth_mean=0.05,
            growth_std=0.02,
            margin_mean=BASELINE_DATA['operating_margin'],
            margin_std=0.03,
            num_sims=100
        )
        
        assert isinstance(result, dict)
        assert result['percentiles'][1] > result['percentiles'][0]  # Median > 10th percentile
        assert result['percentiles'][2] > result['percentiles'][1]  # 90th > Median
    
    @pytest.mark.parametrize("invalid_input", [
        {'base_revenue': -1000},
        {'growth_mean': 1.5},
        {'margin_mean': -0.5},
        {'num_sims': 0}
    ])
    def test_monte_carlo_invalid_inputs(self, invalid_input):
        """Test Monte Carlo simulation with invalid inputs."""
        base_params = {
            'base_revenue': 1000000,
            'growth_mean': 0.05,
            'growth_std': 0.02,
            'margin_mean': 0.15,
            'margin_std': 0.03,
            'num_sims': 100
        }
        params = {**base_params, **invalid_input}
        
        with pytest.raises((ValueError, TypeError)):
            monte_carlo_simulation(**params)