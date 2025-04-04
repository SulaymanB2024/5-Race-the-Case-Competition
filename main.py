"""
Main entry point for generating BFC SEC 10-K reports and strategic summary.
"""

from report_generator import generate_one_year_report, generate_five_year_report, generate_ten_year_report
from strategic_summary import get_strategic_summary

def main():
    # Generate each report
    one_year_report = generate_one_year_report()
    five_year_report = generate_five_year_report()
    ten_year_report = generate_ten_year_report()
    
    # Get strategic summary
    strategic_summary = get_strategic_summary()

    # Output reports to the console
    print("========== ONE-YEAR FORWARD 10-K REPORT ==========\n")
    print(one_year_report)
    print("\n========== FIVE-YEAR FORWARD 10-K REPORT ==========\n")
    print(five_year_report)
    print("\n========== TEN-YEAR FORWARD 10-K REPORT ==========\n")
    print(ten_year_report)
    print("\n========== STRATEGIC SUMMARY & RECOMMENDATIONS ==========\n")
    print(strategic_summary)

if __name__ == '__main__':
    main()
