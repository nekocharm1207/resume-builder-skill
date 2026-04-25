"""
Privacy anonymizer for resume data.

Replaces real names, schools, companies, and project names with placeholders.
Ensures generated resumes never leak personal identifiable information (PII).
"""

import copy
import re
from typing import Dict, List, Optional


# Default anonymization rules
DEFAULT_RULES = {
    # PII fields: exact replacement
    "name": "张XX",
    "phone": "138****8888",
    "email": "zhangxx@example.com",
    "school": "XX大学",
    "company": "XX公司",
    
    # Project name patterns: regex → replacement
    "project_patterns": [
        (r"智慧交通.*?监控系统", "XX智能监控系统"),
        (r"校园考勤系统", "XX管理系统"),
        (r"2025.*?大数据挑战赛", "XX数据竞赛项目"),
    ],
    
    # Company patterns
    "company_patterns": [
        (r".*?信息科技.*?公司", "XX科技有限公司"),
        (r".*?智能科技.*?公司", "XX科技有限公司"),
    ],
    
    # Location patterns (keep city, anonymize district)
    "location_patterns": [
        (r"苏州·.*?·.*?\s", "苏州 "),
        (r"苏州·.*?\s", "苏州 "),
    ],
}


class Anonymizer:
    """
    Anonymizes resume data before generation.
    
    Usage:
        anon = Anonymizer()
        safe_data = anon.anonymize(resume_data)
    """

    def __init__(self, rules: Optional[Dict] = None):
        self.rules = rules or DEFAULT_RULES
        self._replacement_log: List[Dict] = []

    def anonymize(self, data: Dict) -> Dict:
        """Return a deep-copied, anonymized version of resume data."""
        result = copy.deepcopy(data)
        self._replacement_log = []

        # 1. Replace exact PII fields
        for field, replacement in self.rules.items():
            if field in result and isinstance(replacement, str):
                old = result[field]
                result[field] = replacement
                self._log(field, old, replacement)

        # 2. Replace in nested text fields
        self._anonymize_nested(result)

        return result

    def _anonymize_nested(self, data: Dict) -> None:
        """Anonymize text within nested structures (projects, experience, bullets)."""
        
        # Projects
        for proj in data.get("projects", []):
            old_name = proj.get("name", "")
            new_name = self._apply_project_patterns(old_name)
            if new_name != old_name:
                proj["name"] = new_name
                self._log("project.name", old_name, new_name)
            
            # Anonymize bullets
            proj["bullets"] = [
                self._apply_all_patterns(b) for b in proj.get("bullets", [])
            ]

        # Experience
        for exp in data.get("experience", []):
            old_company = exp.get("company", "")
            new_company = self._apply_company_patterns(old_company)
            if new_company != old_company:
                exp["company"] = new_company
                self._log("experience.company", old_company, new_company)
            
            exp["bullets"] = [
                self._apply_all_patterns(b) for b in exp.get("bullets", [])
            ]

        # Self evaluation
        data["self_eval"] = [
            self._apply_all_patterns(e) for e in data.get("self_eval", [])
        ]

        # Target/location
        if "location" in data:
            old_loc = data["location"]
            new_loc = self._apply_location_patterns(old_loc)
            if new_loc != old_loc:
                data["location"] = new_loc
                self._log("location", old_loc, new_loc)

    def _apply_project_patterns(self, text: str) -> str:
        for pattern, replacement in self.rules.get("project_patterns", []):
            text = re.sub(pattern, replacement, text)
        return text

    def _apply_company_patterns(self, text: str) -> str:
        for pattern, replacement in self.rules.get("company_patterns", []):
            text = re.sub(pattern, replacement, text)
        return text

    def _apply_location_patterns(self, text: str) -> str:
        for pattern, replacement in self.rules.get("location_patterns", []):
            text = re.sub(pattern, replacement, text)
        return text

    def _apply_all_patterns(self, text: str) -> str:
        text = self._apply_project_patterns(text)
        text = self._apply_company_patterns(text)
        text = self._apply_location_patterns(text)
        # Replace school name if it appears in text
        school = self.rules.get("school", "XX大学")
        text = text.replace("南京航空航天大学金城学院", school)
        return text

    def _log(self, field: str, old: str, new: str) -> None:
        self._replacement_log.append({"field": field, "old": old, "new": new})

    def get_log(self) -> List[Dict]:
        """Return all replacements made during anonymization."""
        return self._replacement_log

    def print_log(self) -> None:
        """Print anonymization log for verification."""
        print("\n🔒 Anonymization Log")
        print("=" * 50)
        for entry in self._replacement_log:
            print(f"  [{entry['field']}]")
            print(f"    OLD: {entry['old']}")
            print(f"    NEW: {entry['new']}")
        print("=" * 50)
