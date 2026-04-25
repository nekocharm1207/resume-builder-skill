"""Command-line interface for JD Resume Builder."""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from .config import load_config, load_resume, load_jd
from .jd_parser import parse_jd
from .matcher import match_jd_to_resume, verify_coverage
from .generator import generate_resume
from .renderer import render_html
from .page_controller import PageController
from .pdf_builder import build_pdf
from .anonymizer import Anonymizer
from .logger import setup_logger

logger = setup_logger()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jd-resume-builder",
        description="AI-driven resume generator tailored to job descriptions.",
    )
    parser.add_argument("--jd", required=True, help="Path to JD text file")
    parser.add_argument("--resume", required=True, help="Path to resume JSON file")
    parser.add_argument("--output", "-o", default="./output", help="Output directory")
    parser.add_argument("--config", "-c", help="Path to config YAML file")
    parser.add_argument("--max-pages", type=int, default=1, help="Max pages (default: 1)")
    parser.add_argument("--max-attempts", type=int, default=15, help="Max shrink attempts")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML only, skip PDF")
    parser.add_argument("--anonymize", "-a", action="store_true", help="Anonymize PII in output")
    return parser


def main(argv: list = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger("resume_builder").setLevel(logging.DEBUG)

    # Load config
    config = load_config(args.config)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load inputs
    try:
        resume_data = load_resume(args.resume)
        jd_text = load_jd(args.jd)
    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    # Anonymize if requested
    if args.anonymize:
        anon = Anonymizer()
        resume_data = anon.anonymize(resume_data)
        if args.verbose:
            anon.print_log()

    logger.info("=" * 50)
    logger.info("JD Resume Builder v1.0")
    logger.info("=" * 50)
    logger.info("Resume: %s (%s)", resume_data.get("name"), args.resume)
    logger.info("JD: %s", args.jd)

    # Parse JD
    jd = parse_jd(jd_text)
    logger.info("Parsed JD: %s | %s | %s", jd.company, jd.position, jd.location)
    logger.info("Hard skills: %s", ", ".join(jd.hard_skills))
    logger.info("Soft skills: %s", ", ".join(jd.soft_skills))

    # Match
    match_report = match_jd_to_resume(jd, resume_data)
    logger.info("Match results: %d matched, %d missing", len(match_report.matched), len(match_report.missing))
    for m in match_report.matched[:5]:
        logger.info("  ✓ %s → %s (P%d)", m.jd_keyword, m.resume_keyword, m.priority)
    for s in match_report.suggestions[:3]:
        logger.info("  ⚠ %s", s)

    # Generate resume content
    sections = generate_resume(resume_data, {
        "position": jd.position,
        "company": jd.company,
        "salary": jd.salary,
        "location": jd.location,
        "nature": jd.nature,
    }, match_report)
    logger.info("Generated: %d projects, %d experience entries", len(sections["projects"]), len(sections.get("experience", [])))

    # Render HTML
    html = render_html(sections)
    ts = datetime.now().strftime("%m%d_%H%M%S")
    html_path = output_dir / f"resume_{ts}.html"
    html_path.write_text(html, encoding="utf-8")
    logger.info("HTML saved: %s", html_path)

    if args.html_only:
        logger.info("HTML-only mode, skipping PDF.")
        return 0

    # Build PDF with robust page control
    pdf_name = f"{resume_data.get('name', 'resume')}_{jd.position}_{ts}.pdf"
    pdf_path = output_dir / pdf_name

    controller = PageController(
        sections=sections,
        max_pages=args.max_pages,
        max_attempts=args.max_attempts,
        output_path=str(pdf_path),
    )
    result = controller.build()

    # Report
    pages = count_pdf_pages(result.pdf_path) if result.pdf_path else -1
    logger.info("PDF: %s (%d pages, %d attempts)", result.pdf_path, pages, result.attempts)
    if result.warning:
        logger.warning(result.warning)

    # Coverage report
    coverage = verify_coverage(result.final_sections)
    hit = sum(1 for v in coverage.values() if v)
    total = len(coverage)
    logger.info("Keyword coverage: %d/%d (%d%%)", hit, total, hit * 100 // total)
    for k, v in coverage.items():
        logger.info("  %s %s", "✅" if v else "❌", k)

    # Print shrink report if multiple attempts
    if result.attempts > 1:
        print(controller.get_shrink_report())

    logger.info("Done.")
    return 0


def count_pdf_pages(pdf_path: str) -> int:
    from pypdf import PdfReader
    try:
        return len(PdfReader(pdf_path).pages)
    except Exception:
        return -1


if __name__ == "__main__":
    sys.exit(main())
