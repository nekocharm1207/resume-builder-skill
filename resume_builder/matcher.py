"""Keyword matching engine between JD and resume."""

from typing import Dict, List, Set

from .models import JDProfile, MatchReport, SkillMatch
from .synonyms import SKILL_SYNONYMS, KEYWORD_PRIORITY, JD_KEYWORD_CHECKLIST


def extract_keywords_from_resume(resume_data: Dict) -> Set[str]:
    """Extract all searchable text tokens from resume data."""
    texts = []
    texts.append(resume_data.get("name", ""))
    texts.append(resume_data.get("school", ""))
    texts.append(resume_data.get("major", ""))
    texts.extend(resume_data.get("honors", []))

    skills = resume_data.get("skills", {})
    for cat in ["languages", "frontend", "backend", "database", "tools", "ai_algo"]:
        texts.extend(skills.get(cat, []))

    for proj in resume_data.get("projects", []):
        texts.append(proj.get("name", ""))
        texts.append(proj.get("stack", ""))
        texts.extend(proj.get("bullets", []))

    for exp in resume_data.get("experience", []):
        texts.append(exp.get("company", ""))
        texts.append(exp.get("position", ""))
        texts.extend(exp.get("bullets", []))

    texts.extend(resume_data.get("self_eval", []))

    text_block = " ".join(str(t) for t in texts)
    words = set()
    for raw in text_block.replace("、", " ").replace("，", " ").replace("/", " ").split():
        words.add(raw)
        for sub in raw.split("/"):
            words.add(sub)
    return words


def match_jd_to_resume(jd: JDProfile, resume_data: Dict) -> MatchReport:
    """Match JD keywords against resume with synonym expansion."""
    resume_words = extract_keywords_from_resume(resume_data)
    report = MatchReport()

    # Build JD keyword set
    jd_keywords = set()
    jd_keywords.update(jd.hard_skills)
    jd_keywords.update(jd.soft_skills)

    for resp in jd.responsibilities:
        for kw in ["设计", "开发", "编码", "调试", "测试", "维护", "优化", "文档"]:
            if kw in resp:
                jd_keywords.add(kw)

    for req in jd.requirements:
        for kw in ["编程", "工具", "调试", "测试", "维护", "优化", "文档", "协作", "沟通", "学习"]:
            if kw in req:
                jd_keywords.add(kw)

    # Synonym matching
    for jd_kw, syn_list in SKILL_SYNONYMS.items():
        matched = False
        for syn in syn_list:
            if syn in resume_words:
                report.matched.append(SkillMatch(
                    jd_keyword=jd_kw,
                    resume_keyword=syn,
                    priority=KEYWORD_PRIORITY.get(jd_kw, 1),
                ))
                matched = True
                break
        if not matched:
            report.missing.append(jd_kw)

    # Deduplicate matched by jd_keyword (keep highest priority)
    seen = {}
    for m in report.matched:
        if m.jd_keyword not in seen or seen[m.jd_keyword].priority < m.priority:
            seen[m.jd_keyword] = m
    report.matched = sorted(seen.values(), key=lambda x: x.priority, reverse=True)

    # Generate suggestions
    for miss in report.missing:
        if miss == "代码维护":
            report.suggestions.append("在项目经历中补充'使用Git进行代码版本管理与维护'")
        elif miss == "技术文档":
            report.suggestions.append("补充'编写接口文档/技术说明/部署文档'相关描述")
        elif miss == "功能优化":
            report.suggestions.append("补充性能优化或功能改进的具体数据（如响应时间缩短X%）")
        elif miss == "调试":
            report.suggestions.append("补充'完成模块调试/接口联调/问题排查'相关内容")
        else:
            report.suggestions.append(f"建议在简历中显式提及'{miss}'相关能力")

    return report


def verify_coverage(sections: Dict) -> Dict[str, bool]:
    """Verify JD keyword coverage in generated resume sections."""
    resume_text = str(sections)
    result = {}
    for label, keywords in JD_KEYWORD_CHECKLIST:
        hit = any(kw in resume_text for kw in keywords)
        result[label] = hit
    return result
