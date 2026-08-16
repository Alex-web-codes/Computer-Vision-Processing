import sys
import os
import argparse
import pandas as pd

# Import parsers
from pdf_parser import parse_pdf_timetable
from png_parser import parse_png_timetable

def parse_timetable(file_path, output_dir=None):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    ext = os.path.splitext(file_path)[1].lower()
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    if output_dir is None:
        output_dir = os.path.dirname(file_path) or "."
    
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"{base_name}_parsed.json")
    csv_path  = os.path.join(output_dir, f"{base_name}_parsed.csv")

    print("\n" + "=" * 65)
    print(f"         NON-AI TIMETABLE PARSER (File: {os.path.basename(file_path)})")
    print("=" * 65)

    from timetable_pipeline import process_timetable_file
    normalized_json, df, json_path, csv_path = process_timetable_file(file_path, output_dir)
    
    # Build clean display DataFrame from normalized schedule
    schedule = normalized_json.get("schedule", [])
    display_df = pd.DataFrame(schedule) if schedule else df

    print("\n" + "=" * 65)
    print("                      PARSED TIMETABLE TABLE                     ")
    print("=" * 65)
    print(display_df.to_string(index=False))
    print("=" * 65)
    print(f"\n[SUCCESS] Timetable parsed cleanly without AI!")
    print(f"  JSON output: {json_path}")
    print(f"  CSV output:  {csv_path}\n")

    return display_df

def main():
    parser = argparse.ArgumentParser(description="Non-AI Deterministic Timetable Parser (PNG/PDF)")
    parser.add_argument("file_path", help="Path to timetable PNG or PDF file")
    parser.add_argument("--output-dir", "-o", help="Directory to save parsed JSON and CSV outputs", default=None)

    args = parser.parse_args()
    parse_timetable(args.file_path, args.output_dir)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Default test if run without arguments
        dir_path = os.path.dirname(__file__)
        sample_pdf = os.path.join(dir_path, "sample_timetable.pdf")
        sample_png = os.path.join(dir_path, "sample_timetable.png")

        # Auto-generate samples if not present
        if not os.path.exists(sample_pdf) or not os.path.exists(sample_png):
            from generate_sample_data import generate_sample_pdf, generate_sample_png
            generate_sample_pdf(sample_pdf)
            generate_sample_png(sample_png)

        print("Testing PDF parsing...")
        parse_timetable(sample_pdf)

        print("\nTesting PNG image parsing...")
        parse_timetable(sample_png)
    else:
        main()
