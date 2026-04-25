"""JD text parser - extracts structured JDProfile from raw text."""

import re
from typing import List

from .models import JDProfile


# Common keywords for skill extraction
HARD_SKILL_KEYWORDS = [
    "C", "C++", "C#", "Java", "Python", "Go", "Rust", "JavaScript", "TypeScript",
    "Vue", "Vue3", "React", "Angular", "HTML", "CSS", "Node.js",
    "Spring", "Spring Boot", "Django", "Flask", "FastAPI", "Drogon",
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    "Docker", "Kubernetes", "Linux", "Git", "AWS", "Azure",
]

SOFT_SKILL_MAP = {
    "编程": "编程能力",
    "开发": "编程能力",
    "编码": "编程能力",
    "开发工具": "开发工具",
    "工具": "开发工具",
    "调试": "调试与测试",
    "测试": "调试与测试",
    "Debug": "调试与测试",
    "维护": "代码维护",
    "重构": "代码维护",
    "优化": "功能优化",
    "性能": "功能优化",
    "文档": "技术文档",
    "注释": "技术文档",
    "协作": "团队协作",
    "团队": "团队协作",
    "配合": "团队协作",
    "沟通": "沟通能力",
    "对接": "沟通能力",
    "学习": "学习意愿",
    "钻研": "学习意愿",
    "自学": "学习意愿",
    "掌握新技术": "快速掌握新技术",
    "快速掌握": "快速掌握新技术",
}


def parse_jd(jd_text: str) -> JDProfile:
    """
    Parse JD text into structured JDProfile.
    
    Supports both Chinese and English JD formats.
    Falls back to keyword-based extraction when structure is ambiguous.
    """
    jd = JDProfile()
    if not jd_text or not jd_text.strip():
        return jd

    lines = [l.strip() for l in jd_text.strip().splitlines() if l.strip()]
    text_block = " ".join(lines)
    text_lower = text_block.lower()

    # === Extract basic info ===
    # Position
    position_patterns = [
        r"(.{2,20}工程师)",
        r"(.{2,20}开发)",
        r"(.{2,20}算法)",
        r"(.{2,20}产品经理)",
        r"职位[：:]\s*(.+?)(?:\n|\s{2,})",
        r"岗位[：:]\s*(.+?)(?:\n|\s{2,})",
    ]
    for pattern in position_patterns:
        m = re.search(pattern, text_block)
        if m:
            jd.position = m.group(1).strip()
            break

    # Company
    company_patterns = [
        r"公司[：:]\s*(.+?)(?:\n|\s{2,})",
        r"(.+?有限公司)",
        r"(.+?科技)",
    ]
    for pattern in company_patterns:
        m = re.search(pattern, text_block)
        if m:
            jd.company = m.group(1).strip()
            break

    # Location
    if "苏州" in text_block:
        jd.location = "苏州"
    elif "上海" in text_block:
        jd.location = "上海"
    elif "北京" in text_block:
        jd.location = "北京"
    elif "深圳" in text_block:
        jd.location = "深圳"
    elif "杭州" in text_block:
        jd.location = "杭州"

    # Salary
    salary_match = re.search(r"(\d+-\d+K)", text_block, re.IGNORECASE)
    if salary_match:
        jd.salary = salary_match.group(1).upper()

    # Nature
    if "校招" in text_block or "应届" in text_block or "在校生" in text_block:
        jd.nature = "校招"
    elif "实习" in text_block:
        jd.nature = "实习"
    elif "社招" in text_block:
        jd.nature = "社招"

    # Grad year
    year_match = re.search(r"(20\d{2})\s*年?\s*毕业", text_block)
    if year_match:
        jd.grad_year = year_match.group(1)

    # === Extract hard skills ===
    found_skills = set()
    for kw in HARD_SKILL_KEYWORDS:
        # Use word boundary for short keywords to avoid false positives
        if len(kw) <= 2:
            if re.search(rf"\b{re.escape(kw)}\b", text_block):
                found_skills.add(kw)
        else:
            if kw in text_block:
                found_skills.add(kw)
    jd.hard_skills = sorted(found_skills, key=lambda x: text_block.index(x))

    # === Extract soft skills ===
    found_soft = set()
    for key, label in SOFT_SKILL_MAP.items():
        if key in text_block and label not in found_soft:
            found_soft.add(label)
    jd.soft_skills = sorted(found_soft)

    # === Extract responsibilities & requirements ===
    jd.responsibilities = _extract_numbered_list(text_block, ["职责", "岗位", "工作", "负责"])
    jd.requirements = _extract_numbered_list(text_block, ["要求", "任职", "需要", "具备"])

    # Fallback defaults if empty
    if not jd.responsibilities:
        jd.responsibilities = _infer_responsibilities(text_block)
    if not jd.requirements:
        jd.requirements = _infer_requirements(text_block)

    return jd


def _extract_numbered_list(text: str, headers: List[str]) -> List[str]:
    """Extract numbered list items following a header keyword."""
    lines = text.splitlines()
    results = []
    in_list = False
    header_found = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if this line is a header
        if any(h in stripped for h in headers) and not header_found:
            header_found = True
            in_list = True
            continue

        # If we hit another section header, stop
        if header_found and ("要求" in stripped or "职责" in stripped or "福利" in stripped):
            if not any(h in stripped for h in headers):
                break

        # Extract numbered items
        if in_list:
            match = re.match(r"^[\d一二三四五六七八九十]+[\.、\s]+(.+)", stripped)
            if match:
                results.append(match.group(1).strip())
            elif stripped.startswith("-") or stripped.startswith("•"):
                results.append(stripped[1:].strip())

    return results


def _infer_responsibilities(text: str) -> List[str]:
    """Infer default responsibilities if none found."""
    defaults = [
        "参与软件系统的设计与开发，完成基础编码任务",
        "协助完成程序模块的调试与测试工作",
        "根据指导进行代码维护和简单功能优化",
        "配合团队完成基础技术文档的整理与更新",
    ]
    # If text mentions specific duties, use those
    inferred = []
    for d in defaults:
        if any(kw in text for kw in d[:6]):
            inferred.append(d)
    return inferred if inferred else defaults[:2]


def _infer_requirements(text: str) -> List[str]:
    """Infer default requirements if none found."""
    defaults = [
        "具备基本的编程能力，熟悉常用开发工具",
        "能够理解基础技术需求并按时完成分配任务",
        "具备良好的沟通能力，能与团队成员有效协作",
        "有较强的学习意愿，能够快速掌握新技术基础",
    ]
    inferred = []
    for d in defaults:
        if any(kw in text for kw in d[:6]):
            inferred.append(d)
    return inferred if inferred else defaults[:2]
