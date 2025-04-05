"""Unit tests for report generation functionality."""

import pytest
from pathlib import Path
import json
from datetime import datetime
from src.reports.report_generator import (
    ReportGenerator,
    ReportGenerationError,
    DataValidationError,
    ReportRenderingError
)
from src.core.config import (
    BASELINE_DATA,
    MARKET_PENETRATION,
    DIGITAL_METRICS,
    SUSTAINABILITY_TARGETS
)

@pytest.fixture
def sample_data():
    """Provide sample financial data for testing."""
    return {
        'revenue': 13685.2,
        'operating_margin': 0.0956,
        'market_share': 0.089,
        'ebitda': 1725.4,
        'ebitda_margin': 0.1261,
        'assets': 12994.8,
        'liabilities': 7951.3,
        'equity': 5043.5,
        'net_income': 901.4,
        'r_and_d_spend': 512.3,
        'marketing_spend': 2054.7
    }

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "test_outputs"
    output_dir.mkdir()
    return output_dir

class TestReportGenerator:
    """Test suite for ReportGenerator class."""
    
    def test_initialization(self, temp_output_dir):
        """Test ReportGenerator initialization."""
        generator = ReportGenerator(str(temp_output_dir))
        assert generator.output_dir == temp_output_dir
        assert generator.styles is not None
    
    def test_data_validation(self, sample_data):
        """Test input data validation."""
        generator = ReportGenerator()
        
        # Test valid data
        generator._validate_report_data(sample_data)
        
        # Test missing required field
        invalid_data = sample_data.copy()
        del invalid_data['revenue']
        with pytest.raises(DataValidationError):
            generator._validate_report_data(invalid_data)
        
        # Test invalid numeric value
        invalid_data = sample_data.copy()
        invalid_data['operating_margin'] = 'invalid'
        with pytest.raises(DataValidationError):
            generator._validate_report_data(invalid_data)
        
        # Test negative value
        invalid_data = sample_data.copy()
        invalid_data['revenue'] = -1000
        with pytest.raises(DataValidationError):
            generator._validate_report_data(invalid_data)
    
    def test_10k_report_generation(self, temp_output_dir, sample_data):
        """Test generation of 10-K style reports."""
        generator = ReportGenerator(str(temp_output_dir))
        report_paths = generator.generate_10k_reports(sample_data)
        
        # Verify reports were generated
        assert isinstance(report_paths, dict)
        assert all(timeframe in report_paths for timeframe in ['one_year', 'five_year', 'ten_year'])
        assert all(Path(path).exists() for path in report_paths.values())
    
    def test_financial_summary_generation(self, temp_output_dir, sample_data):
        """Test generation of financial summary report."""
        generator = ReportGenerator(str(temp_output_dir))
        report_path = generator.generate_financial_summary(sample_data)
        
        assert Path(report_path).exists()
        assert report_path.endswith('.pdf')
    
    def test_strategic_analysis_generation(self, temp_output_dir, sample_data):
        """Test generation of strategic analysis report."""
        generator = ReportGenerator(str(temp_output_dir))
        market_data = {'market_share': 0.089, 'growth_rate': 0.05}
        competitive_data = {
            'leader_1': {'market_share': 0.15},
            'leader_2': {'market_share': 0.12}
        }
        
        report_path = generator.generate_strategic_analysis(market_data, competitive_data)
        assert Path(report_path).exists()
        assert report_path.endswith('.pdf')
    
    def test_digital_transformation_report(self, temp_output_dir):
        """Test generation of digital transformation report."""
        generator = ReportGenerator(str(temp_output_dir))
        digital_metrics = DIGITAL_METRICS['one_year']
        projections = DIGITAL_METRICS['five_year']
        
        report_path = generator.generate_digital_transformation_report(
            digital_metrics,
            projections
        )
        assert Path(report_path).exists()
        assert report_path.endswith('.pdf')
    
    def test_sustainability_report(self, temp_output_dir):
        """Test generation of sustainability report."""
        generator = ReportGenerator(str(temp_output_dir))
        metrics = SUSTAINABILITY_TARGETS['one_year']
        targets = {
            '2025': SUSTAINABILITY_TARGETS['five_year'],
            '2030': SUSTAINABILITY_TARGETS['ten_year']
        }
        
        report_path = generator.generate_sustainability_report(metrics, targets)
        assert Path(report_path).exists()
        assert report_path.endswith('.pdf')
    
    def test_table_generation(self, sample_data):
        """Test generation of various report tables."""
        generator = ReportGenerator()
        
        # Test financial data table
        table = generator._generate_financial_data_table(sample_data, 'one_year')
        assert table is not None
        
        # Test market analysis table
        table = generator._generate_market_analysis_table(sample_data, 'one_year')
        assert table is not None
        
        # Test strategic initiatives table
        table = generator._generate_strategic_initiatives_table(sample_data, 'one_year')
        assert table is not None
        
        # Test industry comparison table
        table = generator._generate_industry_comparison_table(sample_data, 'one_year')
        assert table is not None
    
    def test_risk_factors(self):
        """Test generation of risk factors."""
        generator = ReportGenerator()
        
        one_year_risks = generator._generate_risk_factors('one_year')
        five_year_risks = generator._generate_risk_factors('five_year')
        ten_year_risks = generator._generate_risk_factors('ten_year')
        
        assert len(one_year_risks) > 0
        assert len(five_year_risks) > 0
        assert len(ten_year_risks) > 0
        
        # Verify different risks for different timeframes
        assert set(one_year_risks) != set(five_year_risks)
        assert set(five_year_risks) != set(ten_year_risks)
    
    def test_swot_analysis(self):
        """Test SWOT analysis generation."""
        generator = ReportGenerator()
        market_data = {'market_share': 0.089, 'growth_rate': 0.05}
        competitive_data = {
            'leader_1': {'market_share': 0.15},
            'leader_2': {'market_share': 0.12}
        }
        
        swot = generator._generate_swot_analysis(market_data, competitive_data)
        assert isinstance(swot, dict)
        assert all(key in swot for key in ['strengths', 'weaknesses', 'opportunities', 'threats'])
        assert all(isinstance(swot[key], list) for key in swot)
    
    def test_digital_maturity_calculation(self):
        """Test digital maturity score calculation."""
        generator = ReportGenerator()
        metrics = {
            'e_commerce_share': 25.0,
            'mobile_traffic': 78,
            'ar_adoption': 45,
            'digital_engagement': 60,
            'personalization_rate': 70
        }
        
        score = generator._calculate_digital_maturity(metrics)
        assert isinstance(score, float)
        assert 0 <= score <= 10
    
    def test_sustainability_score_calculation(self):
        """Test sustainability score calculation."""
        generator = ReportGenerator()
        metrics = SUSTAINABILITY_TARGETS['five_year']
        
        score = generator._calculate_sustainability_score(metrics)
        assert isinstance(score, float)
        assert 0 <= score <= 10
    
    def test_error_handling(self, temp_output_dir):
        """Test error handling in report generation."""
        generator = ReportGenerator(str(temp_output_dir))
        
        # Test with empty data
        with pytest.raises(DataValidationError):
            generator.generate_10k_reports({})
        
        # Test with invalid timeframe
        with pytest.raises(KeyError):
            generator._generate_risk_factors('invalid_timeframe')
        
        # Test with invalid file path
        generator.output_dir = Path('/nonexistent/path')
        with pytest.raises(ReportGenerationError):
            generator.generate_financial_summary({'revenue': 1000})