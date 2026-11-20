"""
Dynamic Resume Tailoring & PDF Generation module using ReportLab.
Updates and compiles a customized ATS-optimized PDF resume when needed for a specific JD.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from config import DEFAULT_RESUME_PATH, RESUMES_DIR
from core.profile_loader import load_profile
from core.matcher import match_job


def generate_tailored_objective(role: str, company: str, matched_skills: list) -> str:
    """Generate an objective tailored to the target role, company, and key skills."""
    skills_preview = ", ".join([s.title() for s in matched_skills[:4]]) if matched_skills else "Python, GenAI, and MLOps"
    return (
        f"AI/ML Engineer with hands-on experience building production-grade LLM applications, "
        f"autonomous agentic workflows, and end-to-end ML pipelines in Python. "
        f"Demonstrated track record leveraging {skills_preview} to deliver high-precision AI systems. "
        f"Excited to contribute to {company} as a {role} by shipping scalable, production-ready AI solutions."
    )


def order_skills_for_jd(skills_dict: Dict[str, list], all_jd_skills: list) -> Dict[str, list]:
    """Reorder and prioritize skills according to relevance to the JD."""
    jd_skills_lower = [s.lower() for s in all_jd_skills]
    
    scored_categories = []
    for cat, s_list in skills_dict.items():
        # Score category by how many of its skills are mentioned in the JD
        matches = sum(1 for s in s_list if any(part in jd_skills_lower for part in s.lower().split()))
        scored_categories.append((matches, cat, s_list))

    # Sort categories descending by relevance score
    scored_categories.sort(key=lambda x: x[0], reverse=True)

    ordered = {}
    for _, cat, s_list in scored_categories:
        # Inside each category, put JD-matching skills first
        matching = [s for s in s_list if any(part in jd_skills_lower for part in s.lower().split())]
        others = [s for s in s_list if s not in matching]
        ordered[cat] = matching + others

    return ordered


def build_pdf_resume(
    profile: Dict[str, Any],
    objective_text: str,
    skills_dict: Dict[str, list],
    output_pdf_path: Path
) -> None:
    """
    Renders an ATS-friendly, clean, elegant PDF resume using ReportLab.
    """
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1, # Center
        textColor=colors.HexColor("#1A1A1A"),
        spaceAfter=3
    )

    contact_style = ParagraphStyle(
        'ContactInfo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#333333"),
        spaceAfter=10
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#111827"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#222222")
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        leftIndent=12,
        textColor=colors.HexColor("#222222"),
        spaceAfter=2
    )

    story = []

    # 1. Header: Name & Contact
    story.append(Paragraph(profile.get("name", "Naveena N").upper(), title_style))
    contact_parts = [
        profile.get("phone", "+91 6379595692"),
        profile.get("email", "navirajan2003@gmail.com"),
        profile.get("location", "Bangalore, India"),
    ]
    if profile.get("linkedin"):
        contact_parts.append(f'<a href="{profile["linkedin"]}">LinkedIn</a>')
    if profile.get("github"):
        contact_parts.append(f'<a href="{profile["github"]}">GitHub</a>')

    story.append(Paragraph(" &nbsp;&bull;&nbsp; ".join(contact_parts), contact_style))

    def add_section_divider(heading: str):
        story.append(Paragraph(heading, section_heading))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#CCCCCC"), spaceBefore=1, spaceAfter=5))

    # 2. Objective
    add_section_divider("OBJECTIVE")
    story.append(Paragraph(objective_text, body_style))
    story.append(Spacer(1, 4))

    # 3. Education
    add_section_divider("EDUCATION")
    for edu in profile.get("education", []):
        degree = edu.get("degree", "")
        school = edu.get("institution", "")
        period = edu.get("period", "")
        edu_html = f"<b>{degree}</b> &nbsp;|&nbsp; <i>{school}</i> <font color='#666666'>({period})</font>"
        story.append(Paragraph(edu_html, body_style))
        story.append(Spacer(1, 2))

    # 4. Skills
    add_section_divider("SKILLS")
    for cat_name, s_items in skills_dict.items():
        cat_label = cat_name.replace("_", " ").title()
        skill_str = ", ".join(s_items)
        story.append(Paragraph(f"<b>{cat_label}:</b> {skill_str}", body_style))
        story.append(Spacer(1, 2))

    # 5. Experience
    add_section_divider("EXPERIENCE")
    for exp in profile.get("experience", []):
        header_text = f"<b>{exp.get('role')}</b> &mdash; <i>{exp.get('company')}, {exp.get('location')}</i> <font color='#555555'>({exp.get('period')})</font>"
        story.append(Paragraph(header_text, body_style))
        story.append(Spacer(1, 2))
        for hl in exp.get("highlights", []):
            story.append(Paragraph(f"&bull; {hl}", bullet_style))
        story.append(Spacer(1, 4))

    # 6. Projects
    add_section_divider("PROJECTS")
    for proj in profile.get("projects", []):
        tech_str = ", ".join(proj.get("tech_stack", []))
        proj_hdr = f"<b>{proj.get('name')}</b> <font color='#555555'>({proj.get('period')})</font> &mdash; <i>[{tech_str}]</i>"
        story.append(Paragraph(proj_hdr, body_style))
        story.append(Spacer(1, 2))
        for hl in proj.get("highlights", []):
            story.append(Paragraph(f"&bull; {hl}", bullet_style))
        story.append(Spacer(1, 4))

    # Build the PDF
    doc.build(story)


def tailor_resume_if_needed(
    job_text: str,
    company: str = "Target Company",
    role: str = "AI Engineer",
    force_tailor: bool = False
) -> Dict[str, Any]:
    """
    Evaluates whether the resume should be tailored to the JD.
    If needed or forced, generates a newly customized PDF resume.
    Otherwise, returns the default resume.
    """
    profile = load_profile()
    match_result = match_job(job_text, profile)

    tailoring_needed = match_result["tailoring_needed"] or force_tailor

    if not tailoring_needed and not force_tailor and DEFAULT_RESUME_PATH.exists():
        return {
            "tailored": False,
            "resume_path": DEFAULT_RESUME_PATH,
            "filename": DEFAULT_RESUME_PATH.name,
            "reason": "Default resume has strong ATS alignment. No modification required.",
            "match_result": match_result,
        }

    # Generate tailored components
    tailored_objective = generate_tailored_objective(role, company, match_result["matched_skills"])
    tailored_skills = order_skills_for_jd(profile.get("skills", {}), match_result["all_jd_skills"])

    clean_company = re.sub(r"[^\w\-]", "_", company).strip("_")
    clean_role = re.sub(r"[^\w\-]", "_", role).strip("_")
    output_filename = f"Naveena_Resume_{clean_company}_{clean_role}.pdf"
    output_pdf_path = RESUMES_DIR / output_filename

    build_pdf_resume(profile, tailored_objective, tailored_skills, output_pdf_path)

    return {
        "tailored": True,
        "resume_path": output_pdf_path,
        "filename": output_filename,
        "reason": f"Tailored resume generated for {role} at {company} to maximize ATS keyword alignment.",
        "tailored_objective": tailored_objective,
        "tailored_skills": tailored_skills,
        "match_result": match_result,
    }

