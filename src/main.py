"""
Main entry point for the financial analysis application.

This module orchestrates the entire analysis process including data collection,
analysis, and report generation.
"""

import sys
import logging
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

from src.core.config import get_config, BASELINE_DATA, MARKET_PENETRATION, DIGITAL_METRICS
from src.core.baseline import get_baseline_data, validate_baseline_data
from src.analysis.quantitative_model import (
    FinancialMetrics,
    analyze_metrics,
    calculate_dcf_valuation,
    calculate_market_share_projection,
    calculate_financial_ratios,
    monte_carlo_simulation
)
from src.reports.report_generator import ReportGenerator
from src.utils.output_handler import OutputHandler
from src.analysis.strategic_summary import generate_strategic_recommendations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Financial Analysis Tool')
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./outputs',
        help='Directory for output files'
    )
    
    parser.add_argument(
        '--scenario',
        choices=['base', 'optimistic', 'pessimistic'],
        default='base',
        help='Analysis scenario to run'
    )
    
    parser.add_argument(
        '--reports',
        nargs='+',
        choices=['financial', 'strategic', 'digital', 'sustainability'],
        default=['financial'],
        help='Types of reports to generate'
    )
    
    parser.add_argument(
        '--monte-carlo',
        action='store_true',
        help='Run Monte Carlo simulations'
    )
    
    return parser.parse_args()

def run_analysis(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Run the complete financial analysis.
    
    Args:
        args: Command line arguments
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    try:
        logger.info("Starting financial analysis")
        
        # Initialize components
        config = get_config()
        baseline_data = get_baseline_data()
        
        if not validate_baseline_data(baseline_data):
            raise ValueError("Invalid baseline data")
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analysis components
        metrics = FinancialMetrics(baseline_data)
        report_gen = ReportGenerator(str(output_dir))
        output_handler = OutputHandler(str(output_dir))
        
        # Perform analysis
        financial_metrics = analyze_metrics(baseline_data)
        results = {
            'financial_metrics': financial_metrics,
            'ratios': calculate_financial_ratios(baseline_data, {}),
            'market_projection': calculate_market_share_projection(
                initial_share=BASELINE_DATA['market_share'],
                market_growth=0.03,  # 3% market growth
                company_growth=0.05,  # 5% company growth
                periods=5
            )
        }
        
        # Run Monte Carlo simulation if requested
        if args.monte_carlo:
            logger.info("Running Monte Carlo simulations")
            simulation_results = monte_carlo_simulation(
                base_revenue=BASELINE_DATA['revenue'],
                growth_mean=0.05,
                growth_std=0.02,
                margin_mean=0.15,
                margin_std=0.03
            )
            results['monte_carlo'] = simulation_results
        
        # Generate requested reports
        report_paths = {}
        
        if 'financial' in args.reports:
            logger.info("Generating 10-K style reports")
            report_data = {
                **baseline_data,  # Include all baseline metrics
                **financial_metrics,  # Include calculated metrics
                'total_investment': baseline_data['assets'],  # Required for ROI calculation
            }
            # Generate all three 10-K reports
            report_paths.update(report_gen.generate_10k_reports(report_data))
            
        if 'strategic' in args.reports:
            logger.info("Generating strategic analysis")
            # Create competitive landscape data
            from config import COMPETITIVE_LANDSCAPE
            competitive_data = {
                'leader_1': {'market_share': 0.15, 'growth_rate': 0.06},
                'leader_2': {'market_share': 0.12, 'growth_rate': 0.05},
                'challenger_1': {'market_share': 0.09, 'growth_rate': 0.08}
            }
            
            strategic_recommendations = generate_strategic_recommendations(
                market_data=results['market_projection'],
                financial_data=results['financial_metrics']
            )
            report_paths['strategic'] = report_gen.generate_strategic_analysis(
                results['market_projection'],
                competitive_data
            )
            
        if 'digital' in args.reports:
            logger.info("Generating digital transformation report")
            report_paths['digital'] = report_gen.generate_digital_transformation_report(
                DIGITAL_METRICS['one_year'],
                DIGITAL_METRICS['five_year']
            )
            
        if 'sustainability' in args.reports:
            logger.info("Generating sustainability report")
            from config import SUSTAINABILITY_TARGETS
            report_paths['sustainability'] = report_gen.generate_sustainability_report(
                SUSTAINABILITY_TARGETS['one_year'],
                SUSTAINABILITY_TARGETS
            )
        
        # Save results
        results['report_paths'] = report_paths
        output_handler.save_results(results, 'analysis_results')
        
        logger.info("Analysis completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        raise RuntimeError(f"Analysis failed: {str(e)}")

def main() -> None:
    """Main entry point."""
    try:
        args = parse_arguments()
        results = run_analysis(args)
        
        # Print summary to console
        print("\nAnalysis Summary:")
        print("-" * 50)
        print(f"Reports generated: {', '.join(results['report_paths'].keys())}")
        print(f"Output directory: {args.output_dir}")
        print("-" * 50)
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
