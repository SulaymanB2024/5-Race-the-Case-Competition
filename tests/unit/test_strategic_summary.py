"""Tests for strategic analysis functionality."""

import pytest
from strategic_summary import (
    analyze_competitive_position,
    generate_strategic_recommendations,
    StrategicInitiative,
    MarketOpportunity,
    calculate_strategic_fit
)

def test_competitive_analysis():
    """Test competitive position analysis."""
    metrics = {
        'market_share': 0.07,
        'growth_rate': 0.05,
        'operating_margin': 0.15,
        'innovation_score': 8.0
    }
    
    competitors = {
        'competitor1': {
            'market_share': 0.10,
            'growth_rate': 0.04,
            'operating_margin': 0.14,
            'innovation_score': 7.5
        },
        'competitor2': {
            'market_share': 0.05,
            'growth_rate': 0.06,
            'operating_margin': 0.13,
            'innovation_score': 8.5
        }
    }
    
    result = analyze_competitive_position(metrics, competitors)
    
    assert 'strengths' in result
    assert 'weaknesses' in result
    assert 'market_position' in result
    assert len(result['strengths']) > 0

def test_strategic_recommendations():
    """Test strategic recommendations generation."""
    market_data = {
        'market_share': 0.07,
        'growth_rate': 0.05,
        'market_size': 52000000000
    }
    
    financial_data = {
        'operating_margin': 0.15,
        'net_margin': 0.10,
        'roi': 0.20,
        'current_ratio': 2.1,
        'quick_ratio': 1.4,
        'asset_turnover': 0.55,
        'inventory_turnover': 4.8
    }
    
    result = generate_strategic_recommendations(market_data, financial_data)
    
    assert 'market_position' in result
    assert 'financial_health' in result
    assert 'strategic_initiatives' in result
    assert 'opportunities' in result
    assert len(result['strategic_initiatives']) > 0

def test_strategic_initiative():
    """Test StrategicInitiative dataclass."""
    initiative = StrategicInitiative(
        name="Market Expansion Program",
        impact=8.5,
        timeline="12-18 months",
        priority=1,
        resources=25.0,
        roi=0.35
    )
    
    assert initiative.name == "Market Expansion Program"
    assert initiative.impact == 8.5
    assert initiative.priority == 1
    assert initiative.roi == 0.35

def test_market_opportunity():
    """Test MarketOpportunity dataclass."""
    opportunity = MarketOpportunity(
        market="UK",
        potential_size=500000000,
        growth_rate=0.08,
        entry_barriers=['Regulation', 'Competition'],
        competitive_intensity=7.5,
        time_to_market=12
    )
    
    assert opportunity.market == "UK"
    assert opportunity.potential_size == 500000000
    assert opportunity.growth_rate == 0.08
    assert len(opportunity.entry_barriers) == 2

def test_strategic_fit():
    """Test strategic fit calculation."""
    initiative = StrategicInitiative(
        name="Digital Experience Enhancement",
        impact=9.0,
        timeline="6-12 months",
        priority=1,
        resources=15.0,
        roi=0.40
    )
    
    capabilities = {
        'technical_capability': 0.8,
        'innovation_capacity': 0.7,
        'change_management': 0.6,
        'customer_insight': 0.9
    }
    
    fit_score = calculate_strategic_fit(initiative, capabilities)
    assert 0 <= fit_score <= 10
    assert fit_score > 7.0  # High fit expected given the capabilities

def test_invalid_initiative():
    """Test handling of invalid initiative name."""
    initiative = StrategicInitiative(
        name="Invalid Initiative",
        impact=5.0,
        timeline="3-6 months",
        priority=3,
        resources=5.0,
        roi=0.15
    )
    
    capabilities = {
        'technical_capability': 0.8,
        'innovation_capacity': 0.7
    }
    
    # Should return default medium fit score for unknown initiative
    fit_score = calculate_strategic_fit(initiative, capabilities)
    assert fit_score == 5.0