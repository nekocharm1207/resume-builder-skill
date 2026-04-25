"""PDF builder with Edge headless and robust file handling."""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

from pypdf import PdfReader


def find_edge_executable() -> str:
    """Find Microsoft Edge executable on the system."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_in_path = shutil.which("msedge")
    if edge_in_path:
        candidates.insert(0, edge_in_path)

    for c in candidates:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError(
        "Microsoft Edge not found. Please install Edge or provide path via EDGE_EXE env var."
    )


def build_pdf(html: str, output_path: str, timeout: int = 60) -> str:
    """
    Convert HTML to PDF using Edge headless with cache disabled.

    Args:
        html: Complete HTML string
        output_path: Target PDF path
        timeout: Max seconds to wait for Edge

    Returns:
        Absolute path to generated PDF
    """
    edge_exe = find_edge_executable()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write temporary HTML with random suffix to avoid cache conflicts
    tmp_dir = Path(tempfile.gettempdir())
    ts = int(time.time() * 1000)
    temp_html = tmp_dir / f"resume_{ts}_{os.getpid()}.html"
    temp_html.write_text(html, encoding="utf-8")

    try:
        temp_url = f"file:///{str(temp_html).replace(chr(92), '/')}?v={ts}"
        cmd = [
            edge_exe,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-application-cache",
            "--disable-cache",
            "--disable-gpu-shader-disk-cache",
            "--media-cache-size=1",
            "--disk-cache-size=1",
            f"--print-to-pdf={output_path}",
            temp_url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if not output_path.exists():
            raise RuntimeError(f"PDF generation failed: {result.stderr or 'unknown error'}")
        return str(output_path)
    finally:
        try:
            temp_html.unlink(missing_ok=True)
        except Exception:
            pass


def count_pdf_pages(pdf_path: str) -> int:
    """Return the number of pages in a PDF file."""
    try:
        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except Exception:
        return -1


def verify_pdf_integrity(pdf_path: str) -> bool:
    """Basic sanity check that PDF is readable and non-empty."""
    try:
        reader = PdfReader(str(pdf_path))
        return len(reader.pages) > 0
    except Exception:
        return False
