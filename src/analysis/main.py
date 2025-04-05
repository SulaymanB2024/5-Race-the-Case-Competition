"""
Main entry point for generating 1, 5, and 10-year 10-K style projection reports.
(Version 3 - Refined)
"""

import sys
import logging
import argparse
from typing import Dict, Any, Optional
from pathlib import Path
import traceback

# --- Module Imports ---
# Use absolute imports assuming 'src' is runnable or PYTHONPATH is set
from src.core.config import get_config, BASELINE_DATA, GROWTH_ASSUMPTIONS
from src.core.baseline import get_baseline_data
from src.analysis.quantitative_model import calculate_10k_projections
from src.reports.report_generator import ReportGenerator, ReportGenerationError, ReportRenderingError

# --- Logging Setup ---
log_file = '10k_generator_v3.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s', # Slightly more detailed format
    handlers=[
        logging.FileHandler(log_file, mode='w'), # Overwrite log each run
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__) # Get logger for this module

# --- Argument Parsing ---
def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for output directory."""
    parser = argparse.ArgumentParser(
        description='BFC 10-K Style Financial Projection Report Generator (v3)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Show defaults in help
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./outputs_v3', # Changed default output dir
        help='Directory for output PDF report files.'
    )
    return parser.parse_args()

# --- Main Execution Logic ---
def run_report_generation(args: argparse.Namespace) -> None:
    """
    Orchestrates the 10-K report generation process: setup, data, calculation, PDF generation.
    """
    try:
        logger.info("="*60)
        logger.info("🚀 Starting BFC 10-K Projection Report Generator (v3)...")
        logger.info("="*60)

        # 1. Setup Output Directory
        output_dir = Path(args.output_dir).resolve() # Get absolute path
        logger.info(f"Ensuring output directory exists: {output_dir}")
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Output directory ready at: {output_dir}")
        except OSError as e:
            logger.exception(f"Fatal: Failed to create output directory '{output_dir}'. Error: {e}")
            raise ReportGenerationError(f"Cannot create output directory: {e}")

        # 2. Load Data
        logger.info("Loading baseline financial data...")
        baseline_data = get_baseline_data() # Includes basic checks/warnings
        if not baseline_data: # Should not happen if get_baseline_data raises error on empty
             logger.error("Fatal: Baseline data could not be loaded.")
             raise ValueError("Failed to load baseline data.")
        logger.info(f"Baseline data (Year 2018) loaded successfully. Found {len(baseline_data)} metrics.")
        logger.debug(f"Baseline keys include: {list(baseline_data.keys())[:5]}...") # Log first few keys

        # 3. Perform Calculations
        logger.info("Calculating 1, 5, 10-year financial projections...")
        # This function now calculates projections for all timeframes
        projection_data = calculate_10k_projections(baseline_data, GROWTH_ASSUMPTIONS)
        if not all(tf in projection_data for tf in ['one_year', 'five_year', 'ten_year']):
             logger.warning("Projection calculations did not return data for all expected timeframes.")
        logger.info("Financial projections calculated.")
        logger.debug(f"Projection data structure keys: {list(projection_data.keys())}")

        # 4. Generate Reports
        logger.info("Initializing PDF Report Generator...")
        report_gen = ReportGenerator(str(output_dir))
        logger.info(f"Generating 10-K reports for timeframes: {list(projection_data.keys() - {'baseline'})}...")

        # generate_10k_reports handles parallelism and error aggregation internally
        generated_paths: Optional[Dict[str, str]] = report_gen.generate_10k_reports(projection_data)

        # 5. Summarize Outcome
        logger.info("-" * 60)
        if generated_paths:
            logger.info("✅ Report Generation Summary:")
            all_successful = True
            for timeframe, path_or_error in sorted(generated_paths.items()): # Sort output
                if "FAILED:" not in path_or_error:
                    logger.info(f"  [SUCCESS] {timeframe.replace('_',' ').title():<10} Report -> {Path(path_or_error).name}")
                else:
                    logger.error(f"  [FAILED]  {timeframe.replace('_',' ').title():<10} Report -> {path_or_error}")
                    all_successful = False
            if not all_successful:
                 logger.warning("One or more reports failed. Review log entries above for details.")
            print(f"\nReport generation complete. PDFs saved in: {output_dir}")
        else:
            logger.error("❌ No reports were generated successfully.")
            print(f"\nReport generation failed. No PDFs were created. Check log: {log_file}")

        logger.info("="*60)
        logger.info("🏁 BFC 10-K Projection Report Generator Finished.")
        logger.info("="*60)

    # --- Error Handling ---
    except (ReportGenerationError, ReportRenderingError, ValueError) as e:
         # Handle known error types gracefully
         error_type = type(e).__name__
         logger.exception(f"Fatal Error ({error_type}): {e}") # Log exception info
         print(f"\n❌ ERROR ({error_type}): Process Aborted. See log '{log_file}' for details.", file=sys.stderr)
         sys.exit(1) # Exit with non-zero code
    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"An unexpected critical error occurred: {str(e)}")
        print(f"\n❌ UNEXPECTED ERROR: Process Aborted. Check log file '{log_file}'.", file=sys.stderr)
        sys.exit(2) # Different exit code for unexpected errors

def main() -> None:
    """Main entry point."""
    args = parse_arguments()
    run_report_generation(args)

if __name__ == '__main__':
    main()