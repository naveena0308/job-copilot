"""
Outreach and Messaging Generator module.
Crafts LinkedIn connection notes (strictly <= 300 characters),
InMails, and customized cover letters.
"""

from typing import Dict, Any, List, Optional
from core.profile_loader import load_profile


def generate_connection_note(company: str, role: str) -> str:
    """
    Generate a LinkedIn connection request note strictly under 300 characters.
    """
    note = (
        f"Hi! Noticed the {role} opening at {company}. "
        f"I'm an AI Engineer with 1.5 yrs exp shipping agentic LLM systems, RAG, and MLOps at MResult Tech & studying BS Data Science at IIT Madras. "
        f"Would love to connect and follow your team's work!"
    )
    if len(note) > 298:
        note = (
            f"Hi! Saw the {role} role at {company}. "
            f"I'm an AI Engineer with 1.5y exp in GenAI, LangGraph, RAG & MLOps (IIT Madras BS). "
            f"Would love to connect!"
        )
    return note


def generate_inmail(company: str, role: str, contact_name: Optional[str] = None) -> str:
    """
    Generate a LinkedIn InMail or direct message.
    """
    salutation = f"Hi {contact_name}," if contact_name else "Hi there,"
    return f"""{salutation}

I came across your team's work and the open {role} role at {company}.

I am an AI/ML Engineer (Associate at MResult Technologies) and IIT Madras BS Data Science student with 1.5+ years of production experience in:
• Agentic AI & RAG: Built autonomous agent engines using LangGraph, LlamaIndex, ReAct, and pgvector.
• MLOps & Production: Containerized deployment with Docker, FastAPI, and MLflow experiment tracking on AWS/GCP.
• Document Intelligence: Reduced manual processing by 95% via multimodal CV pipelines.

Given {company}'s focus on cutting-edge AI, I would love to connect and see if my background is a fit for your team.

Best regards,
Naveena N
navirajan2003@gmail.com | +91 6379595692
"""


def generate_cover_letter(company: str, role: str, matched_skills: Optional[List[str]] = None) -> str:
    """
    Generate a tailored, professional cover letter.
    """
    profile = load_profile()
    name = profile.get("name", "Naveena N")
    email = profile.get("email", "navirajan2003@gmail.com")
    phone = profile.get("phone", "+91 6379595692")
    skills_list = ", ".join([s.title() for s in (matched_skills or ["LangGraph", "FastAPI", "Docker", "PyTorch"])[:4]])

    return f"""Naveena N
Bangalore, Karnataka, India
{phone} | {email}

To:
Hiring Team at {company}

Subject: Application for {role}

Dear Hiring Team,

I am writing to express my strong enthusiasm for the {role} position at {company}. With 1.5+ years of hands-on experience building autonomous agentic AI systems, RAG pipelines, and end-to-end ML architectures in Python, I am eager to bring my practical engineering mindset to your team.

In my current role as Associate (Data Science) at MResult Technologies, I engineered the GnA Intelligence Engine—an agentic analytics platform built on ReAct and LlamaIndex and deployed on AWS EC2 via FastAPI. Furthermore, I developed FinSight AI, a multi-agent financial budget analyst using LangGraph, Neon Postgres, pgvector, and Model Context Protocol (MCP) servers, backed by automated dual-LLM failover and 95.6% benchmark precision.

My technical foundation is strengthened by my dual academic background: a Bachelor of Science in Data Science and its Applications from IIT Madras and a Bachelor of Technology in AI & Data Science from Jeppiaar Institute of Technology. I take pride in adhering to rigorous MLOps practices, including MLflow tracking, Docker containerization, and robust CI/CD pipelines.

I am particularly excited about {company} because of your ambitious vision and technological momentum. I am confident that my technical skills in {skills_list} and my drive for tangible AI impact will allow me to hit the ground running.

Thank you for your consideration. I look forward to the possibility of discussing this role in detail.

Sincerely,

{name}
"""

