"""
Main entry point for generating 1, 5, and 10-year 10-K style projection reports.
(Version 2 - Improved)
"""

import sys
import logging
import argparse
from typing import Dict, Any, Optional # Added Optional
from pathlib import Path
import traceback # For more detailed error logging

# Simplified imports
from src.core.config import get_config, BASELINE_DATA, GROWTH_ASSUMPTIONS
from src.core.baseline import get_baseline_data
from src.analysis.quantitative_model import calculate_10k_projections # Main calculation function
from src.reports.report_generator import ReportGenerator, ReportGenerationError, ReportRenderingError # Import specific errors

# Configure basic logging
# Consider adding timestamps to log file names if running frequently
log_file = '10k_generator.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout) # Keep console output
    ]
)
# Separate logger for this module
logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='BFC 10-K Style Projection Report Generator')
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./outputs',
        help='Directory for output PDF files (Default: ./outputs)'
    )
    # No other arguments needed for this focused version
    return parser.parse_args()

def run_report_generation(args: argparse.Namespace) -> None:
    """
    Runs the 10-K report generation process with enhanced error handling.
    """
    try:
        logger.info("="*50)
        logger.info("Starting 10-K projection report generation process...")

        # --- Configuration and Setup ---
        config = get_config() # Load config if needed (e.g., for log level from env)
        output_dir = Path(args.output_dir)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Output directory set to: {output_dir.resolve()}")
        except OSError as e:
            logger.error(f"Failed to create output directory '{output_dir}': {e}")
            raise ReportGenerationError(f"Cannot create output directory: {e}") from e

        # --- Data Loading ---
        logger.info("Loading baseline data...")
        # get_baseline_data now includes basic checks and warnings
        baseline_data = get_baseline_data()
        logger.info("Baseline data loaded.")

        # --- Calculations ---
        logger.info("Calculating financial projections...")
        # calculate_10k_projections should handle missing keys gracefully or raise ValueError
        projection_data = calculate_10k_projections(baseline_data, GROWTH_ASSUMPTIONS)
        logger.info("Financial projections calculated for all timeframes.")

        # --- Report Generation ---
        logger.info("Initializing report generator...")
        report_gen = ReportGenerator(str(output_dir))

        logger.info("Generating 1, 5, and 10-year 10-K reports...")
        # generate_10k_reports handles parallel generation and aggregates results/errors
        generated_paths: Optional[Dict[str, str]] = report_gen.generate_10k_reports(projection_data)

        # --- Summarize Results ---
        if generated_paths:
            logger.info("--- Report Generation Summary ---")
            all_successful = True
            for timeframe, path_or_error in generated_paths.items():
                if "FAILED:" not in path_or_error:
                    logger.info(f"  [SUCCESS] {timeframe.replace('_',' ').title()} Report: {Path(path_or_error).name}")
                else:
                    logger.error(f"  [FAILED]  {timeframe.replace('_',' ').title()} Report Generation: {path_or_error}")
                    all_successful = False
            if not all_successful:
                 logger.warning("One or more reports failed to generate. See logs above for details.")
        else:
            logger.warning("No reports were generated. Check prior log messages.")

        logger.info("Report generation process finished.")
        logger.info("="*50)

    # Specific error handling
    except (ReportGenerationError, ReportRenderingError) as rge:
         logger.error(f"A critical report generation error occurred: {rge}")
         logger.debug(traceback.format_exc()) # Log full traceback for debugging
         print(f"\nERROR: Report Generation Failed. Check log file '{log_file}' for details.", file=sys.stderr)
         sys.exit(1)
    except ValueError as ve: # Catch data validation/calculation errors
         logger.error(f"A data error occurred: {ve}")
         logger.debug(traceback.format_exc())
         print(f"\nERROR: Data Error. Check input data and log file '{log_file}'.", file=sys.stderr)
         sys.exit(1)
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"An unexpected error occurred during the process: {str(e)}")
        logger.debug(traceback.format_exc())
        print(f"\nUNEXPECTED ERROR. Check log file '{log_file}'.", file=sys.stderr)
        sys.exit(1)

def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    run_report_generation(args)

if __name__ == '__main__':
    main()