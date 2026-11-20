"""
Post Hunter Module.
Searches LinkedIn posts for job openings where recruiters/founders include contact email addresses,
and parses job posts from raw text or search results.
"""

import re
import warnings
from typing import List, Dict, Any, Optional

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from config import DEFAULT_TARGET_ROLES, DEFAULT_LOCATIONS

# Regex for extracting emails
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")

# Ignored email domains / addresses that are not recruiter emails
IGNORED_EMAILS = {
    "support@linkedin.com",
    "help@linkedin.com",
    "info@linkedin.com",
    "security@linkedin.com",
    "user@domain.com",
    "name@company.com",
    "email@example.com",
    "yourname@email.com",
}


def extract_emails(text: str) -> List[str]:
    """Extract all valid contact emails from text."""
    found = EMAIL_REGEX.findall(text)
    cleaned = []
    for email in found:
        email_clean = email.lower().strip(".,:;()[]'\"")
        if email_clean not in IGNORED_EMAILS and not email_clean.endswith(".png") and not email_clean.endswith(".jpg"):
            cleaned.append(email_clean)
    # Deduplicate while preserving order
    return list(dict.fromkeys(cleaned))


def extract_company_and_role(title: str, text: str) -> Dict[str, str]:
    """Heuristic extraction of company name and role from title & text."""
    role = "AI/ML Engineer"
    company = "Hiring Team"

    # Common role titles
    for candidate in [
        "Generative AI Engineer", "GenAI Engineer", "Agentic AI Engineer",
        "LLM Engineer", "AI/ML Engineer", "Machine Learning Engineer",
        "Data Scientist", "MLOps Engineer", "AI Researcher", "Computer Vision Engineer"
    ]:
        if candidate.lower() in (title + " " + text).lower():
            role = candidate
            break

    # Look for "at <Company>" or "<Company> is hiring"
    company_match = re.search(r"(?:at|@|join)\s+([A-Z][A-Za-z0-9&.\-_]+(?:\s+[A-Z][A-Za-z0-9&.\-_]+)?)", title + " " + text)
    if company_match:
        matched_candidate = company_match.group(1).strip()
        if matched_candidate.lower() not in {"linkedin", "the", "our", "a", "an", "we", "immediate"}:
            company = matched_candidate

    return {"company": company, "role": role}


def search_hiring_posts(
    role: str = "AI Engineer",
    location: str = "Bangalore",
    keywords: str = "email OR 'send resume'",
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search DuckDuckGo for public LinkedIn posts announcing job openings with contact emails.
    """
    query = f'site:linkedin.com/posts ("hiring" OR "we are looking for" OR "open position") "{role}" {keywords}'
    if location:
        query += f' "{location}"'

    results = []
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for item in raw_results:
                title = item.get("title", "")
                snippet = item.get("body", "")
                url = item.get("href", "")

                full_text = f"{title}\n{snippet}"
                emails = extract_emails(full_text)
                meta = extract_company_and_role(title, full_text)

                results.append({
                    "title": title,
                    "company": meta["company"],
                    "role": meta["role"],
                    "url": url,
                    "snippet": snippet,
                    "emails": emails,
                    "has_email": len(emails) > 0,
                    "source": "LinkedIn Post (DDG Search)"
                })
    except Exception as e:
        print(f"[PostHunter] Search query failed: {e}")

    return results


def parse_pasted_post(raw_text: str, custom_company: Optional[str] = None, custom_role: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse a user-pasted LinkedIn post or Job Description.
    Extracts emails, company, role, and text content.
    """
    emails = extract_emails(raw_text)
    meta = extract_company_and_role("", raw_text)

    company = custom_company or meta["company"]
    role = custom_role or meta["role"]

    return {
        "title": f"{role} at {company}",
        "company": company,
        "role": role,
        "url": "",
        "snippet": raw_text[:300] + ("..." if len(raw_text) > 300 else ""),
        "full_text": raw_text,
        "emails": emails,
        "has_email": len(emails) > 0,
        "source": "User Pasted Content"
    }
