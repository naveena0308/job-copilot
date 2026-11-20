"""
LinkedIn Job Copilot - Streamlit Web Dashboard
Interactive web interface for job post hunting, ATS matching, dynamic resume tailoring,
automated email outreach via Gmail SMTP, screening question auto-filling, and application tracking.
"""

import streamlit as st
import os
import json
from pathlib import Path

from config import (
    PROFILE_PATH,
    DEFAULT_RESUME_PATH,
    RESUMES_DIR,
    SENDER_EMAIL,
    SENDER_NAME,
    GMAIL_APP_PASSWORD,
    DEFAULT_TARGET_ROLES,
    DEFAULT_LOCATIONS,
)
from core.profile_loader import load_profile, save_profile, get_flattened_skills
from core.post_hunter import search_hiring_posts, parse_pasted_post, extract_emails
from core.matcher import match_job
from core.resume_tailorer import tailor_resume_if_needed
from core.mailer import draft_application_email, send_application_email
from core.qa_generator import answer_screening_question, batch_answer_questions
from core.outreach_generator import generate_connection_note, generate_inmail, generate_cover_letter
from core.tracker import load_tracker, add_application, update_status

# Page setup
st.set_page_config(
    page_title="LinkedIn Job Copilot | Naveena N",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load candidate profile
profile = load_profile()

# Initialize session state variables
if "selected_job" not in st.session_state:
    st.session_state.selected_job = {
        "company": "InnovateAI Labs",
        "role": "Generative AI & Agentic ML Engineer",
        "email": "careers@innovateailabs.com",
        "text": ""
    }
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "tailored_result" not in st.session_state:
    st.session_state.tailored_result = None

# If session state text is empty, load sample job
if not st.session_state.selected_job["text"]:
    sample_file = Path("sample_job.txt")
    if sample_file.exists():
        st.session_state.selected_job["text"] = sample_file.read_text(encoding="utf-8")

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("💼 LinkedIn Job Copilot")
    st.markdown(f"**Candidate:** {profile.get('name', 'Naveena N')}")
    st.markdown(f"**Current Role:** {profile.get('current_role', 'Associate (Data Science)')}")
    st.markdown(f"**Experience:** {profile.get('experience_years', 1.5)} years")
    st.markdown(f"**Education:** IIT Madras BS & JIT B.Tech")

    st.markdown("---")
    st.subheader("⚙️ Gmail Outreach Settings")
    smtp_email = st.text_input("Sender Gmail", value=SENDER_EMAIL, disabled=True)
    app_pwd_input = st.text_input(
        "Gmail App Password",
        value=GMAIL_APP_PASSWORD,
        type="password",
        help="16-character Google App Password generated at myaccount.google.com/apppasswords"
    )
    if app_pwd_input:
        st.session_state["active_app_password"] = app_pwd_input
        st.success("App Password configured")
    else:
        st.info("Tip: Enter App Password to enable live email sending, or use Dry-Run mode.")

    st.markdown("---")
    st.subheader("📄 Resume Status")
    if DEFAULT_RESUME_PATH.exists():
        st.success(f"Default: {DEFAULT_RESUME_PATH.name}")
    else:
        st.warning("Default resume PDF not found!")

# ----------------- MAIN TABS -----------------
tabs = st.tabs([
    "🔍 Find Hiring Posts",
    "🎯 ATS Matcher & Fit",
    "📄 Smart Resume Tailorer",
    "✉️ Email Outreach",
    "📝 Screening Q&A",
    "📊 Application Tracker",
    "👤 Profile & Settings"
])

# ================= TAB 1: FIND HIRING POSTS =================
with tabs[0]:
    st.header("🔍 Search LinkedIn Hiring Posts with Emails")
    st.markdown(
        "Automatically discovers public LinkedIn posts where recruiters or founders posted job openings and requested email applications."
    )

    col1, col2, col3, col4 = st.columns([3, 2, 2, 1.5])
    with col1:
        search_role = st.selectbox("Target Role", options=DEFAULT_TARGET_ROLES + ["Custom..."])
        if search_role == "Custom...":
            search_role = st.text_input("Enter custom role keyword", value="Generative AI")
    with col2:
        search_loc = st.selectbox("Location", options=DEFAULT_LOCATIONS)
    with col3:
        search_kw = st.text_input("Extra Filter", value="email OR 'send resume'")
    with col4:
        st.write("")
        st.write("")
        btn_search = st.button("🔎 Search Posts", use_container_width=True, type="primary")

    if btn_search:
        with st.spinner("Searching LinkedIn posts via DuckDuckGo..."):
            st.session_state.search_results = search_hiring_posts(
                role=search_role,
                location=search_loc,
                keywords=search_kw,
                max_results=8
            )

    results = st.session_state.search_results
    if results:
        st.subheader(f"Found {len(results)} Hiring Posts")
        for i, post in enumerate(results):
            with st.expander(f"📌 {post['role']} at {post['company']} — {post['title'][:70]}...", expanded=(i == 0)):
                col_info, col_act = st.columns([4, 1.5])
                with col_info:
                    st.markdown(f"**URL:** [{post['url']}]({post['url']})" if post['url'] else "")
                    emails = post.get("emails", [])
                    if emails:
                        st.markdown(f"**📧 Extracted Email(s):** `{', '.join(emails)}`")
                    else:
                        st.markdown("**📧 Extracted Email:** *No explicit email found in snippet; see post link*")
                    st.markdown(f"**Snippet:**\n> {post['snippet']}")

                with col_act:
                    if st.button("🚀 Load into Copilot", key=f"load_post_{i}", use_container_width=True):
                        st.session_state.selected_job["company"] = post["company"]
                        st.session_state.selected_job["role"] = post["role"]
                        st.session_state.selected_job["email"] = emails[0] if emails else ""
                        st.session_state.selected_job["text"] = f"{post['title']}\n\n{post['snippet']}"
                        st.success(f"Loaded '{post['role']} at {post['company']}'! Go to Tab 2 or 4.")
                        st.rerun()

    st.markdown("---")
    st.subheader("📋 Or Paste a LinkedIn Post / Job Description Directly")
    pasted_input = st.text_area("Paste raw text from LinkedIn post or JD", height=150, placeholder="Paste job description or recruiter hiring post text here...")
    col_p1, col_p2, col_p3 = st.columns([2, 2, 1.5])
    with col_p1:
        custom_comp = st.text_input("Company (optional override)", placeholder="e.g. Acme Corp")
    with col_p2:
        custom_pos = st.text_input("Role (optional override)", placeholder="e.g. AI Engineer")
    with col_p3:
        st.write("")
        st.write("")
        if st.button("Parse & Load Text", use_container_width=True):
            if pasted_input.strip():
                parsed = parse_pasted_post(pasted_input, custom_comp or None, custom_pos or None)
                st.session_state.selected_job["company"] = parsed["company"]
                st.session_state.selected_job["role"] = parsed["role"]
                st.session_state.selected_job["email"] = parsed["emails"][0] if parsed["emails"] else ""
                st.session_state.selected_job["text"] = pasted_input
                st.success(f"Parsed & Loaded for {parsed['company']}! Check Matcher or Email Outreach tabs.")
                st.rerun()

# ================= TAB 2: ATS MATCHER & FIT =================
with tabs[1]:
    st.header("🎯 ATS Job Match & Skill Gap Analyzer")

    col_target1, col_target2 = st.columns(2)
    with col_target1:
        active_comp = st.text_input("Company Name", value=st.session_state.selected_job["company"])
        st.session_state.selected_job["company"] = active_comp
    with col_target2:
        active_role = st.text_input("Role Title", value=st.session_state.selected_job["role"])
        st.session_state.selected_job["role"] = active_role

    active_jd_text = st.text_area("Active Job Description for Analysis", value=st.session_state.selected_job["text"], height=220)
    st.session_state.selected_job["text"] = active_jd_text

    if active_jd_text.strip():
        match_result = match_job(active_jd_text, profile)

        st.subheader("Match Overview")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            score = match_result["ats_score"]
            st.metric("ATS Match Score", f"{score}%", delta="Strong" if score >= 80 else "Moderate" if score >= 65 else "Low")
        with col_m2:
            st.metric("Matched Skills", len(match_result["matched_skills"]))
        with col_m3:
            st.metric("Missing Skills", len(match_result["missing_skills"]))
        with col_m4:
            st.metric("Experience Check", f"{profile.get('experience_years', 1.5)} yrs")

        st.info(f"**Experience Fit:** {match_result['experience_fit']['status']}")

        # Skills breakdown
        col_sk1, col_sk2 = st.columns(2)
        with col_sk1:
            st.markdown("#### ✅ Matched Skills in Profile")
            if match_result["matched_skills"]:
                chips = " ".join([f"`{s}`" for s in match_result["matched_skills"]])
                st.markdown(chips)
            else:
                st.write("No exact taxonomy skills detected.")

        with col_sk2:
            st.markdown("#### ⚠️ Keyword Gaps / Missing in JD")
            if match_result["missing_skills"]:
                chips_missing = " ".join([f"`{s}`" for s in match_result["missing_skills"]])
                st.markdown(chips_missing)
            else:
                st.write("No major skill gaps identified!")

        # Tailoring Verdict
        st.markdown("---")
        st.subheader("Resume Tailoring Assessment")
        if match_result["tailoring_needed"]:
            st.warning("⚡ **Tailoring Recommended for this JD**")
        else:
            st.success("✅ **Standard Resume is Optimal (No Tailoring Required)**")

        for r in match_result["tailoring_reasons"]:
            st.markdown(f"- {r}")

# ================= TAB 3: SMART RESUME TAILORER =================
with tabs[2]:
    st.header("📄 Dynamic Resume Tailorer & PDF Generator")
    st.markdown(
        "Analyzes whether this JD requires a customized resume. If needed or forced, "
        "it re-aligns the professional objective, reorganizes technical skills, and compiles an ATS-optimized PDF."
    )

    t_comp = st.session_state.selected_job["company"]
    t_role = st.session_state.selected_job["role"]
    t_jd = st.session_state.selected_job["text"]

    col_btn1, col_btn2 = st.columns([2, 2])
    with col_btn1:
        btn_eval_tailor = st.button("⚡ Generate Tailored Resume (If Needed)", type="primary", use_container_width=True)
    with col_btn2:
        btn_force_tailor = st.button("🔨 Force Generate Tailored PDF", use_container_width=True)

    if btn_eval_tailor or btn_force_tailor:
        if not t_jd.strip():
            st.error("Please provide a job description first in Tab 1 or 2.")
        else:
            force = True if btn_force_tailor else False
            with st.spinner("Analyzing JD and compiling ATS-optimized PDF..."):
                tailor_out = tailor_resume_if_needed(t_jd, company=t_comp, role=t_role, force_tailor=force)
                st.session_state.tailored_result = tailor_out

    tailor_data = st.session_state.tailored_result
    if tailor_data:
        st.markdown("---")
        if tailor_data.get("tailored"):
            st.success(f"🎉 **{tailor_data['reason']}**")
            st.markdown(f"**PDF File:** `{tailor_data['filename']}`")

            # Download button for generated PDF
            pdf_path = Path(tailor_data["resume_path"])
            if pdf_path.exists():
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label=f"⬇️ Download {tailor_data['filename']}",
                    data=pdf_bytes,
                    file_name=tailor_data["filename"],
                    mime="application/pdf",
                    use_container_width=True
                )

            # Preview tailored fields
            with st.expander("👁️ Preview Tailored Objective & Prioritized Skills", expanded=True):
                st.markdown("##### Tailored Objective:")
                st.info(tailor_data.get("tailored_objective", ""))
                st.markdown("##### Prioritized Skills Ranking:")
                for cat, sks in tailor_data.get("tailored_skills", {}).items():
                    st.markdown(f"**{cat.replace('_', ' ').title()}:** {', '.join(sks)}")
        else:
            st.info(f"ℹ️ {tailor_data['reason']}")
            st.markdown(f"**Using Default Resume:** `{tailor_data['filename']}`")
            if DEFAULT_RESUME_PATH.exists():
                with open(DEFAULT_RESUME_PATH, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download Default Resume ({DEFAULT_RESUME_PATH.name})",
                        data=f.read(),
                        file_name=DEFAULT_RESUME_PATH.name,
                        mime="application/pdf",
                        use_container_width=True
                    )

