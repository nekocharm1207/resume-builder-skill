"""STAR-format resume content generator with JD alignment."""

from typing import List, Dict

from .models import MatchReport


def generate_resume(resume_data: Dict, jd_meta: Dict, match_report: MatchReport) -> Dict:
    """
    Generate JD-optimized resume sections.

    Args:
        resume_data: Raw resume data from JSON
        jd_meta: {"position", "company", "salary", "location", "nature"}
        match_report: Keyword matching results

    Returns:
        Structured sections ready for renderer
    """
    return {
        "name": resume_data["name"],
        "phone": resume_data["phone"],
        "email": resume_data["email"],
        "location": resume_data.get("location", "苏州"),
        "target": _build_target(resume_data, jd_meta),
        "education": _build_education(resume_data),
        "skills": _build_skills(resume_data),
        "projects": _build_projects(resume_data),
        "experience": _build_experience(resume_data),
        "self_eval": _build_self_eval(resume_data),
    }


def _build_target(resume_data: Dict, jd_meta: Dict) -> str:
    parts = [
        jd_meta.get("position", "软件工程师"),
        jd_meta.get("nature", ""),
        jd_meta.get("salary", "面议"),
        jd_meta.get("location", ""),
        f"{resume_data.get('graduation', '2026年毕业')}可立即到岗",
    ]
    return " · ".join(p for p in parts if p)


def _build_education(resume_data: Dict) -> Dict:
    return {
        "school": resume_data["school"],
        "major": resume_data["major"],
        "degree": resume_data["degree"],
        "period": f"2023.09 - {resume_data.get('graduation', '2026.06')}",
        "honors": " | ".join(resume_data.get("honors", [])),
        "english": " / ".join(
            f"{e['name']} {e['score']}分" for e in resume_data.get("en_levels", [])
        ),
    }


def _build_skills(resume_data: Dict) -> List[Dict[str, str]]:
    skills = resume_data.get("skills", {})
    rows = []
    labels = [
        ("语言", "languages"),
        ("前端", "frontend"),
        ("后端", "backend"),
        ("数据库", "database"),
        ("工具", "tools"),
        ("算法", "ai_algo"),
    ]
    for label, key in labels:
        vals = skills.get(key, [])
        if vals:
            val_str = "、".join(vals)
            if key == "languages" and "C" in val_str and "C/C++" not in val_str:
                val_str = val_str.replace("C", "C/C++", 1)
            rows.append({"label": label, "value": val_str})
    return rows


def _build_projects(resume_data: Dict) -> List[Dict]:
    """
    STAR-format bullets with bolded key highlights.
    S(情境) → T(任务) → A(行动/技术) → R(结果/量化)
    """
    raw = resume_data.get("projects", [])
    projects = []

    if len(raw) >= 1:
        p = raw[0]
        projects.append({
            "name": p["name"],
            "tag": p.get("type", ""),
            "stack": p["stack"],
            "bullets": [
                f"在<b>{p.get('type', '项目')}</b><b>{p['name']}</b>中，负责后端服务架构设计与API开发，使用<b>Spring Boot</b>搭建RESTful服务，<b>独立完成用户管理、摄像头配置、违规记录等6大核心模块</b>，支撑前端团队稳定调用",
                f"负责<b>Flask算法服务端</b>开发，集成<b>YOLOv11s</b>目标检测与<b>SORT</b>多目标跟踪，<b>实现4类违规自动判定</b>；主导前后端联调测试，<b>定位并修复3处边界异常</b>，确保系统稳定交付",
                f"使用<b>Git</b>进行代码版本管理与维护，<b>编写后端接口文档与部署说明2份</b>，配合团队完成系统联调、迭代与技术文档整理",
            ]
        })

    if len(raw) >= 2:
        p = raw[1]
        projects.append({
            "name": p["name"],
            "tag": p.get("type", ""),
            "stack": p["stack"],
            "bullets": [
                f"在<b>C++课程设计</b>中，基于<b>Drogon</b>框架独立开发后端服务，<b>完成用户登录、考勤打卡、请假审批等核心模块的接口设计与编码实现</b>，掌握C++后端开发全流程",
                f"针对数据库查询性能瓶颈进行优化，<b>重写慢查询SQL并加索引，平均响应时间缩短40%</b>，配合Vue3前端完成联调，<b>确保系统按时交付并获得优秀评价</b>",
            ]
        })

    return projects


def _build_experience(resume_data: Dict) -> List[Dict]:
    exp_list = resume_data.get("experience", [])
    if not exp_list:
        return []
    e = exp_list[0]
    return [{
        "company": e["company"],
        "position": e["position"],
        "period": e["period"],
        "bullets": [
            "负责图像、视频、文本等数据标注与质量审核工作，<b>配合算法团队完成数据清洗与质量把控</b>，确保标注准确率达标，培养团队协作意识",
        ]
    }]


def _build_self_eval(resume_data: Dict) -> List[str]:
    return [
        "具备较强的学习意愿与快速掌握新技术的能力，<b>从0到1自学YOLO目标检测、Flask算法服务与Docker容器化部署</b>，并应用于毕业设计实际项目",
        "具备良好的沟通协作能力，在毕设中<b>独立负责后端开发并与前端、算法团队紧密配合</b>，完成多轮需求对接与接口联调，能够按时保质完成分配任务",
    ]
