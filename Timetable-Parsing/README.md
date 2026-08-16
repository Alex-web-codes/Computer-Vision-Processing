# Automatic Timetable Parsing Pipeline

A deterministic, non-AI timetable extraction engine and REST API service designed to parse academic schedules from vector PDFs and raster images into normalized JSON and CSV structures.

## System Architecture

The pipeline processes input documents through two primary extraction drivers depending on file type:

1. **PDF Vector Stream Engine (`pdf_parser.py`)**:
   Uses `pdfplumber` vector line-intersection detection (`vertical_strategy='lines'`, `horizontal_strategy='lines'`) to reconstruct bounding boxes and extract text directly from the PDF vector stream.

2. **Computer Vision Image Engine (`png_parser.py`)**:
   Applies OpenCV Otsu binarization thresholding and morphological rectangle kernels (`MORPH_OPEN`) to isolate vertical and horizontal grid borders. Bounding box cell contours are sorted into coordinate matrices and passed to PyTesseract OCR (`--psm 6`) for cell text recovery.

3. **Schema Normalization (`schema_normalizer.py`)**:
   - **Cell Span Detection**: Merges 2-hour and 3-hour laboratory or project blocks spanning adjacent table columns.
   - **Room Code Extraction**: Compiled regex pattern matching room identifiers (e.g. `AG02`, `C111`, `C112 DSP Lab`, `BYOD Lab`).
   - **Subject & Faculty Separation**: Heuristic token splitting against domain vocabulary dictionaries.
   - **Time Normalization**: Standardizes raw headers into 12-hour AM/PM time range strings.

4. **REST API & Web UI (`server.py`)**:
   FastAPI web service exposing endpoints for file upload (`/api/upload`), base64 payloads (`/api/parse-base64`), file management (`/api/timetables`), and output downloads (`/api/download/{filename}`). Includes an embedded drag-and-drop HTML5 web dashboard and OpenAPI documentation (`/docs`).

## Directory Structure

```
Timetable-Parsing/
├── server.py                   # FastAPI REST API server & web UI handler
├── timetable_pipeline.py       # Core CLI pipeline controller
├── pdf_parser.py               # Vector PDF table parser (pdfplumber)
├── png_parser.py               # Image grid contour parser (OpenCV + PyTesseract)
├── schema_normalizer.py        # Matrix normalization, room regex, and cell merging
├── test_server.py              # PyTest test suite
├── benchmark_timetables.py     # Execution time & accuracy benchmark script
├── output/                     # Parsed JSON and CSV output files
└── samples/                    # Sample PDF and PNG timetable test files
```

## Quick Start

### 1. Requirements

Install OpenCV, pdfplumber, pytesseract, FastAPI, and uvicorn:

```bash
pip install opencv-python pdfplumber pytesseract pandas fastapi uvicorn pytest
```

### 2. Launch REST API Server

```bash
python server.py
```

Access the interactive Web UI dashboard at `http://127.0.0.1:8000/` or Swagger UI at `http://127.0.0.1:8000/docs`.

### 3. CLI Pipeline Execution

```bash
python timetable_pipeline.py /path/to/timetable.pdf output_dir
```

### 4. Run Test Suite

```bash
pytest test_server.py
```
