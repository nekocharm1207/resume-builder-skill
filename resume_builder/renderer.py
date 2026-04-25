"""HTML renderer with dynamic style configuration."""

from jinja2 import Template
from typing import Dict, Optional

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{{ name }} - 简历</title>
<style>
@page {
  size: A4;
  margin: 0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
  font-size: {{ style.body_font_size | default('10.5pt') }};
  line-height: {{ style.body_line_height | default('1.65') }};
  color: #222;
  background: #fff;
  padding: 10mm 13mm 10mm 13mm;
}

/* ===== 顶部横条 ===== */
.topbar {
  background: #1e3a5f;
  color: #fff;
  padding: {{ style.topbar_padding | default('16px 20px 14px 20px') }};
  margin: -10mm -13mm 14px -13mm;
  padding-left: calc(13mm + 20px);
  padding-right: calc(13mm + 20px);
}
.topbar-inner { display: flex; justify-content: space-between; align-items: flex-end; }
.topbar h1 {
  font-size: {{ style.topbar_h1_font_size | default('26pt') }};
  font-weight: 700;
  letter-spacing: 5px;
  margin: 0;
  line-height: 1.05;
  color: #fff;
}
.topbar .subtitle {
  font-size: {{ style.subtitle_font_size | default('10.5pt') }};
  color: #e2e8f0;
  margin-top: 6px;
  letter-spacing: 0.5px;
  font-weight: 500;
}
.topbar .contact {
  font-size: {{ style.contact_font_size | default('10pt') }};
  color: #e2e8f0;
  text-align: right;
  line-height: 1.65;
  font-weight: 500;
}

/* ===== 分节标题 ===== */
.section { margin-bottom: {{ style.section_margin | default('10px') }}; }
.section-title {
  font-size: {{ style.section_title_font_size | default('13pt') }};
  font-weight: 700;
  color: #fff;
  background: #2c5282;
  padding: 4px 10px;
  margin-bottom: 7px;
  border-radius: 3px;
  letter-spacing: 1px;
}

/* ===== 通用条目头部 ===== */
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: {{ style.item_header_font_size | default('10.5pt') }};
  margin-bottom: 2px;
}
.item-header .left {
  font-weight: 700;
  color: #1a1a1a;
  font-size: {{ style.item_header_font_size | default('10.5pt') }};
}
.item-header .tag {
  font-size: {{ style.tag_font_size | default('9pt') }};
  color: #555;
  font-weight: 400;
  margin-left: 5px;
}
.item-header .right {
  color: #555;
  font-size: {{ style.right_font_size | default('9.5pt') }};
  font-variant-numeric: tabular-nums;
}
.item-header .tech {
  color: #4a5568;
  font-size: {{ style.tech_font_size | default('9pt') }};
  font-style: italic;
}

/* ===== Bullet ===== */
.bullet {
  margin: {{ style.bullet_margin | default('2px 0 2px 1.4em') }};
  text-indent: -1.4em;
  font-size: {{ style.bullet_font_size | default('10pt') }};
  line-height: {{ style.bullet_line_height | default('1.58') }};
  color: #333;
}
.bullet::before {
  content: "• ";
  color: #2c5282;
  font-weight: 700;
}
.bullet b {
  color: #1a202c;
  font-weight: 700;
}

/* ===== 教育背景 ===== */
.edu-line {
  display: flex;
  justify-content: space-between;
  font-size: {{ style.edu_line_font_size | default('10.5pt') }};
  font-weight: 600;
}
.edu-detail {
  font-size: {{ style.edu_detail_font_size | default('9.5pt') }};
  color: #444;
  margin-top: 2px;
}
.edu-detail .badge {
  display: inline-block;
  background: #edf2f7;
  color: #2d3748;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: {{ style.badge_font_size | default('9pt') }};
  margin-right: 6px;
  font-weight: 500;
}

/* ===== 技术栈 ===== */
.skills-block {
  font-size: 10pt;
  line-height: {{ style.skill_row_line_height | default('1.85') }};
}
.skill-row {
  display: flex;
  margin-bottom: 1px;
}
.skill-label {
  font-weight: 700;
  color: #1e3a5f;
  min-width: 58px;
  flex-shrink: 0;
}
.skill-value { color: #333; }

/* ===== 经历卡片 ===== */
.card { margin-bottom: {{ style.card_margin_bottom | default('8px') }}; }
.card:last-child { margin-bottom: 0; }
</style>
</head>
<body>

<!-- 顶部横条 -->
<div class="topbar">
  <div class="topbar-inner">
    <div>
      <h1>{{ name }}</h1>
      <div class="subtitle">{{ target }}</div>
    </div>
    <div class="contact">
      <div>{{ phone }}</div>
      <div>{{ email }}</div>
    </div>
  </div>
</div>

<!-- 教育背景 -->
<div class="section">
  <div class="section-title">教育背景</div>
  <div class="edu-line">
    <span>{{ education.school }} · {{ education.major }} · {{ education.degree }}</span>
    <span class="right">{{ education.period }}</span>
  </div>
  <div class="edu-detail">
    <span class="badge">{{ education.honors }}</span>
    <span class="badge">{{ education.english }}</span>
  </div>
</div>

<!-- 技术栈 -->
<div class="section">
  <div class="section-title">技术栈</div>
  <div class="skills-block">
    {% for row in skills %}
    <div class="skill-row">
      <span class="skill-label">{{ row.label }}</span>
      <span class="skill-value">{{ row.value }}</span>
    </div>
    {% endfor %}
  </div>
</div>

<!-- 项目经历 -->
<div class="section">
  <div class="section-title">项目经历</div>
  {% for proj in projects %}
  <div class="card">
    <div class="item-header card-header">
      <span class="left">{{ proj.name }}<span class="tag">{{ proj.tag }}</span></span>
      <span class="tech">{{ proj.stack }}</span>
    </div>
    <div class="card-body">
      {% for b in proj.bullets %}
      <div class="bullet">{{ b }}</div>
      {% endfor %}
    </div>
  </div>
  {% endfor %}
</div>

<!-- 实习经历 -->
{% if experience %}
<div class="section">
  <div class="section-title">实习经历</div>
  {% for exp in experience %}
  <div class="card">
    <div class="item-header card-header">
      <span class="left">{{ exp.company }}<span class="tag">{{ exp.position }}</span></span>
      <span class="right">{{ exp.period }}</span>
    </div>
    <div class="card-body">
      {% for b in exp.bullets %}
      <div class="bullet">{{ b }}</div>
      {% endfor %}
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}

<!-- 自我评价 -->
{% if self_eval %}
<div class="section">
  <div class="section-title">自我评价</div>
  {% for ev in self_eval %}
  <div class="bullet">{{ ev }}</div>
  {% endfor %}
</div>
{% endif %}

</body>
</html>
'''


def render_html(sections: dict, style: Optional[dict] = None) -> str:
    """
    Render resume HTML with dynamic style overrides.

    Args:
        sections: Resume content data
        style: Optional CSS style overrides (e.g., {"body_font_size": "9pt"})

    Returns:
        Complete HTML string ready for PDF conversion
    """
    template = Template(HTML_TEMPLATE)
    # Pass sections keys directly for cleaner template access
    ctx = {"style": style or {}}
    ctx.update(sections)
    return template.render(**ctx)
