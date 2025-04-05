"""
Configuration and assumptions for BFC 10-K Reports.
"""

def get_config():
    """Returns the current configuration settings."""
    return {
        'log_level': 'INFO',
        'baseline_data': BASELINE_DATA,
        'growth_assumptions': GROWTH_ASSUMPTIONS,
        'market_parameters': {
            'market_size': MARKET_SIZE,
            'market_share': MARKET_SHARE
        }
    }

# Baseline financial data from the 2018 10-K
BASELINE_DATA = {
    'assets': 7265,      # in millions USD
    'liabilities': 3794, # in millions USD
    'equity': 3471,      # in millions USD
    'revenue': 4000,     # baseline net sales in millions USD
    'ebitda': 800,      # assumed EBITDA in millions USD
    'ebitda_margin': 0.20,  # EBITDA/Revenue
    'net_income': 400,   # assumed net income in millions USD
    'r_and_d_spend': 200,  # assumed R&D spend in millions USD
}

# Market parameters and growth assumptions
MARKET_SIZE = 52_000  # in millions USD
MARKET_SHARE = 7      # percent

# Strategic growth assumptions
GROWTH_ASSUMPTIONS = {
    'one_year': {
        'revenue_growth_pct': 5,       # modest growth due to initial international and digital adoption
        'asset_growth_pct': 3,
        'liability_growth_pct': 2,
        'equity_growth_pct': 6,
        'ebitda_margin_improvement': 0.5,  # percentage points improvement
        'r_and_d_increase': 10.0          # percentage increase
    },
    'five_year': {
        'cumulative_revenue_growth_pct': 20,  # cumulative growth over 5 years
        'asset_growth_pct': 15,
        'liability_growth_pct': 10,
        'equity_growth_pct': 25,
        'ebitda_margin_improvement': 2.0,    # percentage points improvement
        'r_and_d_increase': 50.0            # percentage increase
    },
    'ten_year': {
        'cumulative_revenue_growth_pct': 40,  # cumulative growth over 10 years
        'asset_growth_pct': 30,
        'liability_growth_pct': 20,
        'equity_growth_pct': 50,
        'ebitda_margin_improvement': 4.0,    # percentage points improvement
        'r_and_d_increase': 100.0           # percentage increase
    }
}

# CAGR ranges for new markets (from case study)
MARKET_CAGR = {
    'UK': (3.2, 8.0),      # in percent per year
    'Germany': (1.3, 4.0)   # in percent per year
}

# Digital transformation assumptions
DIGITAL_IMPACT = {
    'magic_mirror_launch': True,
    'early_adoption_rate': 0.1,  # 10% adoption in early stage
}

# Risk sensitivity assumptions (sensitivity analysis margins in percent)
SENSITIVITY = {
    'consumer_confidence_change': 1,   # 1% change could affect net sales
    'international_growth_variation': 2,  # 2-3% swing in international growth may affect margins
}
