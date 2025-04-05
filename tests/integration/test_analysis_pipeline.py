"""Integration tests for the complete analysis pipeline."""

import pytest
import os
from pathlib import Path
from src.core.config import get_config, BASELINE_DATA
from src.core.baseline import get_baseline_data, validate_baseline_data
from src.analysis.quantitative_model import FinancialMetrics
from src.reports.report_generator import ReportGenerator
from src.utils.output_handler import OutputHandler

@pytest.fixture
def test_output_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    return tmp_path / "test_outputs"

@pytest.fixture
def setup_analysis_components(test_output_dir):
    """Set up all components needed for analysis."""
    test_output_dir.mkdir(exist_ok=True)
    baseline_data = get_baseline_data()
    metrics = FinancialMetrics(baseline_data)
    report_gen = ReportGenerator(str(test_output_dir))
    output_handler = OutputHandler(str(test_output_dir))
    
    return {
        'baseline_data': baseline_data,
        'metrics': metrics,
        'report_gen': report_gen,
        'output_handler': output_handler
    }

class TestAnalysisPipeline:
    """Test suite for the complete analysis pipeline."""
    
    def test_end_to_end_analysis(self, setup_analysis_components, test_output_dir):
        """Test the complete analysis pipeline from data input to report generation."""
        components = setup_analysis_components
        
        # Validate input data
        assert validate_baseline_data(components['baseline_data'])
        
        # Calculate financial metrics
        metrics = components['metrics']
        financial_results = metrics.calculate_ratios()
        assert isinstance(financial_results, dict)
        assert all(key in financial_results for key in ['current_ratio', 'debt_to_equity'])
        
        # Generate reports
        report_gen = components['report_gen']
        report_data = {
            **components['baseline_data'],
            **financial_results,
            'total_investment': components['baseline_data']['assets']
        }
        
        report_paths = report_gen.generate_10k_reports(report_data)
        assert isinstance(report_paths, dict)
        
        # Verify report files were created
        for report_path in report_paths.values():
            assert Path(report_path).exists()
        
        # Save results
        output_handler = components['output_handler']
        results = {
            'financial_metrics': financial_results,
            'report_paths': report_paths
        }
        
        output_path = output_handler.save_results(results, 'test_analysis')
        assert Path(output_path).exists()
        
        # Verify output JSON structure
        saved_results = output_handler.load_results(output_path)
        assert isinstance(saved_results, dict)
        assert 'financial_metrics' in saved_results
        assert 'report_paths' in saved_results
    
    def test_error_handling_pipeline(self, setup_analysis_components, test_output_dir):
        """Test error handling throughout the analysis pipeline."""
        components = setup_analysis_components
        
        # Test invalid data handling
        invalid_data = {**components['baseline_data']}
        invalid_data['market_share'] = -0.1
        
        with pytest.raises(ValueError):
            FinancialMetrics(invalid_data)
        
        # Test report generation with missing data
        report_gen = components['report_gen']
        incomplete_data = {'revenue': 1000000}  # Missing required fields
        
        with pytest.raises(KeyError):
            report_gen.generate_10k_reports(incomplete_data)
        
        # Test output handling with invalid paths
        output_handler = components['output_handler']
        invalid_dir = "/nonexistent/directory"
        
        with pytest.raises(Exception):
            OutputHandler(invalid_dir)
    
    def test_data_consistency(self, setup_analysis_components):
        """Test data consistency across different components."""
        components = setup_analysis_components
        baseline_data = components['baseline_data']
        metrics = components['metrics']
        
        # Calculate metrics
        ratios = metrics.calculate_ratios()
        
        # Verify calculations match expected values
        if 'current_assets' in baseline_data and 'current_liabilities' in baseline_data:
            expected_current_ratio = (
                baseline_data['current_assets'] / baseline_data['current_liabilities']
            )
            assert ratios['current_ratio'] == pytest.approx(expected_current_ratio)
        
        if 'net_income' in baseline_data and 'total_investment' in baseline_data:
            expected_roi = (
                baseline_data['net_income'] / baseline_data['total_investment'] * 100
            )
            calculated_roi = metrics.calculate_roi()
            assert calculated_roi == pytest.approx(expected_roi)