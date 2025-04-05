"""
Configuration settings for the financial analysis application.

This module provides configuration settings and constants used throughout
the application, with support for environment variables and config validation.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    """Application configuration settings."""
    
    output_dir: str = './outputs'
    log_level: str = 'INFO'
    date_format: str = '%Y-%m-%d'
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        return cls(
            output_dir=os.getenv('OUTPUT_DIR', './outputs'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            date_format=os.getenv('DATE_FORMAT', '%Y-%m-%d')
        )

# Application constants
APP_NAME = "BFC Financial Analysis"
VERSION = "1.0.0"

# Financial constants from 2018 10-K
BASELINE_DATA: Dict[str, Any] = {
    # Income Statement Metrics (in millions USD)
    'revenue': 13685.2,           # Net sales
    'cost_of_sales': 5232.7,      # Cost of goods sold
    'gross_profit': 8452.5,       # Gross profit
    'operating_expenses': 7145.2,  # Operating expenses
    'operating_income': 1307.3,   # Operating income
    'interest_expense': 133.8,     # Interest expense
    'income_before_tax': 1173.5,  # Income before taxes
    'net_income': 901.4,          # Net income
    
    # Balance Sheet Metrics (in millions USD)
    'assets': 12994.8,            # Total assets
    'current_assets': 5093.6,     # Current assets
    'cash': 2181.2,               # Cash and cash equivalents
    'inventory': 1618.3,          # Inventory
    'receivables': 1487.8,        # Accounts receivable
    'ppe_net': 1637.6,            # Property, plant and equipment, net
    'goodwill': 3382.5,           # Goodwill
    'intangibles': 1342.6,        # Other intangible assets, net
    
    'liabilities': 7951.3,        # Total liabilities
    'current_liabilities': 2494.1, # Current liabilities
    'long_term_debt': 3361.6,     # Long-term debt
    'equity': 5043.5,             # Total stockholders' equity
    
    # Key Financial Ratios
    'operating_margin': 0.0956,    # Operating margin (9.56%)
    'net_margin': 0.0659,         # Net margin (6.59%)
    'current_ratio': 2.042,       # Current ratio
    'debt_to_equity': 0.667,      # Debt to equity ratio
    'asset_turnover': 1.053,      # Asset turnover ratio
    'inventory_turnover': 3.234,   # Inventory turnover ratio
    'roce': 0.1606,              # Return on Capital Employed
    
    # Market and Growth Metrics
    'market_share': 0.089,        # 8.9% global market share
    'market_cap': 15723.6,        # Market capitalization
    'ebitda': 1725.4,            # EBITDA
    'ebitda_margin': 0.1261,     # EBITDA margin (12.61%)
    
    # Operational Metrics
    'r_and_d_spend': 512.3,      # Research and development
    'marketing_spend': 2054.7,    # Marketing and advertising
    'capex': 468.2,              # Capital expenditures
    'employees': 48000,           # Number of employees
    
    # Segment Revenue (in millions USD)
    'segment_revenue': {
        'skincare': 5635.4,      # Skincare segment
        'makeup': 4674.7,        # Makeup segment
        'fragrance': 1826.8,     # Fragrance segment
        'haircare': 1548.3,      # Hair Care segment
    },
    
    # Geographic Revenue (in millions USD)
    'geographic_revenue': {
        'americas': 4101.1,      # The Americas
        'emea': 5637.5,         # Europe, Middle East & Africa
        'asia_pacific': 3946.6,  # Asia/Pacific
    },
    
    # Distribution Channels (in millions USD)
    'channel_revenue': {
        'department_stores': 4579.5,  # Department stores
        'freestanding_stores': 3196.7, # Freestanding stores
        'travel_retail': 2724.4,      # Travel retail
        'online': 1184.6,             # Online/ecommerce
    }
}

# Market parameters and growth assumptions
MARKET_SIZE = 52_000  # in millions USD
MARKET_SHARE = 7      # percent

# Strategic growth assumptions based on historical performance
GROWTH_ASSUMPTIONS = {
    'one_year': {
        'revenue_growth_pct': 7.2,         # Based on historical CAGR
        'asset_growth_pct': 5.8,           # Based on asset growth trend
        'liability_growth_pct': 4.5,       # Conservative debt management
        'equity_growth_pct': 7.0,          # Balanced capital structure
        'ebitda_margin_improvement': 0.75,  # Target margin expansion
        'r_and_d_increase': 12,            # Innovation investment
        'marketing_efficiency': 3,          # Digital optimization
    },
    'five_year': {
        'cumulative_revenue_growth_pct': 32.5,  # Compound growth target
        'asset_growth_pct': 25.4,
        'liability_growth_pct': 18.7,
        'equity_growth_pct': 31.2,
        'ebitda_margin_improvement': 2.5,
        'r_and_d_increase': 45,
        'marketing_efficiency': 12,
    },
    'ten_year': {
        'cumulative_revenue_growth_pct': 65.0,
        'asset_growth_pct': 48.6,
        'liability_growth_pct': 35.8,
        'equity_growth_pct': 62.5,
        'ebitda_margin_improvement': 4.5,
        'r_and_d_increase': 85,
        'marketing_efficiency': 20,
    }
}

# CAGR ranges for new markets
MARKET_CAGR = {
    'UK': (3.2, 8.0),      # in percent per year
    'Germany': (1.3, 4.0),  # in percent per year
    'France': (2.1, 5.5),   # potential future market
    'Italy': (1.8, 4.8),    # potential future market
    'China': (5.0, 12.0),   # potential future market
    'Japan': (1.5, 4.2),    # potential future market
}

# Digital transformation assumptions
DIGITAL_IMPACT = {
    'magic_mirror_launch': True,
    'early_adoption_rate': 0.1,  # 10% adoption in early stage
    'mature_adoption_rate': 0.4, # 40% adoption in mature stage
    'customer_retention_improvement': 0.15, # 15% improvement in retention
    'conversion_rate_improvement': 0.25, # 25% improvement in conversion
}

# Risk sensitivity assumptions
SENSITIVITY = {
    'consumer_confidence_change': 1,
    'international_growth_variation': 2,
    'raw_material_cost_variation': 3,
    'forex_impact': 2.5,
    'regulatory_cost_impact': 1.5,
}

# Sustainability metrics
SUSTAINABILITY_TARGETS = {
    'one_year': {
        'carbon_reduction': 5,    # percent reduction
        'renewable_energy': 25,   # percent of total energy
        'recycled_packaging': 30, # percent of packaging
        'water_reduction': 3,     # percent reduction
    },
    'five_year': {
        'carbon_reduction': 25,
        'renewable_energy': 60,
        'recycled_packaging': 75,
        'water_reduction': 20,
    },
    'ten_year': {
        'carbon_reduction': 50,
        'renewable_energy': 100,
        'recycled_packaging': 100,
        'water_reduction': 40,
    }
}

# Competitive analysis
COMPETITIVE_LANDSCAPE = {
    'skincare': {
        'market_share': 41.2,    # percent of segment revenue
        'growth_rate': 8.5,      # percent per year
        'r_and_d_intensity': 5.8  # percent of segment revenue
    },
    'makeup': {
        'market_share': 34.2,
        'growth_rate': 6.2,
        'r_and_d_intensity': 4.5
    },
    'fragrance': {
        'market_share': 13.3,
        'growth_rate': 5.8,
        'r_and_d_intensity': 3.8
    },
    'haircare': {
        'market_share': 11.3,
        'growth_rate': 4.5,
        'r_and_d_intensity': 3.5
    }
}

# Industry-specific KPIs
INDUSTRY_KPIS = {
    'new_product_success_rate': 0.35,  # 35% of new products succeed
    'product_development_cycle': 12,    # months
    'customer_acquisition_cost': 45,    # USD per customer
    'lifetime_value': 320,              # USD per customer
    'retail_partnership_coverage': 0.7,  # 70% of target retail channels
    'social_media_engagement': 0.08,    # 8% engagement rate
}

# Market penetration targets by region (based on 2018 geographic revenue)
MARKET_PENETRATION = {
    'one_year': {
        'americas': {'target_share': 10.2, 'brand_awareness': 85, 'distribution_coverage': 82},
        'emea': {'target_share': 11.5, 'brand_awareness': 80, 'distribution_coverage': 75},
        'asia_pacific': {'target_share': 9.8, 'brand_awareness': 75, 'distribution_coverage': 70}
    },
    'five_year': {
        'americas': {'target_share': 12.5, 'brand_awareness': 90, 'distribution_coverage': 88},
        'emea': {'target_share': 14.0, 'brand_awareness': 85, 'distribution_coverage': 82},
        'asia_pacific': {'target_share': 13.5, 'brand_awareness': 82, 'distribution_coverage': 80},
        'emerging_markets': {'target_share': 5.0, 'brand_awareness': 60, 'distribution_coverage': 55}
    },
    'ten_year': {
        'americas': {'target_share': 15.0, 'brand_awareness': 95, 'distribution_coverage': 92},
        'emea': {'target_share': 16.5, 'brand_awareness': 90, 'distribution_coverage': 88},
        'asia_pacific': {'target_share': 18.0, 'brand_awareness': 88, 'distribution_coverage': 85},
        'emerging_markets': {'target_share': 8.5, 'brand_awareness': 75, 'distribution_coverage': 70}
    }
}

# Digital transformation metrics (based on 2018 channel revenue)
DIGITAL_METRICS = {
    'one_year': {
        'e_commerce_share': 12.5,      # Starting from 8.7% (1184.6M/13685.2M)
        'mobile_traffic': 65,          # Mobile-first strategy
        'ar_adoption': 15,            # AR beauty tech adoption
        'digital_engagement': 35,      # Active digital platform users
        'personalization_rate': 30,    # Personalized experiences
        'omnichannel_integration': 40  # Cross-channel integration
    },
    'five_year': {
        'e_commerce_share': 25.0,
        'mobile_traffic': 78,
        'ar_adoption': 45,
        'digital_engagement': 60,
        'personalization_rate': 70,
        'omnichannel_integration': 75
    },
    'ten_year': {
        'e_commerce_share': 40.0,
        'mobile_traffic': 85,
        'ar_adoption': 75,
        'digital_engagement': 80,
        'personalization_rate': 90,
        'omnichannel_integration': 95
    }
}

# Competitive positioning matrix based on 2018 segment performance
COMPETITIVE_MATRIX = {
    'product_innovation': {
        'bfc': 8.5,        # Based on R&D intensity and new product launches
        'leaders': 8.8,
        'challengers': 7.5,
        'emerging': 6.8
    },
    'brand_strength': {
        'bfc': 8.2,        # Based on market share and brand equity
        'leaders': 9.0,
        'challengers': 7.0,
        'emerging': 5.5
    },
    'digital_capabilities': {
        'bfc': 7.8,        # Based on e-commerce and digital engagement
        'leaders': 8.5,
        'challengers': 7.2,
        'emerging': 8.0
    },
    'operational_efficiency': {
        'bfc': 8.0,        # Based on margins and asset turnover
        'leaders': 8.5,
        'challengers': 7.0,
        'emerging': 6.5
    },
    'market_responsiveness': {
        'bfc': 8.2,        # Based on growth rate and market expansion
        'leaders': 7.8,
        'challengers': 7.5,
        'emerging': 8.5
    }
}

# Analysis parameters
ANALYSIS_PARAMS = {
    'projection_years': 5,
    'confidence_interval': 0.95,
    'monte_carlo_sims': 1000,
}

# Visualization settings
PLOT_SETTINGS = {
    'style': 'seaborn',
    'figsize': (12, 8),
    'dpi': 300,
    'save_format': 'png'
}

def validate_config() -> bool:
    """
    Validate configuration settings.
    
    Returns:
        bool: True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate output directory
    output_path = Path(Config.from_env().output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True)
    
    # Validate baseline data
    required_metrics = {'revenue', 'operating_margin', 'market_share'}
    if not all(metric in BASELINE_DATA for metric in required_metrics):
        raise ValueError(f"Missing required metrics in BASELINE_DATA: {required_metrics}")
    
    # Validate numeric values for top-level metrics only
    for key, value in BASELINE_DATA.items():
        if not isinstance(value, (int, float, dict)):
            raise ValueError(f"Invalid value type for {key}: expected number or dictionary, got {type(value)}")
    
    return True

