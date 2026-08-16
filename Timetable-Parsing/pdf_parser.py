import os
import json
import pdfplumber
import pandas as pd

def parse_pdf_timetable(pdf_path, output_json=None, output_csv=None):
    """
    Non-AI Deterministic PDF Timetable Parser.
    Extracts table structure and text streams using exact vector geometry (pdfplumber).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    print(f"[PDF Parser] Parsing PDF timetable: {pdf_path} (Deterministic Geometry Mode)")

    tables_extracted = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            # Extract tables using pdfplumber line-intersection detection
            page_tables = page.extract_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 3,
                "join_tolerance": 3,
            })

            # Fallback to explicit text/lines if line strategy finds no borders
            if not page_tables:
                page_tables = page.extract_tables()

            for table in page_tables:
                if not table:
                    continue
                
                # Clean up None values and whitespace
                cleaned_table = []
                for row in table:
                    cleaned_row = [cell.strip() if cell else "" for cell in row]
                    cleaned_table.append(cleaned_row)

                tables_extracted.append(cleaned_table)

    if not tables_extracted:
        print("[PDF Parser] Warning: No explicit table boundaries found. Extracting raw text lines...")
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text()
            lines = [line.strip().split() for line in text.split("\n") if line.strip()]
            tables_extracted.append(lines)

    primary_table = tables_extracted[0]
    
    # Convert to pandas DataFrame (assuming 1st row is header)
    if len(primary_table) > 1:
        df = pd.DataFrame(primary_table[1:], columns=primary_table[0])
    else:
        df = pd.DataFrame(primary_table)

    # Save outputs if specified
    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(primary_table, f, indent=2, ensure_ascii=False)
        print(f"  [Saved] JSON timetable output -> {output_json}")

    if output_csv:
        df.to_csv(output_csv, index=False, encoding="utf-8")
        print(f"  [Saved] CSV timetable output  -> {output_csv}")

    return primary_table, df

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        t, df = parse_pdf_timetable(pdf_file, "timetable_output.json", "timetable_output.csv")
        print("\n--- Parsed Timetable Table ---")
        print(df)
    else:
        print("Usage: python pdf_parser.py <path_to_timetable.pdf>")
