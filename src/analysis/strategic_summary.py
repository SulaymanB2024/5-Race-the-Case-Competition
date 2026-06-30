"""
Strategic analysis and recommendations module.
"""

from typing import Dict, List, Union, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.core.config import (
    COMPETITIVE_MATRIX,
    COMPETITIVE_LANDSCAPE,
    MARKET_PENETRATION,
    DIGITAL_METRICS,
    SUSTAINABILITY_TARGETS
)

@dataclass
class StrategicInitiative:
    """Represents a strategic initiative with its impact and timeline."""
    name: str
    impact: float  # Expected impact score (0-10)
    timeline: str  # Implementation timeline
    priority: int  # Priority level (1-5)
    resources: float  # Required resources in millions USD
    roi: float  # Expected ROI percentage

@dataclass
class MarketOpportunity:
    """Represents a market opportunity with its potential and risks."""
    market: str
    potential_size: float  # Market size in millions USD
    growth_rate: float  # Annual growth rate
    entry_barriers: List[str]
    competitive_intensity: float  # Score from 0-10
    time_to_market: int  # Months

def analyze_competitive_position(
    metrics: Union[Dict[str, float], List[float]],
    competitors: Dict[str, Dict[str, float]]
) -> Dict[str, Any]:
    """
    Analyze competitive position based on key metrics.
    
    Args:
        metrics: Company metrics (dict or list of market share projections)
        competitors: Competitor metrics
        
    Returns:
        Dict containing competitive analysis results
    """
    # Convert list metrics to dict format for analysis
    if isinstance(metrics, list):
        current_share = metrics[0]
        projected_share = metrics[-1]
        growth_rate = (projected_share / current_share) ** (1/len(metrics)) - 1
        metrics_dict = {
            'market_share': current_share,
            'growth_rate': growth_rate
        }
    else:
        metrics_dict = metrics
    
    strengths = []
    weaknesses = []
    
    # Analyze each metric
    for metric, value in metrics_dict.items():
        competitor_values = [comp.get(metric, 0) for comp in competitors.values()]
        if competitor_values:  # Only analyze if we have competitor data
            avg_value = np.mean(competitor_values)
            
            if value > avg_value * 1.1:  # 10% better than average
                strengths.append((metric, value - avg_value))
            elif value < avg_value * 0.9:  # 10% worse than average
                weaknesses.append((metric, avg_value - value))
    
    return {
        'strengths': sorted(strengths, key=lambda x: x[1], reverse=True),
        'weaknesses': sorted(weaknesses, key=lambda x: x[1], reverse=True),
        'market_position': _calculate_market_position(metrics_dict, competitors),
        'competitive_gaps': _identify_competitive_gaps(metrics_dict, competitors)
    }

