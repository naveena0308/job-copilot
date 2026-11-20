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



def generate_referral_request(company: str, role: str, contact_name: Optional[str] = None, job_ref: Optional[str] = None) -> str:
    """
    Generate a high-converting message requesting an internal referral from an employee.
    """
    salutation = f"Hi {contact_name}," if contact_name else "Hi there,"
    ref_mention = f" (Job Ref: {job_ref})" if job_ref else ""
    return f"""{salutation}

I hope you're doing well!

I noticed {company} is expanding its Generative AI engineering division and currently has an opening for the {role} role{ref_mention}. 

I am currently working as an Associate (Data Science) at MResult Technologies with 1.5+ years of experience building production RAG pipelines, LLM orchestration (LangChain, LlamaIndex, pgvector), and FastAPI microservices. I am also pursuing my B.S. in Data Science from IIT Madras.

Given my direct alignment with the required stack, would you be open to referring me internally or pointing me to the hiring manager for this role?

I would be happy to share my tailored resume and project links to make the referral quick and effortless for you.

Thank you so much for your time!

Best regards,
Naveena N
Phone: +91 6379595692 | Email: navirajan2003@gmail.com
"""


def generate_founder_pitch(company: str, role: str, founder_name: str = "Subra") -> str:
    """
    Generate a concise, high-signal direct pitch for founders/CEOs.
    """
    return f"""Dear {founder_name},

I've been following {company}'s growth in enterprise AI and agentic platforms. I noticed your team is currently scaling its GenAI division and hiring for the {role} position in Chennai.

As an AI/ML Engineer (Associate at MResult Tech) and IIT Madras BS Data Science student with 1.5+ years of production experience shipping RAG pipelines (pgvector, LangChain, LlamaIndex) and autonomous agents, I'd love to contribute directly to building robust AI services at {company}.

I've submitted my application via your careers portal (Job Ref: 4RR955X7). I would welcome the chance to share how my hands-on background can add immediate value to your engineering team.

Best regards,
Naveena N (+91 6379595692 | navirajan2003@gmail.com)
"""


def get_linkedin_people_search_url(company: str, title_keyword: str = "") -> str:
    """
    Generate direct LinkedIn people search URL for a company and target role.
    """
    import urllib.parse
    query = f"{company} {title_keyword}".strip()
    encoded = urllib.parse.quote(query)
    return f"https://www.linkedin.com/search/results/people/?keywords={encoded}&origin=GLOBAL_SEARCH_HEADER"
