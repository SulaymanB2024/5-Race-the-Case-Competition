"""Tests for output generation and report handling."""

import pytest
from pathlib import Path
import json
import os
from output_handler import OutputHandler
from report_generator import ReportGenerator

@pytest.fixture
def output_handler():
    """Fixture for output handler with test directory."""
    test_output_dir = "test_outputs"
    handler = OutputHandler(test_output_dir)
    yield handler
    # Cleanup after tests
    if os.path.exists(test_output_dir):
        for file in Path(test_output_dir).glob("*"):
            file.unlink()
        os.rmdir(test_output_dir)

@pytest.fixture
def report_generator():
    """Fixture for report generator with test directory."""
    test_output_dir = "test_reports"
    generator = ReportGenerator(test_output_dir)
    yield generator
    # Cleanup after tests
    if os.path.exists(test_output_dir):
        for file in Path(test_output_dir).glob("*"):
            file.unlink()
        os.rmdir(test_output_dir)

def test_save_results(output_handler):
    """Test saving analysis results."""
    test_data = {
        'metric1': 100,
        'metric2': 200,
        'nested': {
            'sub1': 0.5,
            'sub2': 0.7
        }
    }
    
    filepath = output_handler.save_results(test_data, "test_results")
    assert os.path.exists(filepath)
    
    # Verify content
    with open(filepath) as f:
        saved_data = json.load(f)
    assert saved_data == test_data

def test_create_financial_dashboard(output_handler):
    """Test financial dashboard creation."""
    metrics = {
        'roi': 15.5,
        'market_growth': 7.2,
        'operating_margin': 12.0,
        'revenue_growth': 5.5
    }
    
    # Test without saving
    output_handler.create_financial_dashboard(metrics)
    
    # Test with saving
    save_path = os.path.join(output_handler.output_dir, "test_dashboard.png")
    output_handler.create_financial_dashboard(metrics, save_path)
    assert os.path.exists(save_path)

def test_export_to_excel(output_handler):
    """Test Excel export functionality."""
    test_data = {
        'Sheet1': {
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        },
        'Sheet2': {
            'metrics': [10, 20, 30],
            'categories': ['X', 'Y', 'Z']
        }
    }
    
    filepath = output_handler.export_to_excel(test_data, "test_export")
    assert os.path.exists(filepath)
    assert filepath.endswith(".xlsx")

def test_generate_summary_plots(output_handler):
    """Test summary plot generation."""
    test_data = {
        'Revenue': [100, 120, 140, 160, 180],
        'Profit': [20, 24, 28, 32, 36]
    }
    
    # Test different plot types
    plot_paths = output_handler.generate_summary_plots(
        test_data,
        plot_type='line',
        save_dir=output_handler.output_dir
    )
    
    assert len(plot_paths) == len(test_data)
    for path in plot_paths.values():
        assert os.path.exists(path)

def test_financial_report_generation(report_generator):
    """Test financial report generation."""
    test_data = {
        'revenue': 1000000,
        'operating_margin': 0.15,
        'net_income': 120000,
        'total_investment': 500000
    }
    
    report_path = report_generator.generate_financial_summary(test_data)
    assert os.path.exists(report_path)
    assert report_path.endswith(".pdf")

def test_strategic_report_generation(report_generator):
    """Test strategic analysis report generation."""
    market_data = {
        'market_share': 0.07,
        'growth_rate': 0.05
    }
    
    competitive_data = {
        'competitor1': {'market_share': 0.10},
        'competitor2': {'market_share': 0.05}
    }
    
    report_path = report_generator.generate_strategic_analysis(
        market_data,
        competitive_data
    )
    assert os.path.exists(report_path)
    assert report_path.endswith(".pdf")

def test_digital_transformation_report(report_generator):
    """Test digital transformation report generation."""
    metrics = {
        'e_commerce_share': 15,
        'mobile_traffic': 55,
        'ar_adoption': 10
    }
    
    projections = {
        'e_commerce_target': 30,
        'mobile_target': 70,
        'ar_target': 25
    }
    
    report_path = report_generator.generate_digital_transformation_report(
        metrics,
        projections
    )
    assert os.path.exists(report_path)
    assert report_path.endswith(".pdf")