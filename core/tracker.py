"""
Application and Outreach Tracker module.
Persists application states, match scores, tailored resumes, and outreach emails in tracker.json.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import TRACKER_PATH


def load_tracker() -> List[Dict[str, Any]]:
    """Load application records from tracker.json."""
    if not TRACKER_PATH.exists():
        return []
    try:
        with open(TRACKER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_tracker(records: List[Dict[str, Any]]) -> None:
    """Save application records to tracker.json."""
    with open(TRACKER_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def add_application(
    company: str,
    role: str,
    recipient_email: Optional[str] = None,
    ats_score: Optional[float] = None,
    tailored_resume_path: Optional[str] = None,
    status: str = "Discovered",
    notes: str = "",
    url: str = ""
) -> Dict[str, Any]:
    """Add a new job or outreach record to the tracker."""
    records = load_tracker()
    
    # Check if duplicate by company and role
    for r in records:
        if r.get("company", "").lower() == company.lower() and r.get("role", "").lower() == role.lower():
            # Update existing
            if recipient_email:
                r["recipient_email"] = recipient_email
            if ats_score is not None:
                r["ats_score"] = ats_score
            if tailored_resume_path:
                r["tailored_resume_path"] = tailored_resume_path
            if notes:
                r["notes"] = notes
            r["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_tracker(records)
            return r

    new_record = {
        "id": len(records) + 1,
        "company": company,
        "role": role,
        "recipient_email": recipient_email or "",
        "ats_score": ats_score,
        "tailored_resume_path": tailored_resume_path or "",
        "status": status,
        "notes": notes,
        "url": url,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    records.append(new_record)
    save_tracker(records)
    return new_record


def update_status(record_id: int, new_status: str, notes: Optional[str] = None) -> bool:
    """Update status of a tracked job."""
    records = load_tracker()
    for r in records:
        if r.get("id") == record_id:
            r["status"] = new_status
            if notes:
                r["notes"] = notes
            r["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_tracker(records)
            return True
    return False

