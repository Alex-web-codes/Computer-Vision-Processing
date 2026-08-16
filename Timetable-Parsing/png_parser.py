import os
import json
import numpy as np
import pandas as pd

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

def parse_png_timetable(png_path, output_json=None, output_csv=None, tesseract_cmd=None):
    """
    Non-AI Computer Vision PNG Timetable Grid Parser.
    Uses OpenCV Canny/Morphological line detection to crop grid cells geometrically.
    """
    if not os.path.exists(png_path):
        raise FileNotFoundError(f"PNG file not found: {png_path}")

    if cv2 is None:
        raise ImportError("opencv-python (cv2) is required for PNG grid detection. Install with: pip install opencv-python")

    if tesseract_cmd and pytesseract:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    print(f"[PNG Parser] Parsing Image timetable: {png_path} (OpenCV Computer Vision Grid Mode)")

    # Read image
    img = cv2.imread(png_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold image (Otsu binarization)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Detect horizontal lines
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (max(1, img.shape[1] // 30), 1))
    horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_h)

    # Detect vertical lines
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(1, img.shape[0] // 30)))
    vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_v)

    # Combine grid lines
    table_grid = cv2.add(horizontal, vertical)

    # Find cell contours
    contours, _ = cv2.findContours(table_grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    min_w, min_h = 30, 15
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > min_w and h > min_h and w < img.shape[1] * 0.95 and h < img.shape[0] * 0.95:
            boxes.append((x, y, w, h))

    if not boxes:
        print("[PNG Parser] Warning: Could not isolate explicit grid border lines. Falling back to whole image.")
        boxes = [(0, 0, img.shape[1], img.shape[0])]

    # Group boxes into rows based on y coordinate tolerance
    boxes = sorted(boxes, key=lambda b: b[1])

    rows = []
    current_row = []
    prev_y = None

    for box in boxes:
        x, y, w, h = box
        if prev_y is None or abs(y - prev_y) < 18:
            current_row.append(box)
        else:
            current_row = sorted(current_row, key=lambda b: b[0])
            rows.append(current_row)
            current_row = [box]
        prev_y = y

    if current_row:
        current_row = sorted(current_row, key=lambda b: b[0])
        rows.append(current_row)

    # Extract text from each cell box using OCR
    table_matrix = []
    for r_idx, row in enumerate(rows):
        row_text = []
        for c_idx, (x, y, w, h) in enumerate(row):
            cell_crop = gray[y:y+h, x:x+w]
            cell_str = ""
            if pytesseract:
                try:
                    cell_str = pytesseract.image_to_string(cell_crop, config="--psm 6").strip()
                    cell_str = cell_str.replace("\n", " ")
                except Exception:
                    cell_str = f"Cell({r_idx},{c_idx})"
            else:
                cell_str = f"Cell({r_idx},{c_idx})"
            row_text.append(cell_str)
        table_matrix.append(row_text)

    # Format into DataFrame safely handling variable column lengths
    max_cols = max(len(r) for r in table_matrix) if table_matrix else 0
    padded_matrix = [r + [""] * (max_cols - len(r)) for r in table_matrix]

    if len(padded_matrix) > 1:
        headers = [h if h else f"Col_{i+1}" for i, h in enumerate(padded_matrix[0])]
        df = pd.DataFrame(padded_matrix[1:], columns=headers)
    else:
        df = pd.DataFrame(padded_matrix)

    # Save outputs if requested
    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(table_matrix, f, indent=2, ensure_ascii=False)
        print(f"  [Saved] JSON timetable output -> {output_json}")

    if output_csv:
        df.to_csv(output_csv, index=False, encoding="utf-8")
        print(f"  [Saved] CSV timetable output  -> {output_csv}")

    return table_matrix, df

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        png_file = sys.argv[1]
        t, df = parse_png_timetable(png_file, "timetable_output.json", "timetable_output.csv")
        print("\n--- Parsed PNG Timetable Table ---")
        print(df)
    else:
        print("Usage: python png_parser.py <path_to_timetable.png>")
