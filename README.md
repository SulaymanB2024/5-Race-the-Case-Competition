# Beauty First Cosmetics (BFC) Financial Analysis Tool

A comprehensive financial analysis and strategic planning tool for Beauty First Cosmetics' Race the Case Competition.

## Features

- Financial metrics calculation and analysis
- Market share and growth projections
- Strategic initiative analysis and recommendations
- Digital transformation impact assessment
- Sustainability metrics tracking
- Risk assessment and mitigation strategies
- Competitive analysis and positioning
- Report generation in multiple formats

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the analysis with default settings:
```bash
python main.py
```

Generate specific reports:
```bash
python main.py --reports financial strategic digital sustainability
```

Run with Monte Carlo simulation:
```bash
python main.py --monte-carlo
```

Choose analysis scenario:
```bash
python main.py --scenario optimistic
```

## Project Structure

- `baseline.py`: Baseline financial data and company overview
- `config.py`: Configuration settings and constants
- `main.py`: Main entry point and analysis orchestration
- `output_handler.py`: Output generation and data visualization
- `quantitative_model.py`: Financial metrics and analysis models
- `report_generator.py`: Report generation in various formats
- `strategic_summary.py`: Strategic analysis and recommendations

## Reports Generated

1. Financial Summary
   - Key performance indicators
   - Financial ratios analysis
   - Growth metrics

2. Strategic Analysis
   - Market positioning
   - Competitive analysis
   - SWOT analysis
   - Growth opportunities

3. Digital Transformation
   - Digital maturity assessment
   - Implementation roadmap
   - Technology initiatives
   - ROI projections

4. Sustainability Report
   - Environmental metrics
   - Sustainability targets
   - Implementation timeline
   - Impact assessment

## Configuration

You can customize the analysis by modifying `config.py`:
- Market parameters
- Growth assumptions
- Risk sensitivity
- Digital transformation targets
- Sustainability goals

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
