"""
Screening Questions Auto-Filler Module.
Answers LinkedIn Easy Apply questions instantly based on profile.json data.
"""

import re
from typing import Dict, Any, List
from core.profile_loader import load_profile, get_normalized_skills_set


def answer_screening_question(question: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes a screening question and returns the optimal tailored answer with reasoning.
    """
    q_lower = question.lower()
    default_answers = profile.get("default_screening_answers", {})
    candidate_skills = get_normalized_skills_set(profile)
    total_exp = profile.get("experience_years", 1.5)

    # 1. Experience with specific skill
    exp_skill_match = re.search(
        r"(?:experience\s+(?:do you have\s+)?(?:with|in)|years\s+(?:of\s+)?(?:work\s+)?experience\s+(?:do you have\s+)?(?:with|in)|worked with)\s+([a-zA-Z0-9#+.\s]+?)(?:\?|\s+do you have|\s+do you possess|$)",
        q_lower
    )
    if not exp_skill_match:
        # Fallback simpler check
        exp_skill_match = re.search(r"(?:with|in)\s+([a-zA-Z0-9#+.\s]+?)(?:\?|$)", q_lower)

    if exp_skill_match and any(term in q_lower for term in ["year", "experience", "worked"]):
        raw_skill = exp_skill_match.group(1).strip()
        queried_skill = raw_skill.lower()
        
        # Check if candidate has skill
        has_skill = (
            queried_skill in candidate_skills 
            or any(queried_skill in s or s in queried_skill for s in candidate_skills)
        )
        if has_skill:
            ans = str(int(round(total_exp))) if total_exp >= 1 else "1"
            return {
                "question": question,
                "answer": ans,
                "explanation": f"Candidate has verified experience with '{raw_skill}' across professional roles and projects ({total_exp} years total)."
            }
        else:
            return {
                "question": question,
                "answer": "1",
                "explanation": f"Transferable foundational expertise in Python/ML and fast learner; hands-on with adjacent tools."
            }

    # 2. Notice period
    if any(k in q_lower for k in ["notice period", "how soon can you join", "start date", "availability"]):
        ans = default_answers.get("notice_period", "30 days (negotiable)")
        return {
            "question": question,
            "answer": ans,
            "explanation": "From profile default screening answers."
        }

    # 3. Work Authorization / Visa Sponsorship
    if any(k in q_lower for k in ["sponsorship", "visa", "require sponsorship"]):
        return {
            "question": question,
            "answer": "No",
            "explanation": "Candidate is an Indian citizen with full legal authorization to work in India."
        }
    if any(k in q_lower for k in ["authorized to work", "legally authorized", "work authorization"]):
        return {
            "question": question,
            "answer": "Yes",
            "explanation": "Authorized to work in India (Citizen)."
        }

    # 4. Location & Relocation
    if any(k in q_lower for k in ["willing to relocate", "relocation"]):
        return {
            "question": question,
            "answer": default_answers.get("willing_to_relocate", "Yes"),
            "explanation": "Open to relocation for strong opportunities."
        }
    if any(k in q_lower for k in ["current location", "where are you located", "city"]):
        return {
            "question": question,
            "answer": default_answers.get("current_location", "Bangalore, India"),
            "explanation": "Currently residing in Bangalore, Karnataka, India."
        }
    if any(k in q_lower for k in ["hybrid", "remote", "on-site", "work mode", "in-office"]):
        return {
            "question": question,
            "answer": "Yes",
            "explanation": "Comfortable with Hybrid, Remote, or On-site arrangements in Bangalore."
        }

    # 5. Education
    if any(k in q_lower for k in ["education", "degree", "highest level of education", "gpa"]):
        edu = profile.get("education", [])
        deg_name = edu[0].get("degree", "Bachelor's Degree") if edu else "Bachelor's Degree"
        return {
            "question": question,
            "answer": deg_name,
            "explanation": "Dual background: IIT Madras (BS Data Science) & Jeppiaar Institute of Tech (B.Tech AI & DS)."
        }

    # 6. Salary / CTC
    if any(k in q_lower for k in ["ctc", "salary", "compensation", "expected ctc"]):
        return {
            "question": question,
            "answer": "Open to discussion / As per industry standards",
            "explanation": "Professional flexible compensation discussion during interview stages."
        }

    # 7. Generic yes/no or fallback
    return {
        "question": question,
        "answer": "Yes",
        "explanation": "Standard positive qualification match."
    }


def batch_answer_questions(questions: List[str]) -> List[Dict[str, Any]]:
    """Answer a batch of screening questions."""
    profile = load_profile()
    return [answer_screening_question(q, profile) for q in questions if q.strip()]
