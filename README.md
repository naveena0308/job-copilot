# 💼 LinkedIn Job Copilot

An intelligent, end-to-end automation copilot built for **Naveena N** (AI/ML & Generative AI Engineer) to:
1. **Discover LinkedIn Hiring Posts with Recruiter Emails:** Live search for posts where recruiters/founders post job openings and request email applications.
2. **ATS Fit & Gap Analysis:** Calculate match score (0-100%), skill overlaps, missing keywords, and experience alignment.
3. **Smart Resume Tailoring (Only When Needed):** Evaluates if the JD requires customization; if so, re-aligns the objective statement, reorganizes skills by relevance, and compiles a clean, ATS-optimized PDF resume using ReportLab.
4. **Automated Gmail Outreach:** Drafts and dispatches personalized, high-converting application emails through your Gmail account with the resume attached (with Dry-Run safety mode).
5. **Easy Apply Screening Q&A Auto-Filler:** Answers screening questions instantly (experience with specific frameworks, notice period, location, citizenship, education).
6. **Application Tracker:** Persists applied roles, tailored resumes, and statuses in `tracker.json`.

---

## 🚀 Quickstart

### 1. Launch the Interactive Web Dashboard (Streamlit)
```bash
python -m streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

### 2. Or Use the Terminal CLI (`cli.py`)

#### 🔍 Search LinkedIn Hiring Posts with Emails:
```bash
python cli.py search "Generative AI Engineer" --location "Bangalore"
```

#### 🎯 Match Job Description against Profile:
```bash
python cli.py match --file sample_job.txt
```

#### 📄 Check & Generate Tailored Resume (Only If Needed):
```bash
python cli.py tailor --file sample_job.txt --company "InnovateAI Labs" --role "Agentic ML Engineer"
```

#### ✉️ Preview & Send Application Email:
```bash
# Preview mode (Dry-run, zero network risk):
python cli.py email careers@innovateailabs.com --company "InnovateAI Labs" --role "Agentic ML Engineer"

# Live dispatch (with Gmail App Password configured):
python cli.py email careers@innovateailabs.com --company "InnovateAI Labs" --role "Agentic ML Engineer" --send
```

#### 📝 Answer Screening Questions:
```bash
python cli.py qa "How many years of work experience do you have with LangGraph?"
python cli.py qa "What is your notice period?"
```

#### 📊 View Application Tracker:
```bash
python cli.py tracker
```

---

## ⚙️ Configuration & Gmail Setup

To send live emails directly from `navirajan2003@gmail.com`:
1. Go to your Google Account: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
2. Generate a 16-character **App Password** (name it e.g. "JobCopilot").
3. Create a `.env` file in the root directory (or enter it in the Streamlit sidebar):
   ```env
   SENDER_EMAIL=navirajan2003@gmail.com
   GMAIL_APP_PASSWORD=your_16_digit_app_password
   ```

> [!NOTE]
> By default, the system runs in **Dry-Run Mode**, which verifies email structure, recipient validity, and PDF attachments before any real email is sent.

---

## 📁 Project Structure

```
linkedin-job-copilot/
├── profile.json                      <- User profile, skills, experience, projects, target roles
├── Naveena_s_Resume___27_10_2026.pdf <- Original PDF resume
├── config.py                         <- Settings, skill taxonomy, paths, weights
├── sample_job.txt                    <- Sample realistic job description for testing
├── tracker.json                      <- Application pipeline and status tracker
├── generated_resumes/                <- Directory where tailored PDF resumes are stored
├── core/
│   ├── __init__.py
│   ├── profile_loader.py             <- Normalized profile query & parser
│   ├── post_hunter.py                <- Searches LinkedIn hiring posts & extracts emails
│   ├── matcher.py                    <- ATS Matcher, gap analyzer & tailoring advisor
│   ├── resume_tailorer.py            <- Dynamic Resume Tailorer & ReportLab PDF compiler
│   ├── mailer.py                     <- High-converting email drafter & Gmail SMTP dispatcher
│   ├── qa_generator.py               <- LinkedIn Easy Apply screening answer engine
│   ├── outreach_generator.py         <- Connection notes (<=300 chars), InMails, cover letters
│   └── tracker.py                    <- Application state persistence
├── cli.py                            <- Rich Terminal CLI
├── app.py                            <- Interactive Streamlit Web Dashboard
├── .env.example                      <- Template for credentials
└── README.md                         <- Project documentation
```

