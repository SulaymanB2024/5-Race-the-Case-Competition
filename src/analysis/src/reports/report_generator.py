"""
Report generation module focused ONLY on 1, 5, 10-year 10-K style projection reports.
(Version 3 - Refined Structure & Formatting)
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, BaseDocTemplate, Frame, PageTemplate, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# Assuming config is not directly needed here anymore

logger = logging.getLogger(__name__)

# --- Helper function to safely get data ---
def safe_get(data_dict: Dict, key: str, default: Any = None) -> Any:
    """Safely get a value from dictionary, return default if missing."""
    return data_dict.get(key, default)

# --- Helper for formatting numbers ---
def format_currency(value: Any, default_str: str = "N/A") -> str:
    """Formats numeric value as currency string ($M) with 1 decimal."""
    if isinstance(value, (int, float)):
        sign = "-" if value < 0 else ""
        return f"{sign}${abs(value):,.1f}M"
    return default_str

def format_percent(value: Any, decimals: int = 1, default_str: str = "N/A") -> str:
    """Formats numeric value as percentage string (assumes value is already %)."""
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}%"
    if isinstance(value, str) and value.startswith("N/A"): # Pass through specific N/A strings
         return value
    return default_str

def format_percent_from_decimal(value: Any, decimals: int = 1, default_str: str = "N/A") -> str:
    """Formats numeric value (decimal form, e.g., 0.15) as percentage string."""
    if isinstance(value, (int, float)):
         # Ensure value is treated as decimal (e.g., 0.15 -> 15.0%)
         return f"{value * 100.0:.{decimals}f}%"
    return default_str

def format_points(value: Any, decimals: int = 2, default_str: str = "N/A") -> str:
     """Formats numeric value as percentage points (p.p.) with sign."""
     if isinstance(value, (int, float)):
          sign = "+" if value >= 0 else "" # Add + sign for non-negative improvement
          return f"{sign}{value:.{decimals}f} p.p."
     return default_str

# --- Exceptions ---
class ReportGenerationError(Exception):
    """Base exception for report generation errors."""
    pass

class ReportRenderingError(ReportGenerationError):
    """Exception for PDF rendering errors."""
    pass

# --- Refined Report Generator ---
class ReportGenerator:
    """Handles generation of 10-K style projection reports with improved structure."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or './outputs_v3') # Match main.py default
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = self._init_styles()
        self._lock = threading.Lock()
        # Use only 3 workers max, one for each report
        self._executor = ThreadPoolExecutor(max_workers=3)

    def _init_styles(self) -> Dict[str, ParagraphStyle]:
        """Initialize styles used in the reports."""
        styles = getSampleStyleSheet()
        # --- Base Style ---
        styles.add(ParagraphStyle(name='Body', parent=styles['Normal'], fontSize=9, leading=11, spaceAfter=5, alignment=TA_JUSTIFY))
        # --- Titles ---
        styles.add(ParagraphStyle(name='ReportTitle', parent=styles['h1'], alignment=TA_CENTER, fontSize=16, spaceAfter=5, textColor=colors.darkblue))
        styles.add(ParagraphStyle(name='ReportSubTitle', parent=styles['h2'], alignment=TA_CENTER, fontSize=11, spaceAfter=10, textColor=colors.dimgray))
        # --- 10-K Structure Titles ---
        styles.add(ParagraphStyle(name='PartTitle', parent=styles['h2'], fontSize=11, spaceBefore=16, spaceAfter=5, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.black))
        styles.add(ParagraphStyle(name='ItemTitle', parent=styles['h3'], fontSize=10, spaceBefore=10, spaceAfter=3, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.darkslategray))
        styles.add(ParagraphStyle(name='SectionTitle', parent=styles['h4'], fontSize=9, spaceBefore=8, spaceAfter=2, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.darkslategray))
        # --- Tables ---
        styles.add(ParagraphStyle(name='TableTitle', parent=styles['Italic'], alignment=TA_CENTER, fontSize=8, spaceBefore=5, spaceAfter=1))
        styles.add(ParagraphStyle(name='TableHeader', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, fontName='Helvetica-Bold', textColor=colors.white)) # White text on dark header
        styles.add(ParagraphStyle(name='TableCell', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=8))
        styles.add(ParagraphStyle(name='TableCellLeft', parent=styles['Normal'], alignment=TA_LEFT, fontSize=8))
        styles.add(ParagraphStyle(name='TableCellCenter', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8))
        # --- Other ---
        styles.add(ParagraphStyle(name='Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=7, textColor=colors.grey))
        styles.add(ParagraphStyle(name='Disclaimer', parent=styles['Italic'], fontSize=8, spaceBefore=5, spaceAfter=5, alignment=TA_LEFT, textColor=colors.darkred))
        styles.add(ParagraphStyle(name='CustomBullet', parent=styles['Body'], firstLineIndent=0, leftIndent=18, bulletIndent=0, spaceAfter=2)) # Renamed from 'Bullet'
        styles.add(ParagraphStyle(name='BulletBold', parent=styles['CustomBullet'], fontName='Helvetica-Bold')) # Updated parent style

        # --- Table Styles ---
        self.table_style_std = TableStyle([
            # Grid and Borders
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BOX', (0,0), (-1,-1), 1, colors.darkgrey),
            # Header Row
            ('BACKGROUND', (0,0), (-1,0), colors.darkslategray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            # Data Rows
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            ('ALIGN', (0,1), (0,-1), 'LEFT'),
            ('VALIGN', (0,1), (-1,-1), 'TOP'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])
        # Add alternating row colors helper
        for i in range(1, 20): # Apply to first 20 rows
             if i % 2 == 0:
                  bg_color = colors.whitesmoke
             else:
                  bg_color = colors.white
             self.table_style_std.add('BACKGROUND', (0, i), (-1, i), bg_color)


        return styles

    # --- Header/Footer Logic ---
    _current_header_text = "BFC Projection Report"
    _current_timeframe_header = ""

    def _header(self, canvas, doc):
         canvas.saveState()
         header = Paragraph(f"{self._current_header_text} - {self._current_timeframe_header}", self.styles['Normal'])
         w, h = header.wrap(doc.width, doc.topMargin)
         header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h + 10)
         canvas.setStrokeColorRGB(0.7, 0.7, 0.7) # Lighter grey line
         canvas.line(doc.leftMargin, doc.height + doc.topMargin - h + 5, doc.width + doc.leftMargin, doc.height + doc.topMargin - h + 5)
         canvas.restoreState()

    def _footer(self, canvas, doc):
         canvas.saveState()
         footer = Paragraph(f"Page {doc.page} | BFC 10-K Projections (Internal Simulation - Not for Filing)", self.styles['Footer'])
         w, h = footer.wrap(doc.width, doc.bottomMargin)
         footer.drawOn(canvas, doc.leftMargin, h - 10)
         canvas.restoreState()

    def _create_page_template(self, doc, header_text="BFC Projection Report", timeframe=""):
         self._current_header_text = header_text
         self._current_timeframe_header = timeframe
         # Increased frame padding for more white space
         frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal',
                       leftPadding=10, bottomPadding=10, rightPadding=10, topPadding=10)
         template = PageTemplate(id='main', frames=frame,
                                 onPage=self._header, onPageEnd=self._footer)
         return template

    # --- Main Report Generation Method ---
    def generate_10k_reports(self, projection_data: Dict[str, Any]) -> Dict[str, str]:
        """Generates 1, 5, and 10-year 10-K style projection reports in parallel."""
        # (Same parallel execution logic as previous version)
        report_paths = {}
        tasks = {
            timeframe: (projection_data, timeframe)
            for timeframe in ['one_year', 'five_year', 'ten_year']
            if timeframe in projection_data
        }
        if 'baseline' not in projection_data or not tasks:
             logger.error("Invalid projection_data provided to generate_10k_reports.")
             return {}

        with self._executor as executor:
            future_to_timeframe = {
                executor.submit(self._generate_single_10k_report, *args): timeframe
                for timeframe, args in tasks.items()
            }
            for future in future_to_timeframe:
                timeframe = future_to_timeframe[future]
                try:
                    report_paths[timeframe] = future.result()
                except Exception as e:
                    logger.error(f"Report generation failed for timeframe '{timeframe}': {e}", exc_info=True)
                    report_paths[timeframe] = f"FAILED: {type(e).__name__}"

        successful_reports = {k: v for k, v in report_paths.items() if not v.startswith("FAILED:")}
        failed_reports = {k: v for k, v in report_paths.items() if v.startswith("FAILED:")}
        if failed_reports:
             logger.error(f"Some 10-K reports failed: {failed_reports}")
        return successful_reports

    # --- Single Report PDF Builder ---
    def _generate_single_10k_report(self, projection_data: Dict[str, Any], timeframe: str) -> str:
        """Generates the PDF content for a single 10-K report timeframe."""
        output_path = self.output_dir / f"BFC_10K_{timeframe}_Projection_v3.pdf" # Added version
        styles = self.styles
        baseline = projection_data.get('baseline', {})
        projections = projection_data.get(timeframe, {})
        years = {'one_year': 1, 'five_year': 5, 'ten_year': 10}.get(timeframe, 0)
        year_end_approx = 2018 + years
        timeframe_title = timeframe.replace('_',' ').title()

        if not projections:
             raise ReportGenerationError(f"No projection data found for timeframe '{timeframe}'.")

        try:
            doc = BaseDocTemplate(str(output_path), pagesize=letter,
                                  leftMargin=0.75*inch, rightMargin=0.75*inch,
                                  topMargin=1.0*inch, bottomMargin=1.0*inch)
            page_template = self._create_page_template(doc, timeframe=f"{timeframe_title} Projection (~{year_end_approx})")
            doc.addPageTemplates([page_template])

            story = []
            # Build report sections
            story.extend(self._build_report_sections(baseline, projections, timeframe))

            logger.debug(f"Building PDF document for {timeframe}...")
            with self._lock:
                 doc.build(story)

            logger.info(f"Successfully built and saved {timeframe} report PDF to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.exception(f"Critical error occurred during PDF build for {timeframe}: {e}") # Log full trace
            # Attempt cleanup
            if output_path.exists():
                try: output_path.unlink()
                except OSError: logger.error(f"Could not remove broken PDF: {output_path}")
            # Wrap general exceptions
            raise ReportRenderingError(f"Failed building {timeframe} PDF: {str(e)}") from e

    def _build_report_sections(self, baseline: Dict, projections: Dict, timeframe: str) -> List:
        """Builds all sections of the report in order."""
        story = []
        
        # Title Page
        story.append(Paragraph("FORM 10-K - FINANCIAL PROJECTION", self.styles['ReportTitle']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Beauty First Cosmetics (BFC)", self.styles['ReportSubTitle']))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph(f"Projection Horizon: {timeframe.replace('_',' ').title()}", self.styles['ReportSubTitle']))
        story.append(Paragraph(f"(Based on 2018 Baseline - Internal Simulation v3)", self.styles['ReportSubTitle']))
        story.append(PageBreak())

        # Disclaimer
        story.append(Paragraph("Important Disclaimer & Basis of Preparation", self.styles['ItemTitle']))
        disclaimer = f"""
        <b>Disclaimer:</b> This document contains forward-looking statements and financial projections based on internal assumptions and methodologies. It is intended for illustrative and planning purposes only and does not constitute a formal SEC filing or audited financial statement. Actual results may differ materially due to various risks and uncertainties. This document should not be relied upon for investment decisions.
        <br/><br/>
        <b>Basis of Preparation:</b> Projections are derived from the company's 2018 baseline financial data and apply management's growth assumptions for revenue, EBITDA margin improvement, and R&D investment increases specific to the {timeframe.replace('_',' ')} horizon. Net income is projected based on simplified margin assumptions linked to EBITDA margin changes. Calculations do not constitute a full financial model. Key assumptions are detailed within relevant sections.
        """
        story.append(Paragraph(disclaimer, self.styles['Disclaimer']))
        story.append(Spacer(1, 0.2*inch))

        # Part I
        story.append(Paragraph("PART I", self.styles['PartTitle']))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph("Item 1. Business", self.styles['ItemTitle']))
        story.extend(self._build_business_section(baseline, projections, timeframe))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Item 1A. Risk Factors", self.styles['ItemTitle']))
        story.extend(self._build_risk_factors_section(timeframe))
        story.append(PageBreak())

        # Part II
        story.append(Paragraph("PART II", self.styles['PartTitle']))
        story.append(Spacer(1, 0.05*inch))
        story.append(Paragraph("Item 6. Selected Financial Data (Projected)", self.styles['ItemTitle']))
        story.append(KeepTogether(self._build_selected_financial_table(baseline, projections, timeframe)))
        story.append(Spacer(1, 0.1*inch))

        story.append(Paragraph("Item 7. Management's Discussion and Analysis (Projected)", self.styles['ItemTitle']))
        story.extend(self._build_mdna_section(baseline, projections, timeframe))
        story.append(Spacer(1, 0.1*inch))

        return story

    # --- Section Building Methods (Returning Lists of Flowables) ---

    def _build_business_section(self, baseline: Dict, projections: Dict, timeframe: str) -> List:
        """Builds the 'Item 1. Business' content."""
        styles = self.styles
        story = []
        story.append(Paragraph("<u>Company Overview & Projected Strategy</u>", styles['SectionTitle']))
        overview_text = f"""
        Beauty First Cosmetics (BFC) is a significant participant in the global cosmetics sector, offering products across skincare, makeup, fragrance, and hair care. This document outlines projections for the {timeframe.replace('_', ' ')} timeframe, using the 2018 fiscal year as a baseline. The underlying strategy assumes continued focus on core brand equities, investment in product innovation (particularly in high-growth categories and sustainable offerings), expansion of digital capabilities (e-commerce, AR tools), and targeted geographic market development. Operational efficiency improvements are also factored into margin projections.
        """
        story.append(Paragraph(overview_text, styles['Body']))
        story.append(Spacer(1, 0.1*inch))

        # Key Assumptions Table
        story.append(Paragraph("<u>Key Financial Projections & Assumptions</u>", styles['SectionTitle']))
        # Use the refined table style (self.table_style_std)
        # Ensure data passed to Paragraph is string
        highlights_data = [
             [Paragraph(h, styles['TableHeader']) for h in ['Metric', 'Baseline (2018)', f'Projected ({timeframe.replace("_"," ").title()})', 'Implied CAGR (%)']],
             [Paragraph('Revenue', styles['TableCellLeft']),
              Paragraph(format_currency(safe_get(baseline, 'revenue')), styles['TableCell']),
              Paragraph(format_currency(safe_get(projections, 'projected_revenue')), styles['TableCell']),
              Paragraph(format_percent(safe_get(projections, 'revenue_cagr')), styles['TableCellCenter'])],
             [Paragraph('EBITDA', styles['TableCellLeft']),
              Paragraph(format_currency(safe_get(baseline, 'ebitda')), styles['TableCell']),
              Paragraph(format_currency(safe_get(projections, 'projected_ebitda')), styles['TableCell']),
              Paragraph(format_percent(safe_get(projections, 'ebitda_cagr')), styles['TableCellCenter'])],
             [Paragraph('EBITDA Margin', styles['TableCellLeft']),
              Paragraph(format_percent_from_decimal(safe_get(baseline, 'ebitda_margin',0)), styles['TableCell']),
              Paragraph(format_percent_from_decimal(safe_get(projections, 'projected_ebitda_margin',0)), styles['TableCell']),
              Paragraph(" ", styles['TableCellCenter'])],
             [Paragraph('Net Income', styles['TableCellLeft']), # Added Net Income
              Paragraph(format_currency(safe_get(baseline, 'net_income')), styles['TableCell']),
              Paragraph(format_currency(safe_get(projections, 'projected_net_income')), styles['TableCell']),
              Paragraph(format_percent(safe_get(projections, 'net_income_cagr')), styles['TableCellCenter'])],
             [Paragraph('R&D Spend', styles['TableCellLeft']),
              Paragraph(format_currency(safe_get(baseline, 'r_and_d_spend')), styles['TableCell']),
              Paragraph(format_currency(safe_get(projections, 'projected_r_and_d_spend')), styles['TableCell']),
              Paragraph(format_percent(safe_get(projections, 'rnd_cagr')), styles['TableCellCenter'])],
        ]
        highlights_table = Table(highlights_data, colWidths=[1.8*inch, 1.6*inch, 1.6*inch, 1.5*inch])
        highlights_table.setStyle(self.table_style_std) # Apply the refined style
        story.append(KeepTogether(highlights_table)) # Wrap in KeepTogether
        return story


    def _build_selected_financial_table(self, baseline: Dict, projections: Dict, timeframe: str) -> Table:
        styles = self.styles
        years = {'one_year': 1, 'five_year': 5, 'ten_year': 10}.get(timeframe, 0)
        
        # Create data with Paragraph objects for each cell
        data = [
            [Paragraph(cell, styles['TableHeader']) for cell in 
             ['Metric', 'Baseline (2018)', f'Projected (~{2018+years})', f'CAGR ({years}yr)']],
        ]
        
        # Add data rows with proper cell formatting
        for metric, base_key, proj_key, cagr_key in [
            ('Revenue', 'revenue', 'projected_revenue', 'revenue_cagr'),
            ('EBITDA', 'ebitda', 'projected_ebitda', 'ebitda_cagr'),
            ('Net Income', 'net_income', 'projected_net_income', 'net_income_cagr')
        ]:
            row = [
                Paragraph(metric, styles['TableCellLeft']),
                Paragraph(format_currency(safe_get(baseline, base_key)), styles['TableCell']),
                Paragraph(format_currency(safe_get(projections, proj_key)), styles['TableCell']),
                Paragraph(format_percent(safe_get(projections, cagr_key)), styles['TableCellCenter'])
            ]
            data.append(row)

        # Create table with fixed column widths
        table = Table(data, colWidths=[2.0*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        
        # Basic table style
        style = TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.darkslategray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ])
        table.setStyle(style)
        return table


    def _build_mdna_section(self, baseline: Dict, projections: Dict, timeframe: str) -> List:
        """Builds the 'Item 7. MD&A' projection content (list of flowables)."""
        styles = self.styles
        story = []
        # Extract key values using helpers for formatting
        proj_rev = format_currency(safe_get(projections, 'projected_revenue'))
        revenue_cagr = format_percent(safe_get(projections, 'revenue_cagr'))
        proj_ebitda = format_currency(safe_get(projections, 'projected_ebitda'))
        proj_ebitda_margin = format_percent_from_decimal(safe_get(projections, 'projected_ebitda_margin', 0))
        ebitda_cagr = format_percent(safe_get(projections, 'ebitda_cagr'))
        proj_net_income = format_currency(safe_get(projections, 'projected_net_income'))
        net_income_cagr = format_percent(safe_get(projections, 'net_income_cagr'))
        proj_rnd = format_currency(safe_get(projections, 'projected_r_and_d_spend'))
        base_rnd = format_currency(safe_get(baseline, 'r_and_d_spend'))
        rnd_cagr = format_percent(safe_get(projections, 'rnd_cagr'))

        # --- Introduction ---
        story.append(Paragraph("<u>Introduction and Basis of Projection</u>", styles['SectionTitle']))
        intro_text = f"""
        This MD&A discusses projected financial trends for BFC over the {timeframe.replace('_', ' ')} horizon, based on 2018 baseline data and specified growth assumptions. These projections are illustrative, forward-looking, and subject to risks. They do not represent formal guidance or audited forecasts. Key assumptions involve revenue growth (driven by market factors and strategic initiatives), targeted improvements in EBITDA margin through operational leverage and efficiency, and increased R&D investment to foster innovation.
        """
        story.append(Paragraph(intro_text, styles['Body']))
        story.append(Spacer(1, 0.1*inch))

        # --- Projected Results with CAGR Commentary ---
        story.append(Paragraph("<u>Projected Financial Performance</u>", styles['SectionTitle']))
        results_text = f"""
        <b>Revenue:</b> Projected to reach {proj_rev}, representing an implied CAGR of {revenue_cagr}. Achieving this growth depends on factors like successful product launches, effective marketing, digital channel performance, and overall market conditions.
        <br/><br/>
        <b>Profitability:</b> EBITDA is projected at {proj_ebitda} with an anticipated margin of {proj_ebitda_margin}. The implied EBITDA CAGR is {ebitda_cagr}. Net Income is projected at {proj_net_income} (CAGR: {net_income_cagr}). The profitability outlook relies on realizing revenue growth, managing cost inflation (COGS, operating expenses), and achieving assumed margin improvements. The projected {net_income_cagr} CAGR for Net Income relative to the {revenue_cagr} CAGR for Revenue suggests an assumption of margin expansion contributing to bottom-line growth.
        """
        story.append(Paragraph(results_text, styles['Body']))
        story.append(Spacer(1, 0.1*inch))

        # --- Key Activities & Investments ---
        story.append(Paragraph("<u>Projected Investments and Activities</u>", styles['SectionTitle']))
        investment_text = f"""
        <b>Research & Development:</b> R&D spending is projected to increase from a baseline of {base_rnd} to {proj_rnd} (CAGR: {rnd_cagr}). This reflects a strategic priority to invest in innovation related to product efficacy, sustainability, and technology integration (e.g., AR/AI applications in beauty).
        <br/><br/>
        <b>Operational Focus:</b> Assumptions include ongoing efforts to optimize the supply chain, enhance digital capabilities for e-commerce and customer engagement, and manage operating expenses effectively to support margin improvement targets. Specific capital expenditure plans are not detailed in this simulation but are assumed to support growth initiatives.
        """
        story.append(Paragraph(investment_text, styles['Body']))
        story.append(Spacer(1, 0.1*inch))

        # --- Liquidity & Capital Resources Outlook ---
        story.append(Paragraph("<u>Projected Liquidity and Capital Resources</u>", styles['SectionTitle']))
        liquidity_text = """
        The projections assume sufficient liquidity will be generated from operations to fund planned investments. Existing capital structure and access to credit markets are assumed stable. Significant deviations in operating cash flow or unforeseen capital needs could impact this outlook. (Detailed cash flow statement projections are not included).
        """
        story.append(Paragraph(liquidity_text, styles['Body']))

        return story


    def _build_risk_factors_section(self, timeframe: str) -> List:
        """Builds the 'Item 1A. Risk Factors' content (list of flowables)."""
        styles = self.styles
        story = []
        story.append(Paragraph("Achieving the financial projections outlined in this document is subject to various significant risks and uncertainties. If these risks materialize, actual results could differ materially from projections. Key risk categories include:", styles['Body']))
        story.append(Spacer(1, 0.05*inch))

        # Using Paragraphs with embedded bold tags for subheadings
        risk_categories = {
            "<b>Market & Competition Risks:</b>": [
                "Shifts in consumer preferences, beauty trends, or spending power.",
                "Intensified competition from established global players and emerging/niche brands, potentially leading to price pressures or market share erosion.",
                "Failure to adapt to evolving retail channels (e.g., D2C, social commerce, traditional retail dynamics)."
            ],
            "<b>Operational & Supply Chain Risks:</b>": [
                "Disruptions in sourcing key raw materials or packaging components.",
                "Manufacturing capacity constraints or quality control issues.",
                "Logistics and transportation challenges impacting cost and delivery.",
                "Cybersecurity incidents affecting operations, customer data, or intellectual property."
            ],
            "<b>Macroeconomic & Geopolitical Risks:</b>": [
                "Global or regional economic downturns impacting consumer demand.",
                "Persistent inflation affecting input costs and consumer prices.",
                "Significant adverse fluctuations in foreign currency exchange rates.",
                "Changes in international trade regulations, tariffs, or geopolitical instability in key markets."
            ],
            "<b>Strategic & Execution Risks:</b>": [
                "Inability to successfully develop and launch innovative, commercially viable products.",
                "Ineffective marketing campaigns or damage to brand reputation.",
                "Challenges in implementing digital transformation initiatives or integrating new technologies.",
                "Difficulties in attracting and retaining key talent."
             ],
             "<b>Regulatory & Compliance Risks:</b>": [
                "Changes in regulations regarding cosmetic ingredients, safety testing, advertising standards, or environmental compliance.",
                "Increased scrutiny or regulations related to data privacy and protection."
             ]
        }
        # Add timeframe specific nuances if desired
        if timeframe in ['five_year', 'ten_year']:
            risk_categories["<b>Longer-Term & Emerging Risks:</b>"] = [
                "Fundamental shifts in technology impacting product development or customer interaction.",
                "Significant demographic changes affecting target consumer groups.",
                f"Challenges in meeting ambitious long-term ({timeframe.replace('_',' ')}) sustainability goals.",
                "Impact of climate change on supply chains or consumer behavior."
            ]

        for category_title, risks in risk_categories.items():
             story.append(Paragraph(category_title, styles['SectionTitle'])) # Use SectionTitle for category
             for risk in risks:
                  story.append(Paragraph(f"• {risk}", styles['CustomBullet']))
             story.append(Spacer(1, 0.05*inch))

        return story


    # --- Context Manager Methods ---
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
             # Ensure shutdown happens cleanly
             try:
                  self._executor.shutdown(wait=True, cancel_futures=False) # Allow completing futures
             except Exception as e:
                  logger.error(f"Error shutting down thread pool executor: {e}")