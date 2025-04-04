"""
Configuration and assumptions for BFC 10-K Reports.
"""

# Baseline financial data from the 2018 10-K
BASELINE_DATA = {
    'assets': 7265,      # in millions USD
    'liabilities': 3794, # in millions USD
    'equity': 3471,      # in millions USD
    'net_sales': 4000,   # assumed baseline net sales in millions USD
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
    },
    'five_year': {
        'cumulative_revenue_growth_pct': 20,  # cumulative growth over 5 years
        'asset_growth_pct': 15,
        'liability_growth_pct': 10,
        'equity_growth_pct': 25,
    },
    'ten_year': {
        'cumulative_revenue_growth_pct': 40,  # cumulative growth over 10 years
        'asset_growth_pct': 30,
        'liability_growth_pct': 20,
        'equity_growth_pct': 50,
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
