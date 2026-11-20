"""
Email Outreach Module.
Crafts tailored job application emails, generates subjects and body pitches,
attaches the resume (original or tailored), and sends through Gmail SMTP with preview/dry-run safety.
"""

import os
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Any, Optional
from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_NAME, GMAIL_APP_PASSWORD, DEFAULT_RESUME_PATH
from core.profile_loader import load_profile


def draft_application_email(
    company: str,
    role: str,
    recipient_email: str,
    matched_skills: Optional[list] = None,
    custom_pitch: Optional[str] = None
) -> Dict[str, str]:
    """
    Drafts a personalized, high-conversion cold outreach email for a job opening.
    """
    profile = load_profile()
    name = profile.get("name", "Naveena N")
    phone = profile.get("phone", "+91 6379595692")
    email = profile.get("email", "navirajan2003@gmail.com")
    location = profile.get("location", "Bangalore, India")
    linkedin = profile.get("linkedin", "https://linkedin.com")
    github = profile.get("github", "https://github.com")

    top_skills = ", ".join([s.title() for s in (matched_skills or ["LangGraph", "RAG", "FastAPI", "Docker"])[:4]])

    subject = f"Application for {role} - {name} (GenAI & MLOps | IIT Madras BS)"

    if custom_pitch:
        pitch_section = custom_pitch
    else:
        pitch_section = (
            f"I came across your opening for the {role} role at {company} and would love to explore how I can add immediate value.\n\n"
            f"Currently, I work as an Associate (Data Science) at MResult Technologies in Bangalore with 1.5+ years of experience "
            f"shipping production AI systems. My core expertise spans:\n"
            f"• Agentic AI & RAG: Built autonomous multi-agent analytics systems (ReAct, LangGraph, LlamaIndex, MCP) and RAG workflows with pgvector/ChromaDB.\n"
            f"• Production ML & Document Intelligence: Developed FastAPI microservices, CV extraction pipelines, and automated LLM evaluation suites.\n"
            f"• MLOps & Cloud: Containerized deployment with Docker, MLflow tracking, and AWS/GCP (Vertex AI) workflows.\n\n"
            f"I am also pursuing a Bachelor of Science in Data Science and its Applications from IIT Madras."
        )

    body = f"""Dear {company} Hiring Team,

{pitch_section}

I have attached my updated resume for your review. I would welcome the opportunity to discuss how my hands-on background with {top_skills} aligns with your team's roadmap.

Thank you for your time and consideration.

Best regards,

{name}
AI/ML Engineer
Phone: {phone}
Email: {email}
Location: {location}
LinkedIn: {linkedin}
GitHub: {github}
"""
    return {
        "subject": subject,
        "body": body,
        "recipient": recipient_email
    }


def send_application_email(
    recipient_email: str,
    subject: str,
    body: str,
    attachment_path: Optional[Path] = None,
    dry_run: bool = False,
    app_password: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends an email with attachment via Gmail SMTP.
    If dry_run is True, verifies the message configuration without dispatching network calls.
    """
    password = app_password or GMAIL_APP_PASSWORD or os.getenv("GMAIL_APP_PASSWORD", "")
    if password:
        password = password.replace(" ", "").strip()
    resume_file = attachment_path or DEFAULT_RESUME_PATH

    if not resume_file.exists():
        return {
            "success": False,
            "error": f"Resume attachment file does not exist at: {resume_file}"
        }

    if not recipient_email or "@" not in recipient_email:
        return {
            "success": False,
            "error": f"Invalid recipient email address: '{recipient_email}'"
        }

    # Dry-Run mode: Safety verification without sending real network packets
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"[DRY-RUN VERIFIED] Ready to send to {recipient_email}. Attachment: {resume_file.name} ({resume_file.stat().st_size} bytes).",
            "recipient": recipient_email,
            "subject": subject,
            "attachment": str(resume_file)
        }

    if not password:
        return {
            "success": False,
            "error": (
                "Gmail App Password not found. "
                "To send emails from your Gmail account, generate a 16-character App Password at "
                "https://myaccount.google.com/apppasswords and provide it in your .env or the copilot UI."
            )
        }

    # Build MIME message
    msg = MIMEMultipart()
    msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"] = recipient_email
    msg["Subject"] = subject

    # Attach Body
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Attach PDF Resume
    try:
        with open(resume_file, "rb") as f:
            part = MIMEApplication(f.read(), Name=resume_file.name)
            part["Content-Disposition"] = f'attachment; filename="{resume_file.name}"'
            msg.attach(part)
    except Exception as e:
        return {"success": False, "error": f"Failed to attach resume file: {e}"}

    # Dispatch via SMTP
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SENDER_EMAIL, password)
            server.send_message(msg)

        return {
            "success": True,
            "dry_run": False,
            "message": f"Successfully sent application email to {recipient_email} with attachment {resume_file.name}!",
            "recipient": recipient_email,
            "subject": subject,
            "attachment": str(resume_file)
        }
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "Authentication failed: Please check your Gmail App Password. Standard Gmail passwords are not supported by Google for SMTP; generate an App Password at https://myaccount.google.com/apppasswords"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"SMTP Error while sending email: {str(e)}"
        }

