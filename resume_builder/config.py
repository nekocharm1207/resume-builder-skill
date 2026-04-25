"""Configuration loader for JD Resume Builder."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

import yaml


DEFAULT_CONFIG = {
    "output_dir": "./output",
    "max_pages": 1,
    "max_attempts": 15,
    "pdf_timeout": 60,
    "edge_exe": None,  # auto-detect
    "template": "default",
    "style": {
        "body_font_size": "10.5pt",
        "body_line_height": "1.65",
        "section_margin": "10px",
    },
}


def load_config(path: Optional[str] = None) -> Dict:
    """
    Load configuration from file or return defaults.

    Searches:
      1. Provided path
      2. ./resume_builder.yaml
      3. ~/.config/resume-builder/config.yaml
      4. Environment variables (RESUME_BUILDER_*)
    """
    config = DEFAULT_CONFIG.copy()

    # Try file-based config
    candidates = []
    if path:
        candidates.append(Path(path))
    candidates.extend([
        Path("resume_builder.yaml"),
        Path.home() / ".config" / "resume-builder" / "config.yaml",
    ])

    for candidate in candidates:
        if candidate.exists():
            raw = yaml.safe_load(candidate.read_text(encoding="utf-8"))
            if raw:
                config.update(raw)
            break

    # Override from environment
    for key in config:
        env_key = f"RESUME_BUILDER_{key.upper()}"
        if env_key in os.environ:
            config[key] = os.environ[env_key]

    return config


def load_resume(path: str) -> Dict:
    """Load resume data from JSON file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Resume file not found: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def load_jd(path: str) -> str:
    """Load JD text from file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JD file not found: {path}")
    return p.read_text(encoding="utf-8")