# ================= TAB 4: EMAIL OUTREACH =================
with tabs[3]:
    st.header("✉️ Automated Email Outreach via Gmail")
    st.markdown(
        "Sends a professional, tailored application email directly through your Gmail account with your resume attached."
    )

    o_comp = st.session_state.selected_job["company"]
    o_role = st.session_state.selected_job["role"]
    o_email = st.session_state.selected_job.get("email", "")

    col_e1, col_e2, col_e3 = st.columns([2.5, 2, 2])
    with col_e1:
        recipient_to = st.text_input("Recipient Email", value=o_email, placeholder="e.g. careers@company.com or recruiter@...")
    with col_e2:
        outreach_comp = st.text_input("Company", value=o_comp)
    with col_e3:
        outreach_role = st.text_input("Role", value=o_role)

    # Choose attachment
    tailor_data = st.session_state.tailored_result
    available_resumes = {}
    if DEFAULT_RESUME_PATH.exists():
        available_resumes[f"Default Resume ({DEFAULT_RESUME_PATH.name})"] = DEFAULT_RESUME_PATH
    if tailor_data and tailor_data.get("tailored") and Path(tailor_data["resume_path"]).exists():
        available_resumes[f"Tailored Resume ({tailor_data['filename']})"] = Path(tailor_data["resume_path"])

    selected_resume_label = st.selectbox("Select Resume Attachment", options=list(available_resumes.keys()) if available_resumes else ["None"])
    selected_attachment_path = available_resumes.get(selected_resume_label)

    # Draft email
    draft = draft_application_email(outreach_comp, outreach_role, recipient_to)

    col_sub, col_dry = st.columns([4, 1.5])
    with col_sub:
        edit_subject = st.text_input("Subject Line", value=draft["subject"])
    with col_dry:
        st.write("")
        st.write("")
        is_dry_run = st.checkbox("Dry-Run Safety Mode", value=True, help="When checked, simulates sending without dispatching real email.")

    edit_body = st.text_area("Email Body", value=draft["body"], height=280)

    col_send1, col_send2 = st.columns([2, 3])
    with col_send1:
        send_btn = st.button("🚀 Send Application Email", type="primary", use_container_width=True)

    if send_btn:
        active_pwd = st.session_state.get("active_app_password") or GMAIL_APP_PASSWORD
        with st.spinner("Processing email dispatch..."):
            send_res = send_application_email(
                recipient_email=recipient_to,
                subject=edit_subject,
                body=edit_body,
                attachment_path=selected_attachment_path,
                dry_run=is_dry_run,
                app_password=active_pwd
            )

        if send_res.get("success"):
            st.success(send_res.get("message"))
            # Track in application tracker
            add_application(
                company=outreach_comp,
                role=outreach_role,
                recipient_email=recipient_to,
                tailored_resume_path=str(selected_attachment_path) if selected_attachment_path else "",
                status="Emailed" if not is_dry_run else "Previewed/Tested"
            )
        else:
            st.error(send_res.get("error"))

    st.markdown("---")
    st.subheader("🔗 Additional LinkedIn Outreach Templates")
    tab_note, tab_inmail, tab_cl = st.tabs(["Connection Note (≤300 chars)", "Recruiter InMail", "Cover Letter"])
    with tab_note:
        c_note = generate_connection_note(outreach_comp, outreach_role)
        st.text_area("LinkedIn Connection Note", value=c_note, height=100)
        st.caption(f"Character count: {len(c_note)} / 300")
    with tab_inmail:
        inmail_text = generate_inmail(outreach_comp, outreach_role)
        st.text_area("LinkedIn InMail Pitch", value=inmail_text, height=220)
    with tab_cl:
        cover_text = generate_cover_letter(outreach_comp, outreach_role)
        st.text_area("Tailored Cover Letter", value=cover_text, height=280)

