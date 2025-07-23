#!/usr/bin/env python3
"""
Test script to verify PDF parsing functionality
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import RankAnalyzer
import pdfplumber
import re


def print_pdf_rows(analyzer):
    """Print actual rows from the PDF to see the structure"""
    print("\n📄 Printing actual PDF rows for inspection:")
    print("=" * 80)

    ews_found = 0
    tfws_found = 0

    try:
        with pdfplumber.open(analyzer.pdf_path) as pdf:
            # Look at more pages to find EWS candidates
            rows_checked = 0
            for page_num in range(min(20, len(pdf.pages))):
                if rows_checked >= 100:  # Check first 100 candidates
                    break

                page = pdf.pages[page_num]

                # Try table extraction first
                tables = page.extract_tables()
                if tables:
                    table = tables[0]  # Look at first table

                    # Print rows, looking for EWS candidates
                    for i, row in enumerate(table):
                        if row and row[0] and str(row[0]).strip().isdigit():
                            rows_checked += 1
                            merit_no = int(row[0])

                            # Check specific columns
                            ews_status = (
                                row[6] if len(row) > 6 else ""
                            )  # EWS is column 6
                            tfws_status = (
                                row[7] if len(row) > 7 else ""
                            )  # TFWS is column 7

                            # Count different types
                            if ews_status and str(ews_status).strip().upper() == "YES":
                                ews_found += 1
                                print(
                                    f"🎯 EWS CANDIDATE #{ews_found}: Merit {merit_no} | EWS='{ews_status}' | TFWS='{tfws_status}'"
                                )

                            if (
                                tfws_status
                                and str(tfws_status).strip().upper() == "YES"
                            ):
                                tfws_found += 1
                                if tfws_found <= 5:  # Show first 5 TFWS candidates
                                    print(
                                        f"📚 TFWS CANDIDATE #{tfws_found}: Merit {merit_no} | EWS='{ews_status}' | TFWS='{tfws_status}'"
                                    )

                            # Show structure for first few rows
                            if rows_checked <= 5:
                                print(
                                    f"Merit {merit_no}: EWS='{ews_status}' | TFWS='{tfws_status}' | Columns 0-9: {row[:10]}"
                                )

                            if rows_checked >= 100:
                                break

    except Exception as e:
        print(f"Error reading PDF: {e}")

    print("=" * 80)
    print(f"📊 SUMMARY after checking {rows_checked} candidates:")
    print(f"   EWS candidates found: {ews_found}")
    print(f"   TFWS candidates found: {tfws_found}")
    print("=" * 80)


def test_pdf_parsing():
    """Test the PDF parsing with a sample merit number"""

    pdf_path = "merit-ranks.pdf"
    if not os.path.exists(pdf_path):
        print("❌ merit-ranks.pdf not found!")
        return False

    print("🔍 Testing PDF parsing...")
    analyzer = RankAnalyzer(pdf_path)

    # First, let's print some actual rows from the PDF to see the structure
    print_pdf_rows(analyzer)

    # Test with a small merit number first
    test_merit_no = 50
    print(f"Testing with merit number: {test_merit_no}")

    try:
        ews_count, error = analyzer.extract_merit_data(test_merit_no)

        if error:
            print(f"❌ Error: {error}")
            return False

        print(
            f"✅ Success! Found {ews_count} EWS candidates up to merit rank {test_merit_no}"
        )
        return True

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False


def test_line_parsing():
    """Test individual line parsing"""

    # Sample lines based on the PDF structure shown in the image
    sample_lines = [
        "1 EN24133045 SAKSOHKAR SHARANYA Open Female -/- MHT-CET-PCM 100.0000000 100.0000000 100.0000000 100.0000000 77.00 77.00 78.00 77.80 83.00 85.00 84.00 80.00",
        "2 EN24234277 DIWAN PRERANA SUNIL Open Female -/- MHT-CET-PCM 100.0000000 100.0000000 100.0000000 100.0000000 63.00 65.00 50.00 69.33 84.80 70.00 92.00 95.00",
        "10 EN24138003 DHURE ARYAN DATTATRAY OBC Male Yes -/- MHT-CET-PCM 100.0000000 99.9850903 99.9382100 100.0000000 75.00 78.00 65.00 72.00 72.00 59.00 57.00 75.00",
    ]

    analyzer = RankAnalyzer("merit-ranks.pdf")

    print("\n🧪 Testing line parsing...")
    for i, line in enumerate(sample_lines, 1):
        print(f"\nTesting line {i}:")
        print(f"Input: {line[:100]}...")

        result = analyzer.parse_candidate_line(line)
        if result:
            print(f"✅ Merit No: {result['merit_no']}, EWS: {result['ews_status']}")
        else:
            print("❌ Failed to parse")


if __name__ == "__main__":
    print("🎓 EWS Rank Analyzer - Test Suite")
    print("=" * 50)

    # Test line parsing first
    test_line_parsing()

    # Test PDF parsing
    print("\n" + "=" * 50)
    success = test_pdf_parsing()

    if success:
        print("\n🎉 All tests passed! The application should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the PDF format and parsing logic.")
