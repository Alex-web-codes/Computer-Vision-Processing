import os
import json
import base64
import uuid
import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from timetable_pipeline import process_timetable_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(
    title="Automatic Timetable Parsing Pipeline API",
    description="REST API service for uploading PDF/Image timetables, automatically parsing grid structures, and generating standardized JSON & CSV files.",
    version="1.0.0"
)

# Enable CORS for cross-origin frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Base64ParseRequest(BaseModel):
    filename: str
    base64_data: str

@app.post("/api/upload", summary="Upload and Parse Timetable File")
async def upload_and_parse(file: UploadFile = File(...)):
    """
    Upload a timetable document (.pdf, .png, .jpg, .jpeg) to automatically parse and generate JSON & CSV.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format '{ext}'. Supported formats: .pdf, .png, .jpg, .jpeg, .bmp, .tiff"
        )

    # Unique upload path to prevent overwrites
    file_id = uuid.uuid4().hex[:8]
    safe_filename = f"{file_id}_{file.filename}"
    upload_path = os.path.join(UPLOADS_DIR, safe_filename)

    with open(upload_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        normalized_json, df, json_path, csv_path = process_timetable_file(upload_path, output_dir=OUTPUT_DIR)
        
        json_filename = os.path.basename(json_path)
        csv_filename = os.path.basename(csv_path)

        return {
            "status": "success",
            "message": "Timetable uploaded and parsed successfully",
            "download_urls": {
                "json": f"/api/download/{json_filename}",
                "csv": f"/api/download/{csv_filename}"
            },
            "view_url": f"/api/view/{json_filename}",
            "data": normalized_json
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")

@app.post("/api/parse-base64", summary="Parse Base64 Encoded Timetable File")
async def parse_base64(payload: Base64ParseRequest):
    """
    Parse a base64 encoded timetable image/PDF string directly.
    """
    try:
        file_bytes = base64.b64decode(payload.base64_data)
        file_id = uuid.uuid4().hex[:8]
        safe_filename = f"{file_id}_{payload.filename}"
        upload_path = os.path.join(UPLOADS_DIR, safe_filename)

        with open(upload_path, "wb") as f:
            f.write(file_bytes)

        normalized_json, df, json_path, csv_path = process_timetable_file(upload_path, output_dir=OUTPUT_DIR)
        
        return {
            "status": "success",
            "download_urls": {
                "json": f"/api/download/{os.path.basename(json_path)}",
                "csv": f"/api/download/{os.path.basename(csv_path)}"
            },
            "data": normalized_json
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode or parse base64 payload: {str(e)}")

@app.get("/api/timetables", summary="List All Generated Parsed Files")
async def list_timetables():
    """
    Get a list of all parsed JSON & CSV files currently available in the output directory.
    """
    files = []
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".json"):
                f_path = os.path.join(OUTPUT_DIR, f)
                stat = os.stat(f_path)
                files.append({
                    "filename": f,
                    "size_bytes": stat.st_size,
                    "created_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "download_url": f"/api/download/{f}",
                    "view_url": f"/api/view/{f}"
                })
    return {"total": len(files), "files": files}

@app.get("/api/view/{filename}", summary="View Parsed JSON Data")
async def view_json(filename: str):
    """
    Retrieve full parsed JSON content for a specific generated file.
    """
    json_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(json_path) or not filename.endswith(".json"):
        raise HTTPException(status_code=404, detail="File not found")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

@app.get("/api/download/{filename}", summary="Download JSON/CSV Output File")
async def download_file(filename: str):
    """
    Download generated JSON or CSV file by name.
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested output file not found")

    media_type = "application/json" if filename.endswith(".json") else "text/csv"
    return FileResponse(file_path, filename=filename, media_type=media_type)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_web_ui():
    """
    Embedded Web Dashboard for testing timetable upload & viewing JSON pipeline output.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📅 Timetable Parser Pipeline API</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b0f19;
            --surface: #141a29;
            --surface-hover: #1b2438;
            --border: #26334d;
            --primary: #3b82f6;
            --primary-glow: rgba(59, 130, 246, 0.15);
            --accent: #10b981;
            --text: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --radius: 12px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
            padding: 2rem 1.5rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            margin-bottom: 2.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
        }

        .brand h1 {
            font-size: 1.8rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            letter-spacing: -0.02em;
        }

        .brand p {
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 0.2rem;
        }

        .docs-badge {
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--primary);
            padding: 0.5rem 1rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.875rem;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .docs-badge:hover {
            background: var(--primary-glow);
            border-color: var(--primary);
        }

        .grid-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }

        @media (max-width: 900px) {
            .grid-layout {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text);
        }

        .dropzone {
            border: 2px dashed var(--border);
            border-radius: var(--radius);
            padding: 3rem 1.5rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            background: rgba(15, 23, 42, 0.4);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
        }

        .dropzone:hover, .dropzone.dragover {
            border-color: var(--primary);
            background: var(--primary-glow);
        }

        .dropzone-icon {
            font-size: 2.5rem;
        }

        .dropzone-text h3 {
            font-size: 1rem;
            font-weight: 600;
        }

        .dropzone-text p {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
        }

        .file-input {
            display: none;
        }

        .btn {
            background: var(--primary);
            color: #fff;
            border: none;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.2s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            text-decoration: none;
        }

        .btn:hover {
            opacity: 0.9;
        }

        .btn-accent {
            background: var(--accent);
        }

        .btn-secondary {
            background: var(--surface-hover);
            color: var(--text);
            border: 1px solid var(--border);
        }

        .status-box {
            margin-top: 1rem;
            padding: 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            display: none;
        }

        .status-box.loading {
            display: block;
            background: var(--primary-glow);
            border: 1px solid var(--primary);
            color: var(--text);
        }

        .status-box.success {
            display: block;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--accent);
            color: var(--text);
        }

        .status-box.error {
            display: block;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid #ef4444;
            color: #fca5a5;
        }

        .json-viewer {
            background: #070a12;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            color: #a7f3d0;
            overflow-x: auto;
            max-height: 480px;
            white-space: pre-wrap;
            word-break: break-all;
        }

        .actions-bar {
            display: flex;
            gap: 0.75rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }

        .meta-tag {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: var(--surface-hover);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .table-preview {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            font-size: 0.85rem;
        }

        .table-preview th, .table-preview td {
            border: 1px solid var(--border);
            padding: 0.5rem 0.75rem;
            text-align: left;
        }

        .table-preview th {
            background: var(--surface-hover);
            color: var(--text-secondary);
            font-weight: 600;
        }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <h1>📅 Automatic Timetable Parser</h1>
                <p>Non-AI Deterministic Upload Pipeline & JSON Generator</p>
            </div>
            <a href="/docs" target="_blank" class="docs-badge">⚡ OpenAPI / Swagger Docs</a>
        </header>

        <div class="grid-layout">
            <!-- Left Column: Upload Card -->
            <div class="card">
                <div class="card-title">
                    <span>📤 Upload Timetable</span>
                </div>
                
                <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
                    <div class="dropzone-icon">📄</div>
                    <div class="dropzone-text">
                        <h3>Click to upload or drag & drop file</h3>
                        <p>Supports PDF (.pdf) and Image files (.png, .jpg, .jpeg)</p>
                    </div>
                    <input type="file" id="fileInput" class="file-input" accept=".pdf,.png,.jpg,.jpeg,.bmp,.tiff" onchange="handleFileSelect(event)">
                </div>

                <div id="statusBox" class="status-box"></div>

                <div id="fileInfo" style="margin-top: 1rem; display: none;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span id="selectedFileName" class="meta-tag">📄 filename.pdf</span>
                        <button class="btn" onclick="uploadFile()">⚡ Parse & Generate JSON</button>
                    </div>
                </div>

                <!-- API Endpoint Reference -->
                <div style="margin-top: 2rem; border-top: 1px solid var(--border); padding-top: 1rem;">
                    <div class="card-title" style="font-size: 0.95rem;">🔌 API Endpoint Info</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; background: #070a12; padding: 0.75rem; border-radius: 6px; border: 1px solid var(--border);">
                        <span style="color: #38bdf8;">POST</span> <span style="color: var(--text);">/api/upload</span><br>
                        <span style="color: var(--text-muted);">Content-Type: multipart/form-data</span>
                    </div>
                </div>
            </div>

            <!-- Right Column: Result Viewer -->
            <div class="card">
                <div class="card-title" style="justify-content: space-between;">
                    <span>📊 Generated JSON Output</span>
                    <div id="metaTags" style="display: flex; gap: 0.5rem;"></div>
                </div>

                <div id="jsonContainer">
                    <pre class="json-viewer" id="jsonViewer">// Upload a timetable file to inspect the generated JSON schema</pre>
                </div>

                <div class="actions-bar" id="actionsBar" style="display: none;">
                    <a id="downloadJsonBtn" class="btn btn-accent" download>⬇️ Download JSON</a>
                    <a id="downloadCsvBtn" class="btn btn-secondary" download>⬇️ Download CSV</a>
                    <button class="btn btn-secondary" onclick="copyJson()">📋 Copy JSON</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;
        let currentJsonData = null;

        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelect();
            }
        });

        function handleFileSelect() {
            if (fileInput.files.length) {
                selectedFile = fileInput.files[0];
                document.getElementById('selectedFileName').innerText = '📄 ' + selectedFile.name;
                document.getElementById('fileInfo').style.display = 'block';
                hideStatus();
            }
        }

        function showStatus(text, type) {
            const statusBox = document.getElementById('statusBox');
            statusBox.className = 'status-box ' + type;
            if (type === 'loading') {
                statusBox.innerHTML = '<span class="spinner"></span> ' + text;
            } else {
                statusBox.innerText = text;
            }
        }

        function hideStatus() {
            document.getElementById('statusBox').style.display = 'none';
        }

        async function uploadFile() {
            if (!selectedFile) return;

            showStatus('Uploading & parsing timetable with deterministic pipeline...', 'loading');

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    showStatus('✅ Successfully parsed timetable and generated JSON file!', 'success');
                    currentJsonData = result.data;
                    document.getElementById('jsonViewer').innerText = JSON.stringify(result.data, null, 2);
                    
                    // Setup download links
                    document.getElementById('downloadJsonBtn').href = result.download_urls.json;
                    document.getElementById('downloadCsvBtn').href = result.download_urls.csv;
                    document.getElementById('actionsBar').style.display = 'flex';

                    // Update meta tags
                    if (result.data && result.data.metadata) {
                        const meta = result.data.metadata;
                        document.getElementById('metaTags').innerHTML = `
                            <span class="meta-tag">📅 ${meta.total_days} Days</span>
                            <span class="meta-tag">⏰ ${meta.total_time_slots} Slots</span>
                            <span class="meta-tag">📋 ${meta.total_entries} Cells</span>
                        `;
                    }
                } else {
                    showStatus('❌ Error: ' + (result.detail || 'Failed to parse file'), 'error');
                }
            } catch (err) {
                showStatus('❌ Network Error: ' + err.message, 'error');
            }
        }

        function copyJson() {
            if (!currentJsonData) return;
            navigator.clipboard.writeText(JSON.stringify(currentJsonData, null, 2));
            alert('JSON copied to clipboard!');
        }
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    print("[START] Starting Automatic Timetable Parsing Pipeline Server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
