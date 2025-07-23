from flask import Flask, render_template, request, jsonify
import pdfplumber
import re
import os

app = Flask(__name__)


class RankAnalyzer:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_merit_data(self, target_merit_no):
        """
        Extract data from PDF up to the target merit number and count EWS candidates
        """
        ews_count = 0
        found_target = False
        candidates_data = []
        last_merit_no = 0

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"Processing PDF with {len(pdf.pages)} pages...")

                for page_num, page in enumerate(pdf.pages):
                    if found_target:
                        break

                    print(f"Processing page {page_num + 1}...")

                    # Try to extract table first
                    tables = page.extract_tables()

                    if tables:
                        # Process table data
                        for table in tables:
                            for row in table:
                                if found_target:
                                    break

                                if not row or len(row) < 5:
                                    continue

                                # Try to parse the first cell as merit number
                                try:
                                    merit_cell = str(row[0]).strip() if row[0] else ""
                                    merit_match = re.search(r"(\d+)", merit_cell)

                                    if not merit_match:
                                        continue

                                    merit_no = int(merit_match.group(1))

                                    # Skip if merit number is not in ascending order (likely header or invalid)
                                    if merit_no <= last_merit_no and merit_no < 100:
                                        continue

                                    # Look for EWS status in the row - ONLY check column 6 (EWS column)
                                    ews_status = "-"
                                    if (
                                        len(row) > 6
                                        and row[6]
                                        and str(row[6]).strip().upper()
                                        in ["YES", "YES@"]
                                    ):
                                        ews_status = "Yes"

                                    candidate_data = {
                                        "merit_no": merit_no,
                                        "ews_status": ews_status,
                                        "raw_row": row,
                                    }

                                    candidates_data.append(candidate_data)
                                    last_merit_no = merit_no

                                    # Count EWS candidates
                                    if ews_status.upper() == "YES":
                                        ews_count += 1

                                    # Check if we've reached the target merit number
                                    if merit_no >= target_merit_no:
                                        found_target = True
                                        break

                                except (ValueError, IndexError):
                                    continue

                    # If no tables found or table extraction didn't work, fall back to text extraction
                    if not tables or not candidates_data:
                        text = page.extract_text()
                        if not text:
                            continue

                        lines = text.split("\n")

                        for line in lines:
                            if found_target:
                                break

                            # Skip header lines and empty lines
                            if (
                                not line.strip()
                                or "Merit" in line
                                or "Application" in line
                                or "Candidate" in line
                                or "Category" in line
                                or len(line.strip()) < 10
                            ):
                                continue

                            candidate_data = self.parse_candidate_line(line)

                            if candidate_data:
                                merit_no = candidate_data["merit_no"]
                                ews_status = candidate_data["ews_status"]

                                # Skip if merit number is not in ascending order (likely invalid)
                                if merit_no <= last_merit_no and merit_no < 100:
                                    continue

                                candidates_data.append(candidate_data)
                                last_merit_no = merit_no

                                # Count EWS candidates
                                if ews_status.upper() == "YES":
                                    ews_count += 1

                                # Check if we've reached the target merit number
                                if merit_no >= target_merit_no:
                                    found_target = True
                                    break

        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return None, str(e)

        if not found_target:
            return (
                None,
                f"Merit number {target_merit_no} not found in the PDF. Last merit number processed: {last_merit_no}",
            )

        print(
            f"Found {len(candidates_data)} candidates, {ews_count} EWS candidates up to merit rank {target_merit_no}"
        )
        return ews_count, None

    def parse_candidate_line(self, line):
        """
        Parse a line from the PDF to extract candidate information
        Based on the structure visible in the image:
        Merit No | Application ID | Name | Category | Gender | PWD/Def | EWS | TFWS | Orphan | ... etc
        """
        try:
            # Clean the line
            line = line.strip()
            if not line:
                return None

            # Split the line by multiple spaces or tabs to handle table structure
            parts = re.split(r"\s{2,}|\t+", line)

            # If that doesn't work well, try splitting by single spaces
            if len(parts) < 5:
                parts = line.split()

            if len(parts) < 5:  # Minimum expected columns
                return None

            # Try to extract merit number from the first part
            merit_no_str = parts[0].strip()

            # Handle cases where merit number might have extra characters
            merit_match = re.search(r"(\d+)", merit_no_str)
            if not merit_match:
                return None

            merit_no = int(merit_match.group(1))

            # Look for EWS status - ONLY check the EWS column (position 6)
            ews_status = "-"

            # Based on the PDF structure:
            # Columns: Merit No, App ID, Name, Category, Gender, PWD/Def, EWS, TFWS, Orphan...
            # EWS is at index 6 (0-based)

            # Method 1: Check specific EWS position (index 6)
            if len(parts) > 6 and parts[6].strip().upper() in ["YES", "YES@"]:
                ews_status = "Yes"

            # Method 2: If parts are not well-separated, try to find the EWS column by position
            elif len(parts) <= 6:
                # Fall back to searching, but be more restrictive
                # Look for "Yes" or "Yes@" in reasonable EWS position (around 6th-8th position)
                line_parts = line.split()
                if len(line_parts) > 6:
                    # Check positions that could be EWS column (6-8)
                    for i in range(6, min(9, len(line_parts))):
                        if line_parts[i].upper() in ["YES", "YES@"]:
                            # Additional check: make sure this isn't a percentage or other value
                            if not any(
                                char in line_parts[i] for char in [".", "%", "/"]
                            ):
                                ews_status = "Yes"
                                break

            return {
                "merit_no": merit_no,
                "ews_status": ews_status,
                "raw_line": line,
                "parsed_parts": parts,
            }

        except (ValueError, IndexError) as e:
            # Skip lines that don't match expected format
            return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_rank():
    try:
        merit_rank = int(request.form["merit_rank"])

        if merit_rank <= 0:
            return (
                jsonify({"error": "Please enter a valid merit rank (positive number)"}),
                400,
            )

        # Check if PDF exists
        pdf_path = "merit-ranks.pdf"
        if not os.path.exists(pdf_path):
            return jsonify({"error": "Merit ranks PDF file not found"}), 404

        # Analyze the PDF
        analyzer = RankAnalyzer(pdf_path)
        ews_rank, error = analyzer.extract_merit_data(merit_rank)

        if error:
            return jsonify({"error": error}), 400

        return jsonify(
            {
                "merit_rank": merit_rank,
                "ews_rank": ews_rank,
                "message": f"Your EWS rank is {ews_rank} (out of candidates up to merit rank {merit_rank})",
            }
        )

    except ValueError:
        return jsonify({"error": "Please enter a valid number for merit rank"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