def generate_strategic_recommendations(
    market_data: Dict[str, Any],
    financial_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate strategic recommendations based on market and financial data.
    
    Args:
        market_data: Market analysis data
        financial_data: Financial metrics and projections
        
    Returns:
        Dict containing strategic recommendations and initiatives
    """
    # Analyze current position
    market_position = _analyze_market_position(market_data)
    financial_health = _analyze_financial_health(financial_data)
    
    # Generate initiatives
    initiatives = _generate_initiatives(market_position, financial_health)
    
    # Identify opportunities
    opportunities = _identify_opportunities(market_data, financial_data)
    
    # Create implementation roadmap
    roadmap = _create_implementation_roadmap(initiatives)
    
    return {
        'market_position': market_position,
        'financial_health': financial_health,
        'strategic_initiatives': initiatives,
        'opportunities': opportunities,
        'implementation_roadmap': roadmap,
        'risk_assessment': _assess_risks(initiatives, market_data)
    }

def _analyze_market_position(data: Union[Dict[str, Any], List[float]]) -> Dict[str, Any]:
    """Analyze current market position."""
    if isinstance(data, list):
        # Handle market projection list data
        current_share = data[0]  # First element is current share
        projected_share = data[-1]  # Last element is projected share
        growth_rate = (projected_share / current_share) ** (1/len(data)) - 1
        return {
            'market_share': current_share,
            'growth_rate': growth_rate,
            'competitive_position': _calculate_competitive_position({'market_share': current_share, 'growth_rate': growth_rate}),
            'market_trends': _identify_market_trends({'market_share': current_share, 'growth_rate': growth_rate})
        }
    else:
        # Handle dictionary data
        return {
            'market_share': data.get('market_share', 0),
            'growth_rate': data.get('growth_rate', 0),
            'competitive_position': _calculate_competitive_position(data),
            'market_trends': _identify_market_trends(data)
        }

def _analyze_financial_health(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze financial health metrics."""
    return {
        'profitability': {
            'operating_margin': data.get('operating_margin', 0),
            'net_margin': data.get('net_margin', 0),
            'roi': data.get('roi', 0)
        },
        'liquidity': {
            'current_ratio': data.get('current_ratio', 0),
            'quick_ratio': data.get('quick_ratio', 0)
        },
        'efficiency': {
            'asset_turnover': data.get('asset_turnover', 0),
            'inventory_turnover': data.get('inventory_turnover', 0)
        }
    }

def _generate_initiatives(
    market_position: Dict[str, Any],
    financial_health: Dict[str, Any]
) -> List[StrategicInitiative]:
    """Generate strategic initiatives based on analysis."""
    initiatives = []
    
    # Market expansion initiative
    if market_position['growth_rate'] > 0.05:  # 5% growth rate threshold
        initiatives.append(StrategicInitiative(
            name="Market Expansion Program",
            impact=8.5,
            timeline="12-18 months",
            priority=1,
            resources=25.0,  # $25M investment
            roi=0.35  # 35% expected ROI
        ))
    
    # Digital transformation initiative
    if DIGITAL_IMPACT['magic_mirror_launch']:
        initiatives.append(StrategicInitiative(
            name="Digital Experience Enhancement",
            impact=9.0,
            timeline="6-12 months",
            priority=1,
            resources=15.0,
            roi=0.40
        ))
    
    # Operational efficiency initiative
    if financial_health['efficiency']['asset_turnover'] < 0.6:
        initiatives.append(StrategicInitiative(
            name="Operational Excellence Program",
            impact=7.5,
            timeline="12-24 months",
            priority=2,
            resources=10.0,
            roi=0.25
        ))
    
    # Sustainability initiative
    initiatives.append(StrategicInitiative(
        name="Sustainable Beauty Initiative",
        impact=8.0,
        timeline="18-36 months",
        priority=2,
        resources=20.0,
        roi=0.30
    ))
    
    return initiatives

def _identify_opportunities(
    market_data: Union[Dict[str, Any], List[float]],
    financial_data: Dict[str, Any]
) -> List[MarketOpportunity]:
    """Identify market opportunities."""
    opportunities = []
    
    # Get market size from config since it's not in the projection data
    from config import MARKET_SIZE, MARKET_PENETRATION
    
    # Calculate growth rate if market_data is a list of projections
    if isinstance(market_data, list):
        current_share = market_data[0]
        projected_share = market_data[-1]
        growth_rate = (projected_share / current_share) ** (1/len(market_data)) - 1
        market_size = MARKET_SIZE  # Use configured market size
    else:
        current_share = market_data.get('market_share', 0)
        growth_rate = market_data.get('growth_rate', 0)
        market_size = market_data.get('market_size', MARKET_SIZE)
    
    # Analyze each target market
    for market, data in MARKET_PENETRATION['five_year'].items():
        opportunity = MarketOpportunity(
            market=market,
            potential_size=market_size * data['target_share'] / 100,
            growth_rate=growth_rate,
            entry_barriers=['Regulation', 'Local competition', 'Distribution'],
            competitive_intensity=7.5,
            time_to_market=12
        )
        opportunities.append(opportunity)
    
    return opportunities

def _create_implementation_roadmap(
    initiatives: List[StrategicInitiative]
) -> List[Dict[str, Any]]:
    """Create implementation roadmap for initiatives."""
    # Sort initiatives by priority
    sorted_initiatives = sorted(initiatives, key=lambda x: (x.priority, -x.impact))
    
    roadmap = []
    current_quarter = 1
    
    for initiative in sorted_initiatives:
        timeline_months = int(initiative.timeline.split('-')[0])
        quarters = (timeline_months + 2) // 3  # Round up to nearest quarter
        
        roadmap.append({
            'initiative': initiative.name,
            'start_quarter': f"Q{current_quarter}",
            'duration_quarters': quarters,
            'key_milestones': _generate_milestones(initiative),
            'resources': initiative.resources,
            'expected_roi': initiative.roi
        })
        
        current_quarter += quarters
    
    return roadmap

def _generate_milestones(initiative: StrategicInitiative) -> List[Dict[str, Any]]:
    """Generate milestones for an initiative."""
    if initiative.name == "Market Expansion Program":
        return [
            {'phase': 'Market Analysis', 'timeline': 'Month 1-2'},
            {'phase': 'Partner Selection', 'timeline': 'Month 3-4'},
            {'phase': 'Infrastructure Setup', 'timeline': 'Month 5-8'},
            {'phase': 'Launch Preparation', 'timeline': 'Month 9-11'},
            {'phase': 'Market Entry', 'timeline': 'Month 12'}
        ]
    elif initiative.name == "Digital Experience Enhancement":
        return [
            {'phase': 'Technology Assessment', 'timeline': 'Month 1'},
            {'phase': 'Platform Development', 'timeline': 'Month 2-4'},
            {'phase': 'Beta Testing', 'timeline': 'Month 5'},
            {'phase': 'Full Deployment', 'timeline': 'Month 6'}
        ]
    else:
        return [
            {'phase': 'Planning', 'timeline': 'Month 1-2'},
            {'phase': 'Implementation', 'timeline': 'Month 3-8'},
            {'phase': 'Evaluation', 'timeline': 'Month 9-10'},
            {'phase': 'Optimization', 'timeline': 'Month 11-12'}
        ]

def _assess_risks(
    initiatives: List[StrategicInitiative],
    market_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Assess risks associated with strategic initiatives."""
    risk_assessment = {
        'market_risks': [
            {
                'type': 'Competition',
                'probability': 0.7,
                'impact': 8,
                'mitigation': 'Differentiation strategy and unique value proposition'
            },
            {
                'type': 'Market Volatility',
                'probability': 0.5,
                'impact': 6,
                'mitigation': 'Diversified market approach and agile response capability'
            }
        ],
        'operational_risks': [
            {
                'type': 'Supply Chain',
                'probability': 0.4,
                'impact': 7,
                'mitigation': 'Multiple supplier relationships and inventory optimization'
            },
            {
                'type': 'Technology',
                'probability': 0.3,
                'impact': 5,
                'mitigation': 'Phased implementation and extensive testing'
            }
        ],
        'financial_risks': [
            {
                'type': 'Currency',
                'probability': 0.6,
                'impact': 4,
                'mitigation': 'Hedging strategy and local pricing adjustments'
            },
            {
                'type': 'Investment',
                'probability': 0.4,
                'impact': 6,
                'mitigation': 'Staged investment approach with clear milestones'
            }
        ]
    }
    
    # Calculate risk scores
    for category in risk_assessment.values():
        for risk in category:
            risk['score'] = risk['probability'] * risk['impact']
    
    return risk_assessment

def _calculate_competitive_position(data: Dict[str, Any]) -> str:
    """Calculate competitive position based on market data."""
    market_share = data.get('market_share', 0)
    growth_rate = data.get('growth_rate', 0)
    
    if market_share >= 0.15:  # 15% market share
        return 'Market Leader'
    elif market_share >= 0.05 and growth_rate > 0.1:  # 5% share and 10% growth
        return 'Fast Growing Challenger'
    elif market_share >= 0.05:
        return 'Established Player'
    else:
        return 'Market Challenger'

def _identify_market_trends(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify key market trends."""
    return [
        {
            'trend': 'Sustainability',
            'impact': 'High',
            'timeframe': '1-3 years',
            'opportunity_score': 8.5
        },
        {
            'trend': 'Digital Beauty',
            'impact': 'High',
            'timeframe': '0-2 years',
            'opportunity_score': 9.0
        },
        {
            'trend': 'Personalization',
            'impact': 'Medium',
            'timeframe': '1-2 years',
            'opportunity_score': 7.5
        }
    ]

def calculate_strategic_fit(
    initiative: StrategicInitiative,
    company_capabilities: Dict[str, float]
) -> float:
    """
    Calculate strategic fit score for an initiative.
    
    Args:
        initiative: Strategic initiative to evaluate
        company_capabilities: Company capability scores
        
    Returns:
        float: Strategic fit score (0-10)
    """
    # Capability requirements for different initiative types
    capability_requirements = {
        'Market Expansion Program': {
            'market_knowledge': 0.3,
            'distribution_network': 0.3,
            'financial_resources': 0.2,
            'brand_strength': 0.2
        },
        'Digital Experience Enhancement': {
            'technical_capability': 0.4,
            'innovation_capacity': 0.3,
            'change_management': 0.2,
            'customer_insight': 0.1
        },
        'Operational Excellence Program': {
            'process_efficiency': 0.4,
            'technical_capability': 0.3,
            'change_management': 0.2,
            'financial_resources': 0.1
        },
        'Sustainable Beauty Initiative': {
            'innovation_capacity': 0.3,
            'supply_chain': 0.3,
            'brand_strength': 0.2,
            'financial_resources': 0.2
        }
    }
    
    if initiative.name not in capability_requirements:
        return 5.0  # Default medium fit
    
    requirements = capability_requirements[initiative.name]
    # Scale up the calculation by 10 to get score in 0-10 range
    fit_score = 10 * sum(
        weight * company_capabilities.get(capability, 0)
        for capability, weight in requirements.items()
    )
    
    return min(10.0, fit_score)

def _calculate_market_position(
    metrics: Dict[str, float],
    competitors: Dict[str, Dict[str, float]]
) -> Dict[str, Any]:
    """Calculate relative market position compared to competitors."""
    position_metrics = {}
    
    for metric, value in metrics.items():
        competitor_values = [comp[metric] for comp in competitors.values()]
        avg_value = np.mean(competitor_values)
        percentile = sum(value > cv for cv in competitor_values) / len(competitor_values) * 100
        
        position_metrics[metric] = {
            'value': value,
            'industry_avg': avg_value,
            'percentile': percentile,
            'relative_position': 'Above Average' if value > avg_value else 'Below Average'
        }
    
    return position_metrics

def _identify_competitive_gaps(
    metrics: Dict[str, float],
    competitors: Dict[str, Dict[str, float]]
) -> List[Dict[str, Any]]:
    """Identify key competitive gaps and improvement opportunities."""
    gaps = []
    
    for metric, value in metrics.items():
        best_competitor = max(
            competitors.items(),
            key=lambda x: x[1].get(metric, 0)
        )
        gap = best_competitor[1].get(metric, 0) - value
        
        if gap > 0:  # There's a gap to close
            gaps.append({
                'metric': metric,
                'current_value': value,
                'best_in_class': best_competitor[1].get(metric, 0),
                'gap': gap,
                'competitor': best_competitor[0],
                'priority': 'High' if gap > value * 0.2 else 'Medium'  # 20% threshold
            })
    
    return sorted(gaps, key=lambda x: x['gap'], reverse=True)