def get_config() -> Config:
    """
    Get validated configuration instance.
    
    Returns:
        Config: Application configuration
        
    Raises:
        ValueError: If configuration is invalid
    """
    validate_config()
    return Config.from_env()

# Analysis scenarios
SCENARIOS = {
    'base_case': {
        'growth_rate': 0.05,
        'margin_improvement': 0.00,
        'market_share_gain': 0.00
    },
    'optimistic': {
        'growth_rate': 0.08,
        'margin_improvement': 0.02,
        'market_share_gain': 0.02
    },
    'pessimistic': {
        'growth_rate': 0.02,
        'margin_improvement': -0.01,
        'market_share_gain': -0.01
    }
}

# Risk factors based on 2018 10-K disclosures
RISK_FACTORS = {
    'market_volatility': {
        'impact': 0.15,           # Standard deviation of market returns
        'probability': 0.65,      # Likelihood of significant volatility
        'mitigation_strength': 0.7  # Effectiveness of hedging strategies
    },
    'competitor_pressure': {
        'impact': 0.20,           # Potential market share impact
        'probability': 0.80,      # Likelihood of increased competition
        'mitigation_strength': 0.75  # Brand strength and innovation pipeline
    },
    'supply_chain': {
        'impact': 0.25,           # Revenue impact of disruption
        'probability': 0.40,      # Likelihood of major disruption
        'mitigation_strength': 0.80  # Supplier diversification
    },
    'regulatory_changes': {
        'impact': 0.18,           # Compliance cost impact
        'probability': 0.55,      # Likelihood of significant changes
        'mitigation_strength': 0.85  # Regulatory preparation level
    },
    'forex_exposure': {
        'impact': 0.12,           # Revenue impact of currency fluctuations
        'probability': 0.70,      # Likelihood of adverse movements
        'mitigation_strength': 0.82  # Hedging effectiveness
    },
    'digital_disruption': {
        'impact': 0.30,           # Potential market impact
        'probability': 0.75,      # Likelihood of digital shifts
        'mitigation_strength': 0.78  # Digital transformation readiness
    }
}
