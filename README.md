# 5-Race-the-Case-Competition# BFC 10-K Reports Generator

This repository contains a modularized Python project to generate hypothetical SEC 10‑K reports for Beauty First Cosmetics (BFC) at one-year, five-year, and ten-year intervals, along with a strategic summary and recommendations.

## Repository Structure

BFC_10K_Reports/ ├── README.md ├── setup.py ├── main.py └── bfc_reports ├── init.py ├── baseline.py ├── config.py ├── report_generator.py ├── strategic_summary.py └── utils.py


## How to Run

1. Ensure you have Python 3 installed.
2. (Optional) Install any requirements if you package this further.
3. Run the main script:

   ```bash
   python main.py

## How to Run

1. Ensure you have Python 3 installed.
2. (Optional) Install any requirements if you package this further.
3. Run the main script:

   ```bash
   python main.py
This will print the three forward-looking 10‑K reports and the strategic summary to the console.

Overview
bfc_reports/config.py contains configuration parameters and baseline assumptions.

bfc_reports/baseline.py provides functions to fetch the baseline financial data.

bfc_reports/report_generator.py builds each 10‑K report.

bfc_reports/strategic_summary.py generates the strategic summary.

bfc_reports/utils.py contains any helper functions.

main.py orchestrates the generation and prints the outputs.

Feel free to modify the assumptions and narrative details in the configuration file as needed.

yaml
Copy

---

#### 2. setup.py

```python
from setuptools import setup, find_packages

setup(
    name='BFC_10K_Reports',
    version='0.1.0',
    packages=find_packages(),
    description='Generate hypothetical forward-looking SEC 10-K reports for Beauty First Cosmetics (BFC)',
    author='Your Name',
    author_email='your.email@example.com',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'bfc10k=main:main',
        ],
    },
)
