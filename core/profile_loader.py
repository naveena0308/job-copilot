"""
Profile Loader module.
Handles reading and querying profile.json with normalized lookups.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Set
from config import PROFILE_PATH


def load_profile(path: Path = PROFILE_PATH) -> Dict[str, Any]:
    """Load profile JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Profile file not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile_data: Dict[str, Any], path: Path = PROFILE_PATH) -> None:
    """Save updated profile data back to JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)


def get_flattened_skills(profile: Dict[str, Any]) -> List[str]:
    """Retrieve all skills as a flat list."""
    skills_dict = profile.get("skills", {})
    all_skills = []
    for category, skill_list in skills_dict.items():
        if isinstance(skill_list, list):
            all_skills.extend(skill_list)
    return all_skills


def get_normalized_skills_set(profile: Dict[str, Any]) -> Set[str]:
    """Return a set of lowercase skills for quick matching."""
    skills = get_flattened_skills(profile)
    normalized = set()
    for s in skills:
        cleaned = s.lower().strip()
        normalized.add(cleaned)
        # Also add base variations (e.g. 'AWS (S3, EC2)' -> 'aws', 's3', 'ec2')
        if "(" in cleaned and ")" in cleaned:
            base = cleaned[:cleaned.find("(")].strip()
            inside = cleaned[cleaned.find("(") + 1:cleaned.find(")")].strip()
            if base:
                normalized.add(base)
            for part in inside.split(","):
                part_clean = part.strip()
                if part_clean:
                    normalized.add(part_clean)
    return normalized