# ================= TAB 5: SCREENING Q&A =================
with tabs[4]:
    st.header("📝 LinkedIn Easy Apply Screening Auto-Filler")
    st.markdown("Instantly answer screening questions regarding experience, notice period, location, CTC, and tech skills.")

    qa_input = st.text_area(
        "Enter questions (one per line)",
        value="How many years of work experience do you have with LangGraph?\nWhat is your notice period?\nAre you willing to relocate to Bangalore?\nWhat is your current work authorization?",
        height=120
    )

    if st.button("⚡ Generate Answers", type="primary"):
        questions = [q.strip() for q in qa_input.splitlines() if q.strip()]
        answers = batch_answer_questions(questions)

        for a in answers:
            with st.container():
                st.markdown(f"**Question:** {a['question']}")
                col_ans, col_exp = st.columns([2, 4])
                with col_ans:
                    st.code(a['answer'], language=None)
                with col_exp:
                    st.caption(f"Rationale: {a['explanation']}")
                st.markdown("---")

# ================= TAB 6: APPLICATION TRACKER =================
with tabs[5]:
    st.header("📊 Application & Outreach Tracker")
    st.markdown("Track all discovered posts, tailored resumes, and outreach statuses.")

    tracker_records = load_tracker()

    if not tracker_records:
        st.info("No applications tracked yet. Use Tab 1 or 4 to start outreach!")
    else:
        st.dataframe(tracker_records, use_container_width=True)

        st.subheader("Update Application Status")
        col_t1, col_t2, col_t3 = st.columns([2, 2, 1.5])
        with col_t1:
            rec_ids = [r["id"] for r in tracker_records]
            selected_id = st.selectbox("Select Application ID", options=rec_ids)
        with col_t2:
            new_st = st.selectbox("New Status", options=["Discovered", "Tailored", "Emailed", "Interviewing", "Offer", "Rejected"])
        with col_t3:
            st.write("")
            st.write("")
            if st.button("Update Status", use_container_width=True):
                update_status(selected_id, new_st)
                st.success(f"Updated status of #{selected_id} to '{new_st}'!")
                st.rerun()

# ================= TAB 7: PROFILE & SETTINGS =================
with tabs[6]:
    st.header("👤 Profile & Screening Defaults")
    st.markdown("View or edit the structured information parsed from your resume.")

    st.json(profile)

    if st.button("💾 Save Profile Changes (if edited)", disabled=True):
        st.info("To edit profile details, update profile.json directly.")

