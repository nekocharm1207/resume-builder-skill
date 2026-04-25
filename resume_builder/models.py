"""Data models for JD Resume Builder."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class JDProfile:
    company: str = ""
    position: str = ""
    salary: str = ""
    location: str = ""
    nature: str = ""           # 校招/社招/实习
    grad_year: str = ""
    hard_skills: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)


@dataclass
class ResumeProfile:
    name: str = ""
    phone: str = ""
    email: str = ""
    school: str = ""
    major: str = ""
    degree: str = ""
    graduation: str = ""
    location: str = ""
    skills: Dict[str, List[str]] = field(default_factory=dict)
    projects: List[Dict] = field(default_factory=list)
    experience: List[Dict] = field(default_factory=list)
    self_eval: List[str] = field(default_factory=list)
    honors: List[str] = field(default_factory=list)
    en_levels: List[Dict] = field(default_factory=list)


@dataclass
class SkillMatch:
    jd_keyword: str
    resume_keyword: str
    priority: int = 1


@dataclass
class MatchReport:
    matched: List[SkillMatch] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class PageControlResult:
    pdf_path: str
    pages: int
    attempts: int
    final_style: Dict
    final_sections: Dict
    history: List[Dict]
    warning: Optional[str] = None


@dataclass
class StyleConfig:
    """CSS style configuration for the resume template."""
    body_font_size: str = "10.5pt"
    body_line_height: str = "1.65"
    section_margin: str = "10px"
    bullet_margin: str = "2px 0 2px 1.4em"
    topbar_padding: str = "16px 20px 14px 20px"
    section_title_font_size: str = "13pt"
    topbar_h1_font_size: str = "26pt"
    subtitle_font_size: str = "10.5pt"
    contact_font_size: str = "10pt"
    item_header_font_size: str = "10.5pt"
    bullet_font_size: str = "10pt"
    bullet_line_height: str = "1.58"
    skill_row_line_height: str = "1.85"
    edu_line_font_size: str = "10.5pt"
    edu_detail_font_size: str = "9.5pt"
    badge_font_size: str = "9pt"
    tag_font_size: str = "9pt"
    tech_font_size: str = "9pt"
    right_font_size: str = "9.5pt"
    card_margin_bottom: str = "8px"
