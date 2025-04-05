"""
Report generation module for financial analysis results.

This module handles the generation of various report types including financial summaries,
strategic analysis, and competitive positioning reports.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Callable
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import threading
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from src.core.config import (
    BASELINE_DATA, MARKET_PENETRATION, COMPETITIVE_MATRIX,
    DIGITAL_METRICS, SUSTAINABILITY_TARGETS, GROWTH_ASSUMPTIONS
)
from src.utils.output_handler import OutputHandler

# Configure logging
logger = logging.getLogger(__name__)

class ReportGenerationError(Exception):
    """Base exception for report generation errors."""
    pass

class DataValidationError(ReportGenerationError):
    """Exception for data validation errors."""
    pass

class ReportRenderingError(ReportGenerationError):
    """Exception for PDF rendering errors."""
    pass

class ReportGenerator:
    """Handles generation of various report types with caching and parallel processing."""
    
    def __init__(self, output_dir: Optional[str] = None, cache_size: int = 32):
        """
        Initialize report generator with output directory and caching.
        
        Args:
            output_dir: Directory to save outputs
            cache_size: Size of the LRU cache for report sections
        """
        self.output_handler = OutputHandler(output_dir)
        self.output_dir = Path(output_dir or './outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize styles with custom additions
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()
        
        # Thread safety
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize section generators
        self._section_generators = self._init_section_generators()
    
    def _init_custom_styles(self) -> None:
        """Initialize custom paragraph and table styles."""
        self.styles.add(
            ParagraphStyle(
                name='HeaderTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='SectionTitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=10
            )
        )
        self.styles.add(
            ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                leading=14,
                spaceBefore=6,
                spaceAfter=6
            )
        )
    
    def _init_section_generators(self) -> Dict[str, Callable]:
        """Initialize mapping of section names to their generator functions."""
        return {
            'business_overview': self._generate_business_overview,
            'financial_data': self._generate_financial_data_table,
            'md_and_a': self._generate_md_and_a,
            'market_analysis': self._generate_market_analysis_table,
            'risk_factors': self._generate_risk_factors,
            'strategic_initiatives': self._generate_strategic_initiatives_table,
            'industry_comparison': self._generate_industry_comparison_table,
            'detailed_projections': self._generate_detailed_projections
        }
    
    @lru_cache(maxsize=32)
    def generate_10k_reports(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate comprehensive 10-K style reports for different time horizons.
        
        Args:
            data: Financial and business data for report generation
            
        Returns:
            Dict[str, str]: Mapping of timeframe to report file paths
            
        Raises:
            ReportGenerationError: If report generation fails
        """
        try:
            # Validate input data
            self._validate_report_data(data)
            
            # Generate reports in parallel
            report_tasks = {
                timeframe: (data, timeframe)
                for timeframe in ['one_year', 'five_year', 'ten_year']
            }
            
            report_paths = {}
            with ThreadPoolExecutor() as executor:
                future_to_timeframe = {
                    executor.submit(self._generate_10k_report, *args): timeframe
                    for timeframe, args in report_tasks.items()
                }
                
                for future in future_to_timeframe:
                    timeframe = future_to_timeframe[future]
                    try:
                        report_paths[timeframe] = future.result()
                    except Exception as e:
                        logger.error(f"Failed to generate {timeframe} report: {str(e)}")
                        raise
            
            return report_paths
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate 10-K reports: {str(e)}")
    
    def _validate_report_data(self, data: Dict[str, Any]) -> None:
        """
        Validate input data for report generation.
        
        Args:
            data: Data to validate
            
        Raises:
            DataValidationError: If data validation fails
        """
        required_fields = {
            'revenue', 'operating_margin', 'market_share', 'ebitda',
            'assets', 'liabilities', 'equity'
        }
        
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            raise DataValidationError(
                f"Missing required fields for report generation: {missing_fields}"
            )
        
        # Validate numeric fields
        numeric_fields = {
            field: data[field]
            for field in required_fields
            if field in data
        }
        
        for field, value in numeric_fields.items():
            if not isinstance(value, (int, float)):
                raise DataValidationError(
                    f"Field '{field}' must be numeric, got {type(value).__name__}"
                )
            if value < 0:
                raise DataValidationError(
                    f"Field '{field}' cannot be negative, got {value}"
                )
    
    def _generate_10k_report(self, data: Dict[str, Any], timeframe: str) -> str:
        """
        Generate a single 10-K style report for a specific timeframe.
        
        Args:
            data: Financial and business data
            timeframe: Report timeframe ('one_year', 'five_year', 'ten_year')
            
        Returns:
            str: Path to generated report
            
        Raises:
            ReportRenderingError: If report rendering fails
        """
        try:
            output_path = self.output_dir / f'10k_report_{timeframe}.pdf'
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Generate report elements in parallel
            story = []
            story.append(Paragraph(
                f"Beauty First Cosmetics - {timeframe.replace('_', ' ').title()} Report",
                self.styles['HeaderTitle']
            ))
            story.append(Spacer(1, 30))
            
            # Generate sections in parallel
            section_tasks = {
                section: executor.submit(generator, data, timeframe)
                for section, generator in self._section_generators.items()
            }
            
            # Add sections in order
            for section_name in self._section_generators.keys():
                story.append(Paragraph(
                    section_name.replace('_', ' ').title(),
                    self.styles['SectionTitle']
                ))
                story.append(Spacer(1, 12))
                
                # Get section content
                section_content = section_tasks[section_name].result()
                if isinstance(section_content, (str, Paragraph)):
                    story.append(Paragraph(str(section_content), self.styles['BodyText']))
                elif isinstance(section_content, (Table, Image, ListFlowable)):
                    story.append(section_content)
                elif isinstance(section_content, list):
                    for item in section_content:
                        if isinstance(item, str):
                            story.append(
                                ListItem(
                                    Paragraph(item, self.styles['BodyText']),
                                    leftIndent=20
                                )
                            )
                        else:
                            story.append(item)
                
                story.append(Spacer(1, 20))
                
                # Add page break after major sections
                if section_name in {'business_overview', 'financial_data', 'md_and_a'}:
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            logger.info(f"Generated {timeframe} report at {output_path}")
            return str(output_path)
            
        except Exception as e:
            raise ReportRenderingError(f"Failed to generate {timeframe} report: {str(e)}")
    
    # ... existing section generator methods with improved error handling ...
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self._executor.shutdown(wait=True)
        plt.close('all')  # Clean up any remaining plots

    def generate_financial_summary(self, data: Dict[str, Any]) -> str:
        """
        Generate a comprehensive financial summary report.
        
        Args:
            data: Financial metrics and analysis results
            
        Returns:
            str: Path to generated report
        """
        try:
            output_path = self.output_dir / 'financial_summary.pdf'
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            story = []
            
            # Title and Company Overview
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("Financial Summary Report", title_style))
            story.append(Spacer(1, 12))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            exec_summary = """
            Beauty First Cosmetics (BFC) demonstrates strong financial performance with a focus on sustainable growth
            and market expansion. This report presents a comprehensive analysis of key financial metrics,
            operational efficiency, and market positioning.
            """
            story.append(Paragraph(exec_summary, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Key Performance Metrics
            story.append(Paragraph("Key Performance Metrics", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            metrics_data = [
                ['Metric', 'Value', 'Industry Benchmark'],
                ['Revenue', f"${data.get('revenue', 0):,.2f}M", 'N/A'],
                ['Operating Margin', f"{data.get('operating_margin', 0)*100:.1f}%", "10.5%"],
                ['ROI', f"{(data.get('net_income', 0) / data.get('total_investment', 1))*100:.1f}%", "15.0%"],
                ['Market Share', f"{data.get('market_share', 0)*100:.1f}%", "14.3%"],
                ['EBITDA Margin', f"{data.get('ebitda_margin', 0)*100:.1f}%", "16.5%"]
            ]
            
            table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Financial Ratios Analysis
            story.append(Paragraph("Financial Ratios Analysis", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Profitability Ratios
            story.append(Paragraph("Profitability Ratios", self.styles['Heading3']))
            prof_data = [
                ['Ratio', 'Value', 'Assessment'],
                ['Gross Margin', f"{data.get('gross_profit', 0) / data.get('revenue', 1) * 100:.1f}%", 'Strong'],
                ['Operating Margin', f"{data.get('operating_margin', 0)*100:.1f}%", 'Above Average'],
                ['Net Margin', f"{data.get('net_income', 0) / data.get('revenue', 1) * 100:.1f}%", 'Competitive'],
                ['ROCE', f"{data.get('roce', 0):.1f}%", 'Industry Leading']
            ]
            
            prof_table = Table(prof_data, colWidths=[2.5*inch, 2*inch, 2*inch])
            prof_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(prof_table)
            story.append(Spacer(1, 20))
            
            # Efficiency Ratios
            story.append(Paragraph("Efficiency Ratios", self.styles['Heading3']))
            eff_data = [
                ['Ratio', 'Value', 'Industry Average'],
                ['Asset Turnover', f"{data.get('asset_turnover', 0):.2f}", "0.65"],
                ['Inventory Turnover', f"{data.get('inventory_turnover', 0):.1f}", "4.2"],
                ['Receivables Turnover', f"{data.get('receivables', 0) / data.get('revenue', 1):.2f}", "8.5"]
            ]
            
            eff_table = Table(eff_data, colWidths=[2.5*inch, 2*inch, 2*inch])
            eff_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(eff_table)
            story.append(Spacer(1, 20))
            
            # Liquidity and Solvency
            story.append(Paragraph("Liquidity & Solvency", self.styles['Heading3']))
            liq_data = [
                ['Ratio', 'Value', 'Target Range'],
                ['Current Ratio', f"{data.get('current_ratio', 0):.2f}", "1.5 - 2.5"],
                ['Quick Ratio', f"{data.get('quick_ratio', 0):.2f}", "1.0 - 1.5"],
                ['Debt to Equity', f"{data.get('debt_to_equity', 0):.2f}", "0.3 - 0.6"]
            ]
            
            liq_table = Table(liq_data, colWidths=[2.5*inch, 2*inch, 2*inch])
            liq_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(liq_table)
            story.append(Spacer(1, 20))
            
            # Market Performance
            story.append(Paragraph("Market Performance", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            market_analysis = f"""
            BFC maintains a {data.get('market_share', 0)*100:.1f}% market share in a $52B industry,
            positioning it as a significant player in the cosmetics sector. The company's growth rate
            of {data.get('market_growth', 0)*100:.1f}% demonstrates strong market momentum.
            Key growth drivers include:
            • Strong digital presence and e-commerce penetration
            • Expanding international market reach
            • Innovation in sustainable product lines
            • Strategic marketing initiatives
            """
            story.append(Paragraph(market_analysis, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Investment & Growth
            story.append(Paragraph("Investment & Growth", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            inv_data = [
                ['Metric', 'Amount ($M)', '% of Revenue'],
                ['R&D Investment', f"{data.get('r_and_d_spend', 0):.1f}", f"{data.get('r_and_d_spend', 0)/data.get('revenue', 1)*100:.1f}%"],
                ['Marketing Spend', f"{data.get('marketing_spend', 0)::.1f}", f"{data.get('marketing_spend', 0)/data.get('revenue', 1)*100:.1f}%"],
                ['Capital Expenditure', f"{data.get('assets', 0)*0.15:.1f}", "15.0%"]
            ]
            
            inv_table = Table(inv_data, colWidths=[2.5*inch, 2*inch, 2*inch])
            inv_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(inv_table)
            story.append(Spacer(1, 20))
            
            # Future Outlook
            story.append(Paragraph("Future Outlook", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            outlook = """
            Based on current performance metrics and market conditions, BFC is well-positioned for
            sustained growth. Key opportunities include:
            • Digital transformation initiatives
            • Geographic expansion in high-growth markets
            • Sustainability-driven product innovation
            • Operational efficiency improvements
            
            The company's strong financial position and strategic investments support a positive
            growth trajectory for the coming years.
            """
            story.append(Paragraph(outlook, self.styles['Normal']))
            
            # Build the PDF
            doc.build(story)
            logger.info(f"Financial summary generated at {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating financial summary: {str(e)}")
            raise RuntimeError(f"Failed to generate financial summary: {str(e)}")
    
    def generate_strategic_analysis(
        self,
        market_data: Union[Dict[str, Any], List[float]],
        competitive_data: Dict[str, Any]
    ) -> str:
        """
        Generate strategic analysis report.
        
        Args:
            market_data: Market analysis data (dict or list of projections)
            competitive_data: Competitive analysis data
            
        Returns:
            str: Path to generated report
        """
        try:
            output_path = self.output_dir / 'strategic_analysis.pdf'
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            story.append(Paragraph("Strategic Analysis Report", title_style))
            story.append(Spacer(1, 12))
            
            # Market Position
            story.append(Paragraph("Market Position", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Convert list data to dict format if needed
            if isinstance(market_data, list):
                current_share = market_data[0]
                projected_share = market_data[-1]
                growth_rate = (projected_share / current_share) ** (1/len(market_data)) - 1
                market_metrics = [
                    ['Metric', 'Value'],
                    ['Current Market Share', f"{current_share*100:.1f}%"],
                    ['Projected Market Share', f"{projected_share*100:.1f}%"],
                    ['Growth Rate', f"{growth_rate*100:.1f}%"]
                ]
            else:
                market_metrics = [
                    ['Metric', 'Value'],
                    ['Market Share', f"{market_data.get('market_share', 0)*100:.1f}%"],
                    ['Growth Rate', f"{market_data.get('growth_rate', 0)*100:.1f}%"]
                ]
            
            market_table = Table(market_metrics, colWidths=[3*inch, 2*inch])
            market_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(market_table)
            story.append(Spacer(1, 20))
            
            # Competitive Analysis
            story.append(Paragraph("Competitive Analysis", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            comp_data = [['Competitor', 'Market Share']]
            for comp, data in competitive_data.items():
                comp_data.append([comp, f"{data.get('market_share', 0)*100:.1f}%"])
            
            comp_table = Table(comp_data, colWidths=[3*inch, 2*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(comp_table)
            
            # Build the PDF
            doc.build(story)
            logger.info(f"Strategic analysis generated at {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating strategic analysis: {str(e)}")
            raise RuntimeError(f"Failed to generate strategic analysis: {str(e)}")
    
    def generate_digital_transformation_report(
        self,
        digital_metrics: Dict[str, Any],
        projections: Dict[str, Any]
    ) -> str:
        """
        Generate digital transformation report.
        
        Args:
            digital_metrics: Current digital metrics
            projections: Future projections
            
        Returns:
            str: Path to generated report
        """
        try:
            output_path = self.output_dir / 'digital_transformation.pdf'
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            story.append(Paragraph("Digital Transformation Report", title_style))
            story.append(Spacer(1, 12))
            
            # Current Metrics
            story.append(Paragraph("Current Digital Metrics", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            metrics_data = [['Metric', 'Current', 'Target']]
            for metric, value in digital_metrics.items():
                target = projections.get(f"{metric}_target", "N/A")
                metrics_data.append([
                    metric.replace('_', ' ').title(),
                    f"{value}%",
                    f"{target}%"
                ])
            
            metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metrics_table)
            
            # Build the PDF
            doc.build(story)
            logger.info(f"Digital transformation report generated at {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating digital transformation report: {str(e)}")
            raise RuntimeError(f"Failed to generate digital transformation report: {str(e)}")
    
    def generate_sustainability_report(
        self,
        metrics: Dict[str, Any],
        targets: Dict[str, Any]
    ) -> str:
        """
        Generate sustainability report.
        
        Args:
            metrics: Current sustainability metrics
            targets: Sustainability targets
            
        Returns:
            str: Path to generated report
        """
        try:
            output_path = self.output_dir / 'sustainability.pdf'
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            story.append(Paragraph("Sustainability Report", title_style))
            story.append(Spacer(1, 12))
            
            # Metrics Table
            metrics_data = [['Metric', 'Current', '2025 Target', '2030 Target']]
            for metric, value in metrics.items():
                metrics_data.append([
                    metric.replace('_', ' ').title(),
                    f"{value}%",
                    f"{targets.get('2025', {}).get(metric, 'N/A')}%",
                    f"{targets.get('2030', {}).get(metric, 'N/A')}%"
                ])
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metrics_table)
            
            # Build the PDF
            doc.build(story)
            logger.info(f"Sustainability report generated at {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating sustainability report: {str(e)}")
            raise RuntimeError(f"Failed to generate sustainability report: {str(e)}")
    
    def generate_10k_reports(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive 10-K style reports for different time horizons."""
        report_paths = {}
        report_paths['one_year'] = self._generate_10k_report(data, 'one_year')
        report_paths['five_year'] = self._generate_10k_report(data, 'five_year')
        report_paths['ten_year'] = self._generate_10k_report(data, 'ten_year')
        return report_paths
        
    def _generate_10k_report(self, data: Dict[str, Any], timeframe: str) -> str:
        """Generate a single 10-K style report for a specific timeframe."""
        try:
            output_path = self.output_dir / f'10k_report_{timeframe}.pdf'
            doc = SimpleDocTemplate(str(output_path), pagesize=letter)
            story = []
            
            # Title Page
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )
            
            period_map = {
                'one_year': '2026',
                'five_year': '2030',
                'ten_year': '2035'
            }
            
            story.append(Paragraph(f"FORM 10-K PROJECTION", title_style))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Beauty First Cosmetics (BFC)", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Fiscal Year {period_map[timeframe]} Projection", self.styles['Heading2']))
            story.append(Spacer(1, 30))
            
            # Part I: Business Overview
            story.append(Paragraph("PART I - BUSINESS OVERVIEW", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            business_overview = self._generate_business_overview(data, timeframe)
            story.append(Paragraph(business_overview, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Industry Comparison
            story.append(Paragraph("Industry Position", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(self._generate_industry_comparison_table(data, timeframe))
            story.append(Spacer(1, 20))
            
            # Part II: Financial Data
            story.append(Paragraph("PART II - FINANCIAL DATA", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Selected Financial Data Table
            financial_data = self._generate_financial_data_table(data, timeframe)
            story.append(financial_data)
            story.append(Spacer(1, 20))
            
            # Detailed Financial Projections
            story.append(Paragraph("Detailed Financial Projections", self.styles['Heading3']))
            story.append(Spacer(1, 12))
            story.append(self._generate_detailed_projections(data, timeframe))
            story.append(Spacer(1, 20))
            
            # Management Discussion
            story.append(Paragraph("Management's Discussion and Analysis", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            md_and_a = self._generate_md_and_a(data, timeframe)
            story.append(Paragraph(md_and_a, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Part III: Market Analysis
            story.append(Paragraph("PART III - MARKET ANALYSIS", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            market_data = self._generate_market_analysis_table(data, timeframe)
            story.append(market_data)
            story.append(Spacer(1, 20))
            
            # Risk Factors
            story.append(Paragraph("Risk Factors", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            risk_factors = self._generate_risk_factors(timeframe)
            for risk in risk_factors:
                story.append(Paragraph(f"• {risk}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Part IV: Growth Strategy
            story.append(Paragraph("PART IV - STRATEGIC INITIATIVES", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            strategy_data = self._generate_strategic_initiatives_table(data, timeframe)
            story.append(strategy_data)
            story.append(Spacer(1, 20))
            
            # Build the PDF
            doc.build(story)
            logger.info(f"10-K report for {timeframe} generated at {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating 10-K report: {str(e)}")
            raise RuntimeError(f"Failed to generate 10-K report: {str(e)}")
            
    def _generate_business_overview(self, data: Dict[str, Any], timeframe: str) -> str:
        """Generate business overview section."""
        growth_assumptions = GROWTH_ASSUMPTIONS[timeframe]
        
        overview = f"""
        Beauty First Cosmetics (BFC) is a leading cosmetics company operating in multiple segments
        including Cosmetics, Hair, Fragrances, Skin Care, and Beauty Tools. 
        
        Projected Growth:
        • Revenue Growth: {growth_assumptions['revenue_growth_pct'] if timeframe == 'one_year' else growth_assumptions['cumulative_revenue_growth_pct']}%
        • EBITDA Margin Improvement: {growth_assumptions['ebitda_margin_improvement']} percentage points
        • R&D Investment Increase: {growth_assumptions['r_and_d_increase']}%
        
        Key Markets and Segments:
        • Primary Markets: US, UK, Germany, France
        • Emerging Markets: China, Japan
        • Digital Commerce: {DIGITAL_METRICS[timeframe]['e_commerce_share']}% of total sales
        
        Sustainability Targets:
        • Carbon Reduction: {SUSTAINABILITY_TARGETS[timeframe]['carbon_reduction']}%
        • Renewable Energy: {SUSTAINABILITY_TARGETS[timeframe]['renewable_energy']}%
        • Recycled Packaging: {SUSTAINABILITY_TARGETS[timeframe]['recycled_packaging']}%
        """
        return overview
        
    def _generate_financial_data_table(self, data: Dict[str, Any], timeframe: str) -> Table:
        """Generate financial data table."""
        growth = GROWTH_ASSUMPTIONS[timeframe]
        base_revenue = data.get('revenue', 0)
        
        growth_rate = (growth['revenue_growth_pct'] if timeframe == 'one_year' 
                      else growth['cumulative_revenue_growth_pct']) / 100
        
        projected_revenue = base_revenue * (1 + growth_rate)
        projected_ebitda = projected_revenue * (data.get('ebitda_margin', 0) + growth['ebitda_margin_improvement']/100)
        
        financial_data = [
            ['Metric', 'Current', 'Projected', 'Change'],
            ['Revenue ($M)', f"{base_revenue:,.0f}", f"{projected_revenue:,.0f}", 
             f"+{growth['revenue_growth_pct'] if timeframe == 'one_year' else growth['cumulative_revenue_growth_pct']}%"],
            ['EBITDA ($M)', f"{data.get('ebitda', 0):,.0f}", f"{projected_ebitda:,.0f}", 
             f"+{growth['ebitda_margin_improvement']}pts"],
            ['R&D ($M)', f"{data.get('r_and_d_spend', 0):,.0f}", 
             f"{data.get('r_and_d_spend', 0) * (1 + growth['r_and_d_increase']/100):,.0f}", 
             f"+{growth['r_and_d_increase']}%"]
        ]
        
        table = Table(financial_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return table
        
    def _generate_md_and_a(self, data: Dict[str, Any], timeframe: str) -> str:
        """Generate Management Discussion and Analysis section."""
        growth = GROWTH_ASSUMPTIONS[timeframe]
        digital = DIGITAL_METRICS[timeframe]
        
        # Handle different key names for different timeframes
        growth_rate = (growth['revenue_growth_pct'] if timeframe == 'one_year' 
                      else growth['cumulative_revenue_growth_pct'])
        
        analysis = f"""
        Financial Performance and Outlook:
        The company projects revenue growth of {growth_rate}% driven by:
        • Digital transformation with e-commerce reaching {digital['e_commerce_share']}% of sales
        • Geographic expansion in key markets
        • Product innovation and sustainability initiatives
        
        Operational Efficiency:
        • Asset efficiency improvement of {growth['asset_growth_pct']}%
        • Marketing efficiency gains of {growth['marketing_efficiency']}%
        • Supply chain optimization
        
        Capital Structure:
        • Maintained healthy debt-to-equity ratio
        • Strong liquidity position
        • Strategic investments in growth initiatives
        
        Growth Initiatives:
        • R&D investment increase of {growth['r_and_d_increase']}%
        • EBITDA margin improvement target of {growth['ebitda_margin_improvement']} percentage points
        • Marketing efficiency optimization of {growth['marketing_efficiency']}%
        """
        return analysis
        
    def _generate_market_analysis_table(self, data: Dict[str, Any], timeframe: str) -> Table:
        """Generate market analysis table."""
        market_data = MARKET_PENETRATION[timeframe]
        
        rows = [['Market', 'Target Share', 'Brand Awareness', 'Distribution']]
        for market, metrics in market_data.items():
            rows.append([
                market,
                f"{metrics['target_share']}%",
                f"{metrics['brand_awareness']}%",
                f"{metrics['distribution_coverage']}%"
            ])
        
        table = Table(rows, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return table
        
    def _generate_risk_factors(self, timeframe: str) -> List[str]:
        """Generate risk factors based on timeframe."""
        common_risks = [
            "Competitive market pressure and changing consumer preferences",
            "Global economic conditions and currency fluctuations",
            "Supply chain disruptions and raw material costs",
            "Regulatory changes in key markets",
            "Cybersecurity and data privacy risks"
        ]
        
        timeframe_specific_risks = {
            'one_year': [
                "Short-term market volatility",
                "Integration risks from recent acquisitions",
                "Immediate impact of sustainability regulations"
            ],
            'five_year': [
                "Emerging market expansion risks",
                "Technology adoption and digital transformation challenges",
                "Changes in retail landscape"
            ],
            'ten_year': [
                "Long-term sustainability compliance",
                "Demographic shifts in key markets",
                "Disruptive industry innovations"
            ]
        }
        
        return common_risks + timeframe_specific_risks[timeframe]
        
    def _generate_strategic_initiatives_table(self, data: Dict[str, Any], timeframe: str) -> Table:
        """Generate strategic initiatives table."""
        digital = DIGITAL_METRICS[timeframe]
        sustainability = SUSTAINABILITY_TARGETS[timeframe]
        
        initiatives = [
            ['Initiative', 'Target', 'Investment Focus'],
            ['Digital Transformation', f"{digital['e_commerce_share']}% digital sales", 'Technology & Analytics'],
            ['Sustainability', f"{sustainability['carbon_reduction']}% carbon reduction", 'Green Operations'],
            ['Market Expansion', 'Multiple markets', 'Geographic Growth'],
            ['Product Innovation', 'Continuous', 'R&D Investment']
        ]
        
        table = Table(initiatives, colWidths=[2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return table
    
    def _generate_swot_analysis(
        self,
        market_data: Dict[str, Any],
        competitive_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate SWOT analysis based on market and competitive data."""
        return {
            'strengths': [
                'Strong market position',
                'Digital capabilities',
                'Product innovation',
                'Operational efficiency'
            ],
            'weaknesses': [
                'Limited international presence',
                'High marketing costs',
                'Product development cycle'
            ],
            'opportunities': [
                'Digital transformation',
                'International expansion',
                'Sustainability leadership'
            ],
            'threats': [
                'Intense competition',
                'Market volatility',
                'Regulatory changes'
            ]
        }
    
    def _calculate_digital_maturity(self, metrics: Dict[str, Any]) -> float:
        """Calculate digital maturity score."""
        weights = {
            'e_commerce_share': 0.3,
            'mobile_traffic': 0.2,
            'ar_adoption': 0.2,
            'digital_engagement': 0.15,
            'personalization_rate': 0.15
        }
        
        score = sum(
            metrics.get(metric, 0) * weight
            for metric, weight in weights.items()
        )
        
        return min(10, score)
    
    def _generate_digital_roadmap(
        self,
        projections: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate digital transformation roadmap."""
        return [
            {
                'phase': 'Foundation',
                'timeline': '0-6 months',
                'initiatives': [
                    'E-commerce platform upgrade',
                    'Mobile app development',
                    'Digital marketing automation'
                ]
            },
            {
                'phase': 'Innovation',
                'timeline': '6-18 months',
                'initiatives': [
                    'AR implementation',
                    'AI-powered personalization',
                    'Digital supply chain'
                ]
            },
            {
                'phase': 'Optimization',
                'timeline': '18-36 months',
                'initiatives': [
                    'Advanced analytics',
                    'Platform integration',
                    'Digital ecosystem'
                ]
            }
        ]
    
    def _calculate_sustainability_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate sustainability score."""
        weights = {
            'carbon_reduction': 0.3,
            'renewable_energy': 0.25,
            'recycled_packaging': 0.25,
            'water_reduction': 0.2
        }
        
        score = sum(
            metrics.get(metric, 0) * weight
            for metric, weight in weights.items()
        )
        
        return min(10, score)
    
    def _generate_sustainability_timeline(
        self,
        targets: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate sustainability implementation timeline."""
        return [
            {
                'phase': 'Initial',
                'timeline': 'Year 1',
                'targets': [
                    f"{targets['one_year']['carbon_reduction']}% carbon reduction",
                    f"{targets['one_year']['renewable_energy']}% renewable energy",
                    f"{targets['one_year']['recycled_packaging']}% recycled packaging"
                ]
            },
            {
                'phase': 'Intermediate',
                'timeline': 'Years 2-5',
                'targets': [
                    f"{targets['five_year']['carbon_reduction']}% carbon reduction",
                    f"{targets['five_year']['renewable_energy']}% renewable energy",
                    f"{targets['five_year']['recycled_packaging']}% recycled packaging"
                ]
            },
            {
                'phase': 'Advanced',
                'timeline': 'Years 6-10',
                'targets': [
                    f"{targets['ten_year']['carbon_reduction']}% carbon reduction",
                    f"{targets['ten_year']['renewable_energy']}% renewable energy",
                    f"{targets['ten_year']['recycled_packaging']}% recycled packaging"
                ]
            }
        ]
    
    def _generate_industry_comparison_table(self, data: Dict[str, Any], timeframe: str) -> Table:
        """Generate industry comparison table with key metrics."""
        industry_data = [
            ['Metric', 'BFC', 'Industry Average', 'Top Quartile'],
            ['Operating Margin', f"{data.get('operating_margin', 0)*100:.1f}%", "12.5%", "18.2%"],
            ['R&D % Revenue', f"{data.get('r_and_d_spend', 0)/data.get('revenue', 1)*100:.1f}%", "3.8%", "5.5%"],
            ['Digital Sales', f"{DIGITAL_METRICS[timeframe]['e_commerce_share']}%", "25%", "35%"],
            ['Sustainability Score', self._calculate_sustainability_score(SUSTAINABILITY_TARGETS[timeframe]), "6.5", "8.5"]
        ]
        
        table = Table(industry_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return table

    def _generate_detailed_projections(self, data: Dict[str, Any], timeframe: str) -> Table:
        """Generate detailed financial projections table."""
        growth = GROWTH_ASSUMPTIONS[timeframe]
        base_metrics = {
            'revenue': data.get('revenue', 0),
            'ebitda': data.get('ebitda', 0),
            'net_income': data.get('net_income', 0),
            'operating_cash_flow': data.get('ebitda', 0) * 0.8  # Estimated
        }
        
        growth_rate = (growth['revenue_growth_pct'] if timeframe == 'one_year' 
                      else growth['cumulative_revenue_growth_pct']) / 100
        
        projected = {
            'revenue': base_metrics['revenue'] * (1 + growth_rate),
            'ebitda': base_metrics['revenue'] * (1 + growth_rate) * (data.get('ebitda_margin', 0) + growth['ebitda_margin_improvement']/100),
            'net_income': base_metrics['net_income'] * (1 + growth_rate * 1.1),  # Assuming slightly better net income growth
            'operating_cash_flow': base_metrics['operating_cash_flow'] * (1 + growth_rate * 0.9)  # Slightly conservative
        }
        
        projection_data = [
            ['Metric ($M)', 'Current', 'Projected', 'CAGR'],
            ['Revenue', f"{base_metrics['revenue']:,.0f}", f"{projected['revenue']:,.0f}", 
             f"{((projected['revenue']/base_metrics['revenue'])**(1/self._get_years(timeframe))-1)*100:.1f}%"],
            ['EBITDA', f"{base_metrics['ebitda']:,.0f}", f"{projected['ebitda']:,.0f}",
             f"{((projected['ebitda']/base_metrics['ebitda'])**(1/self._get_years(timeframe))-1)*100:.1f}%"],
            ['Net Income', f"{base_metrics['net_income']:,.0f}", f"{projected['net_income']:,.0f}",
             f"{((projected['net_income']/base_metrics['net_income'])**(1/self._get_years(timeframe))-1)*100:.1f}%"],
            ['Op. Cash Flow', f"{base_metrics['operating_cash_flow']:,.0f}", f"{projected['operating_cash_flow']:,.0f}",
             f"{((projected['operating_cash_flow']/base_metrics['operating_cash_flow'])**(1/self._get_years(timeframe))-1)*100:.1f}%"]
        ]
        
        table = Table(projection_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return table
        
    def _get_years(self, timeframe: str) -> int:
        """Get number of years for a timeframe."""
        return {'one_year': 1, 'five_year': 5, 'ten_year': 10}[timeframe]
