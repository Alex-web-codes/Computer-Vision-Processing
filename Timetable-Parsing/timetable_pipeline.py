import os
import json
import pandas as pd
from pdf_parser import parse_pdf_timetable
from png_parser import parse_png_timetable
from schema_normalizer import normalize_timetable_matrix

def process_timetable_file(file_path, output_dir=None):
    """
    Automatic Timetable Processing Pipeline.
    Accepts PDF or Image timetable file, parses matrix, normalizes JSON, saves JSON & CSV files.
    Returns (normalized_dict, dataframe, json_output_path, csv_output_path).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    base_name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1].lower()

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(file_path) or ".", "output")

    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, f"{base_name}_parsed.json")
    csv_path = os.path.join(output_dir, f"{base_name}_parsed.csv")

    print(f"\n[Pipeline] Processing file: {filename} ({ext.upper()})")

    # Step 1: Extract 2D matrix
    if ext == ".pdf":
        raw_matrix, df = parse_pdf_timetable(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        raw_matrix, df = parse_png_timetable(file_path)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Supported formats: .pdf, .png, .jpg, .jpeg, .bmp, .tiff")

    # Step 2: Normalize matrix to standardized JSON schema
    normalized_json = normalize_timetable_matrix(raw_matrix, filename=filename)

    # Step 3: Write outputs
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(normalized_json, f, indent=2, ensure_ascii=False)

    df.to_csv(csv_path, index=False, encoding="utf-8")

    print(f"[Pipeline Success] Output generated:")
    print(f" - JSON: {json_path}")
    print(f" - CSV:  {csv_path}")

    return normalized_json, df, json_path, csv_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        out_dir = sys.argv[2] if len(sys.argv) > 2 else None
        res, _, j_path, c_path = process_timetable_file(target_file, out_dir)
        print(f"Processed {target_file} -> {j_path}")
    else:
        # Default test run on sample file
        dir_path = os.path.dirname(__file__)
        sample_pdf = os.path.join(dir_path, "7th Sem CSEA.pdf")
        if os.path.exists(sample_pdf):
            process_timetable_file(sample_pdf)
        else:
            print("Usage: python timetable_pipeline.py <path_to_timetable>")
