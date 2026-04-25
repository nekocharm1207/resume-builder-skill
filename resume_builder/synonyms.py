"""Synonym dictionary and keyword priority for JD-resume matching."""

SKILL_SYNONYMS = {
    # Languages
    "C": ["C", "C++", "C/C++", "Drogon"],
    "JavaScript": ["JavaScript", "JS", "TypeScript", "Vue3", "Vue", "前端开发", "ES6", "HTML", "CSS", "HTML/CSS"],
    "Java": ["Java", "Spring Boot", "Spring", "JVM", "Maven"],
    "Python": ["Python", "Flask", "PyTorch", "TensorFlow", "YOLO"],
    "Go": ["Go", "Golang", "Gin"],
    "Rust": ["Rust"],

    # Technical skills
    "编程能力": ["编程", "开发", "编码", "实现", "蓝桥杯", "算法", "软件"],
    "开发工具": ["Git", "Docker", "VS Code", "IDE", "Linux", "开发环境", "Postman"],
    "调试": ["调试", "测试", "Debug", "排查", "单元测试", "验证", "联调", "修复"],
    "代码维护": ["维护", "重构", "Git", "版本管理", "代码审查", "版本控制"],
    "功能优化": ["优化", "性能", "提升", "改进", "加速", "降耗", "缩短", "提高"],
    "技术文档": ["文档", "接口文档", "README", "注释", "技术说明", "论文", "部署说明"],

    # Soft skills
    "团队协作": ["协作", "团队", "配合", "沟通", "联调", "协同", "成员"],
    "沟通能力": ["沟通", "联调", "对接", "交流", "文档", "配合"],
    "学习意愿": ["学习", "钻研", "自学", "快速掌握", "新技术", "从0到1", "掌握"],
    "执行力": ["按时", "完成", "独立", "负责", "deadline", "交付", "确保"],
}

KEYWORD_PRIORITY = {
    "C": 10,
    "JavaScript": 10,
    "Java": 9,
    "Python": 9,
    "Go": 8,
    "Rust": 8,
    "编程能力": 9,
    "开发工具": 8,
    "调试": 8,
    "代码维护": 7,
    "功能优化": 7,
    "技术文档": 6,
    "团队协作": 6,
    "沟通能力": 6,
    "学习意愿": 5,
    "执行力": 5,
}

JD_KEYWORD_CHECKLIST = [
    ("C语言", ["C", "C++", "Drogon"]),
    ("JavaScript", ["JavaScript", "TypeScript", "Vue3", "前端"]),
    ("Java", ["Java", "Spring Boot", "Spring"]),
    ("Python", ["Python", "Flask", "YOLO"]),
    ("编程能力", ["蓝桥杯", "编程", "开发", "编码"]),
    ("开发工具", ["Git", "Docker", "Linux", "VS Code"]),
    ("调试与测试", ["调试", "测试", "联调", "修复", "验证"]),
    ("代码维护", ["Git", "维护", "版本管理"]),
    ("功能优化", ["优化", "提升", "缩短", "改进"]),
    ("技术文档", ["文档", "接口文档", "说明", "注释"]),
    ("团队协作", ["团队", "协作", "配合", "联调"]),
    ("沟通能力", ["沟通", "对接", "交流", "配合"]),
    ("学习意愿", ["学习", "钻研", "自学", "快速掌握"]),
    ("快速掌握新技术", ["快速掌握", "从0到1", "新技术"]),
]
