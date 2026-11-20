"""
Command Line Interface (CLI) for LinkedIn Job Copilot.
Execute search, match analysis, resume tailoring, and email outreach from the terminal.
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.profile_loader import load_profile
from core.post_hunter import search_hiring_posts, parse_pasted_post, extract_emails
from core.matcher import match_job
from core.resume_tailorer import tailor_resume_if_needed
from core.mailer import draft_application_email, send_application_email
from core.qa_generator import answer_screening_question
from core.tracker import load_tracker, add_application, update_status

console = Console()


def cmd_search(args):
    """Search LinkedIn posts for job openings with emails."""
    console.print(f"[bold cyan]🔍 Searching LinkedIn posts for:[/bold cyan] [green]{args.role}[/green] in [yellow]{args.location}[/yellow]...")
    posts = search_hiring_posts(role=args.role, location=args.location, max_results=args.max_results)

    if not posts:
        console.print("[yellow]No posts found matching the criteria. Try broadening role or location keywords.[/yellow]")
        return

    table = Table(title=f"Discovered Job Openings ({len(posts)} found)", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Company / Role", style="bold green")
    table.add_column("Extracted Email", style="bold yellow")
    table.add_column("Snippet Preview", style="white")

    for idx, p in enumerate(posts, 1):
        email_str = ", ".join(p["emails"]) if p["emails"] else "[dim]No email in snippet[/dim]"
        comp_role = f"{p['company']}\n[dim]{p['role']}[/dim]"
        snippet = (p["snippet"][:130] + "...") if len(p["snippet"]) > 130 else p["snippet"]
        table.add_row(str(idx), comp_role, email_str, snippet)

    console.print(table)
    console.print("[dim]Tip: Use 'python cli.py email <email> --company <comp> --role <role>' to send outreach![/dim]")


def cmd_match(args):
    """Match job description and compute ATS fit score."""
    job_text = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[red]Error: File not found: {args.file}[/red]")
            return
        job_text = file_path.read_text(encoding="utf-8")
    elif args.text:
        job_text = args.text
    else:
        console.print("[red]Please provide --file or --text[/red]")
        return

    profile = load_profile()
    res = match_job(job_text, profile)

    score = res["ats_score"]
    color = "green" if score >= 80 else "yellow" if score >= 65 else "red"

    panel_text = (
        f"[bold]ATS Match Score:[/bold] [{color}]{score}%[/{color}]\n"
        f"[bold]Role Fit:[/bold] {res['role_relevance']['matched_role']}\n"
        f"[bold]Experience Fit:[/bold] {res['experience_fit']['status']}\n\n"
        f"[bold]Matched Skills ({len(res['matched_skills'])}):[/bold] {', '.join(res['matched_skills']) or 'None'}\n"
        f"[bold]Missing / Gap Skills ({len(res['missing_skills'])}):[/bold] {', '.join(res['missing_skills']) or 'None'}\n\n"
        f"[bold]Tailoring Recommended:[/bold] {'[bold yellow]YES[/bold yellow]' if res['tailoring_needed'] else '[green]NO (Standard resume sufficient)[/green]'}\n"
    )
    for r in res["tailoring_reasons"]:
        panel_text += f"  • {r}\n"

    console.print(Panel(panel_text, title="🎯 ATS Match Analysis", border_style="cyan"))


def cmd_tailor(args):
    """Check if resume needs tailoring and compile customized PDF."""
    job_text = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[red]Error: File not found: {args.file}[/red]")
            return
        job_text = file_path.read_text(encoding="utf-8")
    elif args.text:
        job_text = args.text
    else:
        console.print("[red]Please provide --file or --text[/red]")
        return

    res = tailor_resume_if_needed(job_text, company=args.company, role=args.role, force_tailor=args.force)

    if res["tailored"]:
        console.print(f"[bold green]✨ Tailored Resume Generated![/bold green]")
        console.print(f"[cyan]Saved to:[/cyan] [bold]{res['resume_path']}[/bold]")
        console.print(f"[yellow]Reason:[/yellow] {res['reason']}")
    else:
        console.print(f"[bold green]✓ Default Resume is Already Optimal![/bold green]")
        console.print(f"[cyan]Using:[/cyan] {res['resume_path']}")
        console.print(f"[dim]{res['reason']}[/dim]")


def cmd_email(args):
    """Draft and send application email with resume attachment."""
    parsed_meta = extract_emails(args.to)
    recipient = parsed_meta[0] if parsed_meta else args.to

    draft = draft_application_email(
        company=args.company,
        role=args.role,
        recipient_email=recipient
    )

    console.print(Panel(
        f"[bold]To:[/bold] {draft['recipient']}\n"
        f"[bold]Subject:[/bold] {draft['subject']}\n\n"
        f"{draft['body']}",
        title="✉️ Email Preview",
        border_style="magenta"
    ))

    attachment = Path(args.attachment) if args.attachment else None
    dry_run = not args.send  # Defaults to dry-run safety unless --send is passed

    result = send_application_email(
        recipient_email=draft["recipient"],
        subject=draft["subject"],
        body=draft["body"],
        attachment_path=attachment,
        dry_run=dry_run
    )

    if result.get("success"):
        console.print(f"[bold green]{result.get('message')}[/bold green]")
        # Track application
        add_application(
            company=args.company,
            role=args.role,
            recipient_email=recipient,
            status="Emailed" if not dry_run else "Previewed"
        )
    else:
        console.print(f"[bold red]Failed: {result.get('error')}[/bold red]")


def cmd_qa(args):
    """Answer screening question."""
    profile = load_profile()
    ans = answer_screening_question(args.question, profile)
    console.print(f"[bold cyan]Q:[/bold cyan] {ans['question']}")
    console.print(f"[bold green]A:[/bold green] [bold]{ans['answer']}[/bold]")
    console.print(f"[dim]Rationale: {ans['explanation']}[/dim]")


def cmd_tracker(args):
    """View application tracker records."""
    records = load_tracker()
    if not records:
        console.print("[yellow]Tracker is currently empty. Analyze or email jobs to track them![/yellow]")
        return

    table = Table(title="📊 Job Applications Tracker", show_lines=True)
    table.add_column("ID", width=4)
    table.add_column("Company", style="bold green")
    table.add_column("Role", style="cyan")
    table.add_column("Recipient Email", style="yellow")
    table.add_column("Status", style="magenta")
    table.add_column("Last Updated", style="dim")

    for r in records:
        table.add_row(
            str(r.get("id")),
            r.get("company", ""),
            r.get("role", ""),
            r.get("recipient_email", ""),
            r.get("status", ""),
            r.get("last_updated", "")
        )
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Job Copilot CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Search
    p_search = subparsers.add_parser("search", help="Search LinkedIn posts for job openings with emails")
    p_search.add_argument("role", nargs="?", default="Generative AI Engineer", help="Job role title")
    p_search.add_argument("--location", default="Bangalore", help="Location (e.g. Bangalore, Remote, India)")
    p_search.add_argument("--max-results", type=int, default=8, help="Max results to fetch")

    # Match
    p_match = subparsers.add_parser("match", help="Match job description against profile")
    p_match.add_argument("--file", help="Path to job description text file")
    p_match.add_argument("--text", help="Raw job description text")

    # Tailor
    p_tailor = subparsers.add_parser("tailor", help="Tailor resume to JD if needed")
    p_tailor.add_argument("--file", help="Path to job description text file")
    p_tailor.add_argument("--text", help="Raw job description text")
    p_tailor.add_argument("--company", default="Target Company", help="Company name")
    p_tailor.add_argument("--role", default="AI/ML Engineer", help="Role title")
    p_tailor.add_argument("--force", action="store_true", help="Force generate tailored resume even if score is high")

    # Email
    p_email = subparsers.add_parser("email", help="Draft and send outreach email")
    p_email.add_argument("to", help="Recipient email address")
    p_email.add_argument("--company", default="Hiring Team", help="Company name")
    p_email.add_argument("--role", default="AI/ML Engineer", help="Job title")
    p_email.add_argument("--attachment", help="Path to specific resume PDF")
    p_email.add_argument("--send", action="store_true", help="Send actual email (defaults to dry-run preview)")

    # QA
    p_qa = subparsers.add_parser("qa", help="Answer screening question")
    p_qa.add_argument("question", help="Screening question string")

    # Tracker
    p_track = subparsers.add_parser("tracker", help="View tracker records")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "match":
        cmd_match(args)
    elif args.command == "tailor":
        cmd_tailor(args)
    elif args.command == "email":
        cmd_email(args)
    elif args.command == "qa":
        cmd_qa(args)
    elif args.command == "tracker":
        cmd_tracker(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

