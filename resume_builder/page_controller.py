"""
Robust single-page PDF controller.

When content exceeds 1 page, automatically degrades through:
  Phase 1: Typography shrink (font-size, line-height, margins) - content preserved
  Phase 2: Content pruning (low-priority bullets/sections removed)
  Phase 3: Extreme shrink (font-size down to 7.5pt)

Maximum attempts: 15 (5 typography + 8 content + 2 extreme)
"""

import copy
import logging
import tempfile
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .models import PageControlResult, StyleConfig
from .renderer import render_html
from .pdf_builder import build_pdf as _build_pdf, count_pdf_pages

logger = logging.getLogger(__name__)


class PageController:
    """
    健壮的单页PDF控制器。

    当内容超出 max_pages 时，按以下优先级自动降级：

    Phase 1 - 排版收缩（不改变内容）:
        Step 0: 默认 10.5pt / 1.65 / 10px
        Step 1: 10.0pt / 1.60 / 8px
        Step 2:  9.5pt / 1.55 / 6px
        Step 3:  9.0pt / 1.50 / 6px
        Step 4:  8.5pt / 1.45 / 4px

    Phase 2 - 内容裁剪（按优先级删除）:
        Step 5:  自我评价最后一条bullet
        Step 6:  自我评价全部
        Step 7:  实习经历最后一条bullet
        Step 8:  实习经历全部
        Step 9:  项目2最后一条bullet
        Step 10: 项目2全部
        Step 11: 项目1最后一条bullet

    Phase 3 - 极限排版（理论上不会走到这里）:
        Step 12+: 继续缩小字号
    """

    STYLE_PHASES: List[Dict[str, str]] = [
        {
            "body_font_size": "10.5pt", "body_line_height": "1.65",
            "section_margin": "10px", "bullet_margin": "2px 0 2px 1.4em",
            "topbar_padding": "16px 20px 14px 20px",
            "section_title_font_size": "13pt", "topbar_h1_font_size": "26pt",
            "bullet_line_height": "1.58", "card_margin_bottom": "8px",
        },
        {
            "body_font_size": "10.0pt", "body_line_height": "1.60",
            "section_margin": "8px", "bullet_margin": "1px 0 1px 1.4em",
            "topbar_padding": "14px 18px 12px 18px",
            "section_title_font_size": "12.5pt", "topbar_h1_font_size": "24pt",
            "bullet_line_height": "1.55", "card_margin_bottom": "6px",
        },
        {
            "body_font_size": "9.5pt", "body_line_height": "1.55",
            "section_margin": "6px", "bullet_margin": "1px 0 1px 1.4em",
            "topbar_padding": "12px 16px 10px 16px",
            "section_title_font_size": "12pt", "topbar_h1_font_size": "22pt",
            "bullet_line_height": "1.52", "card_margin_bottom": "5px",
        },
        {
            "body_font_size": "9.0pt", "body_line_height": "1.50",
            "section_margin": "6px", "bullet_margin": "1px 0 0px 1.4em",
            "topbar_padding": "10px 14px 8px 14px",
            "section_title_font_size": "11.5pt", "topbar_h1_font_size": "20pt",
            "bullet_line_height": "1.48", "card_margin_bottom": "4px",
        },
        {
            "body_font_size": "8.5pt", "body_line_height": "1.45",
            "section_margin": "4px", "bullet_margin": "0px 0 0px 1.4em",
            "topbar_padding": "8px 12px 6px 12px",
            "section_title_font_size": "11pt", "topbar_h1_font_size": "18pt",
            "bullet_line_height": "1.45", "card_margin_bottom": "3px",
        },
    ]

    def __init__(
        self,
        sections: Dict,
        max_pages: int = 1,
        max_attempts: int = 15,
        output_path: Optional[str] = None,
    ):
        self.original_sections = copy.deepcopy(sections)
        self.current_sections = copy.deepcopy(sections)
        self.max_pages = max_pages
        self.max_attempts = max_attempts
        self.output_path = output_path
        self.attempt = 0
        self.style_phase = 0
        self.content_phase = 0
        self.history: List[Dict] = []

    def build(self, build_pdf_fn: Optional[Callable] = None) -> PageControlResult:
        """
        主循环：渲染 → 生成PDF → 验证 → 收缩 → 重试

        Returns:
            PageControlResult with pdf_path, pages, attempts, history, etc.
        """
        build_pdf_fn = build_pdf_fn or _build_pdf
        pdf_path = ""
        pages = 0

        for attempt in range(self.max_attempts):
            self.attempt = attempt
            style = self._get_current_style()

            # 渲染HTML
            html = render_html(self.current_sections, style)

            # 生成PDF（使用临时文件避免锁定冲突）
            tmp_pdf = Path(tempfile.gettempdir()) / f"resume_{attempt}_{id(self)}.pdf"
            pdf_path = build_pdf_fn(html, str(tmp_pdf))

            # 验证页数
            pages = count_pdf_pages(pdf_path)
            self.history.append({
                "attempt": attempt,
                "pages": pages,
                "style_phase": self.style_phase,
                "content_phase": self.content_phase,
                "style": style,
            })

            logger.info(
                "[Attempt %d] Pages=%d | font=%s | line-height=%s | section-margin=%s",
                attempt, pages,
                style.get("body_font_size"),
                style.get("body_line_height"),
                style.get("section_margin"),
            )

            if pages <= self.max_pages:
                # 成功！复制到最终输出路径
                if self.output_path:
                    import shutil
                    shutil.copy2(pdf_path, self.output_path)
                    pdf_path = self.output_path
                return PageControlResult(
                    pdf_path=pdf_path,
                    pages=pages,
                    attempts=attempt + 1,
                    final_style=style,
                    final_sections=copy.deepcopy(self.current_sections),
                    history=self.history,
                )

            # 需要收缩
            if not self._shrink():
                logger.warning("All shrink strategies exhausted after %d attempts", attempt + 1)
                if self.output_path:
                    import shutil
                    shutil.copy2(pdf_path, self.output_path)
                    pdf_path = self.output_path
                return PageControlResult(
                    pdf_path=pdf_path,
                    pages=pages,
                    attempts=attempt + 1,
                    final_style=style,
                    final_sections=copy.deepcopy(self.current_sections),
                    history=self.history,
                    warning="Could not fit to target page count after all strategies",
                )

        # 达到最大重试次数
        logger.warning("Max attempts (%d) reached", self.max_attempts)
        if self.output_path:
            import shutil
            shutil.copy2(pdf_path, self.output_path)
            pdf_path = self.output_path
        return PageControlResult(
            pdf_path=pdf_path,
            pages=pages,
            attempts=self.max_attempts,
            final_style=self._get_current_style(),
            final_sections=copy.deepcopy(self.current_sections),
            history=self.history,
            warning=f"Max attempts ({self.max_attempts}) reached",
        )

    def _get_current_style(self) -> Dict[str, str]:
        """获取当前样式配置。"""
        if self.style_phase < len(self.STYLE_PHASES):
            return self.STYLE_PHASES[self.style_phase].copy()

        # 超出预定义phases，极限微缩
        last = self.STYLE_PHASES[-1].copy()
        extra = self.style_phase - len(self.STYLE_PHASES) + 1
        font_val = max(7.5, 8.5 - extra * 0.5)
        last["body_font_size"] = f"{font_val:.1f}pt"
        last["section_title_font_size"] = f"{max(10.0, 11.0 - extra * 0.5):.1f}pt"
        last["topbar_h1_font_size"] = f"{max(16, 18 - extra):.0f}pt"
        return last

    def _shrink(self) -> bool:
        """应用下一级收缩策略。返回False表示所有策略已耗尽。"""
        # Phase 1: 排版收缩
        if self.style_phase < len(self.STYLE_PHASES) + 2:
            self.style_phase += 1
            logger.info("Strategy: typography shrink → phase %d", self.style_phase)
            return True

        # Phase 2: 内容裁剪
        result = self._shrink_content()
        if result:
            self.content_phase += 1
            logger.info("Strategy: content prune → phase %d", self.content_phase)
            return True

        return False

    def _shrink_content(self) -> bool:
        """
        按优先级裁剪内容。返回True表示成功删除了某些内容。
        优先级：自我评价 > 实习经历 > 项目经历（从后往前）
        """
        s = self.current_sections

        # Step 1: 删除自我评价最后一条bullet（保留至少1条）
        if s.get("self_eval") and len(s["self_eval"]) > 1:
            removed = s["self_eval"].pop()
            logger.debug("Pruned: self_eval last bullet → %s", removed[:30])
            return True

        # Step 2: 删除自我评价全部
        if s.get("self_eval"):
            s["self_eval"] = []
            logger.debug("Pruned: self_eval section removed")
            return True

        # Step 3: 删除实习经历最后一条bullet
        if s.get("experience"):
            for idx in range(len(s["experience"]) - 1, -1, -1):
                exp = s["experience"][idx]
                if exp.get("bullets") and len(exp["bullets"]) > 0:
                    removed = exp["bullets"].pop()
                    logger.debug("Pruned: experience bullet → %s", removed[:30])
                    if not exp["bullets"]:
                        s["experience"].pop(idx)
                    return True

        # Step 4: 删除实习经历全部
        if s.get("experience"):
            s["experience"] = []
            logger.debug("Pruned: experience section removed")
            return True

        # Step 5: 删除项目经历最后一个项目的最后一条bullet
        if s.get("projects"):
            for idx in range(len(s["projects"]) - 1, -1, -1):
                proj = s["projects"][idx]
                if proj.get("bullets") and len(proj["bullets"]) > 1:
                    removed = proj["bullets"].pop()
                    logger.debug("Pruned: project%d last bullet → %s", idx, removed[:30])
                    return True

        # Step 6: 删除项目经历最后一个项目（保留至少1个）
        if s.get("projects") and len(s["projects"]) > 1:
            removed = s["projects"].pop()
            logger.debug("Pruned: project removed → %s", removed.get("name", ""))
            return True

        # Step 7: 删除第一个项目的最后一条bullet（保留至少1条）
        if s.get("projects"):
            for proj in s["projects"]:
                if proj.get("bullets") and len(proj["bullets"]) > 1:
                    removed = proj["bullets"].pop()
                    logger.debug("Pruned: project first last bullet → %s", removed[:30])
                    return True

        return False

    def get_shrink_report(self) -> str:
        """生成收缩过程的详细报告。"""
        lines = ["\n📊 Page Control Report", "=" * 50]
        for h in self.history:
            lines.append(
                f"  Attempt {h['attempt']}: {h['pages']} pages | "
                f"font={h['style'].get('body_font_size')} | "
                f"lh={h['style'].get('body_line_height')} | "
                f"margin={h['style'].get('section_margin')}"
            )
        lines.append("=" * 50)
        return "\n".join(lines)
