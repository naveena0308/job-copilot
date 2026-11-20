"""
ATS Matcher and Skill Gap Analyzer module.
Evaluates job descriptions against candidate profile, computes ATS match scores,
identifies skill gaps, and determines whether resume tailoring is required.
"""

import re
from typing import Dict, Any, List, Set, Tuple
from config import TECH_SKILLS_TAXONOMY, SCORING_WEIGHTS
from core.profile_loader import load_profile, get_normalized_skills_set, get_flattened_skills


def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """
    Scan job text against the skills taxonomy and identify all mentioned skills.
    Returns categorized detected skills.
    """
    text_lower = " " + text.lower() + " "
    detected = {}

    for category, skill_list in TECH_SKILLS_TAXONOMY.items():
        found_in_cat = []
        for skill in skill_list:
            # Word boundary regex matching to avoid substring false positives (e.g. 'c' in 'cloud')
            pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
            if re.search(pattern, text_lower):
                found_in_cat.append(skill)
        if found_in_cat:
            detected[category] = found_in_cat

    return detected


def extract_experience_required(text: str) -> Tuple[float, str]:
    """
    Extract required years of experience from job text using regex patterns.
    Returns (min_years, explanation_string).
    """
    patterns = [
        r"(\d+)\s*(?:-\s*(\d+)|\+)?\s*(?:years|yrs)(?:\s+of)?\s+experience",
        r"experience\s*:\s*(\d+)(?:\s*-\s*(\d+)|\+)?\s*(?:years|yrs)",
        r"minimum\s+(?:of\s+)?(\d+)\s*(?:years|yrs)",
    ]

    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            min_yr = float(match.group(1))
            full_match = match.group(0)
            return min_yr, full_match

    # Default if no explicit years found
    return 0.0, "No explicit years specified"


def match_job(job_text: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute comprehensive match score and gap analysis.
    """
    detected_by_cat = extract_skills_from_text(job_text)
    candidate_skills = get_normalized_skills_set(profile)

    all_jd_skills = []
    matched_skills = []
    missing_skills = []

    for cat, skills in detected_by_cat.items():
        for skill in skills:
            all_jd_skills.append(skill)
            # Check if skill or synonym is in candidate skills
            if skill in candidate_skills:
                matched_skills.append(skill)
            else:
                # Check partial / related match
                is_matched = any(skill in cs or cs in skill for cs in candidate_skills)
                if is_matched:
                    matched_skills.append(skill)
                else:
                    missing_skills.append(skill)

    total_jd_skills = len(all_jd_skills)
    skill_coverage = (len(matched_skills) / total_jd_skills) if total_jd_skills > 0 else 0.85

    # Experience check
    min_exp, exp_match_str = extract_experience_required(job_text)
    candidate_exp = profile.get("experience_years", 1.5)

    if min_exp == 0.0 or candidate_exp >= min_exp:
        exp_score = 1.0
        exp_status = f"Candidate's {candidate_exp} yrs meets or exceeds {exp_match_str}"
    elif candidate_exp >= (min_exp - 1.0):
        exp_score = 0.80
        exp_status = f"Close match: Candidate has {candidate_exp} yrs vs {exp_match_str}"
    else:
        exp_score = 0.50
        exp_status = f"Experience stretch: Requires {exp_match_str}, candidate has {candidate_exp} yrs"

    # Role relevance
    target_roles = [r.lower() for r in profile.get("target_roles", [])]
    text_lower = job_text.lower()
    role_score = 0.70
    matched_target_role = "AI/ML Role"
    for r in target_roles:
        if r in text_lower:
            role_score = 1.0
            matched_target_role = r.title()
            break

    # Location fit check
    preferred_locs = ["chennai", "bangalore", "bengaluru", "remote", "hybrid"]
    is_chennai = "chennai" in text_lower
    is_bangalore = "bangalore" in text_lower or "bengaluru" in text_lower
    is_remote = "remote" in text_lower or "hybrid" in text_lower

    if is_chennai:
        location_status = "Direct Match (Chennai - Primary Preference)"
    elif is_bangalore:
        location_status = "Match (Bangalore - Secondary Preference)"
    elif is_remote:
        location_status = "Match (Remote / Hybrid)"
    else:
        location_status = "Location not explicitly specified or outside primary preference"

    # Calculate overall ATS Score (0 - 100)
    w_skills = SCORING_WEIGHTS["required_skills"]
    w_exp = SCORING_WEIGHTS["experience_fit"]
    w_role = SCORING_WEIGHTS["role_relevance"]
    w_pref = SCORING_WEIGHTS["preferred_skills"]

    raw_score = (skill_coverage * (w_skills + w_pref) + exp_score * w_exp + role_score * w_role)
    ats_score = round(raw_score * 100, 1)

    # Determine if tailoring is needed
    tailoring_needed = False
    reasons = []

    if ats_score < 88.0 and len(missing_skills) > 0:
        tailoring_needed = True
        reasons.append(f"JD highlights {len(missing_skills)} key skills ({', '.join(missing_skills[:4])}) that can be synergized into projects/skills.")

    # Check if specific projects should be emphasized
    if any(k in all_jd_skills for k in ["langgraph", "mcp", "autogen", "react", "agentic", "llamaindex"]):
        tailoring_needed = True
        reasons.append("Role is heavily Agentic AI / LLM focused. Prioritizing 'FinSight AI' and 'GnA Engine' at top will strongly maximize ATS relevance.")
    elif any(k in all_jd_skills for k in ["mlops", "docker", "mlflow", "ci/cd", "deployment"]):
        tailoring_needed = True
        reasons.append("Role emphasizes MLOps/Production deployments. Reordering skills to front-load MLflow, Docker, CI/CD and highlighting Churn Prediction pipeline is advised.")
    elif any(k in all_jd_skills for k in ["computer vision", "opencv", "yolo"]):
        tailoring_needed = True
        reasons.append("Role involves Computer Vision. Highlighting multimodal CV workflows and YOLO/OpenCV is recommended.")

    if not tailoring_needed:
        reasons.append("Profile already has high alignment (>88% ATS fit) with default resume; tailoring optional.")

    return {
        "ats_score": ats_score,
        "matched_skills": list(dict.fromkeys(matched_skills)),
        "missing_skills": list(dict.fromkeys(missing_skills)),
        "all_jd_skills": all_jd_skills,
        "skill_coverage_pct": round(skill_coverage * 100, 1),
        "experience_fit": {
            "required_exp": min_exp,
            "detected_phrase": exp_match_str,
            "candidate_exp": candidate_exp,
            "status": exp_status,
        },
        "role_relevance": {
            "matched_role": matched_target_role,
            "score": role_score,
        },
        "location_fit": location_status,
        "tailoring_needed": tailoring_needed,
        "tailoring_reasons": reasons,
    }

