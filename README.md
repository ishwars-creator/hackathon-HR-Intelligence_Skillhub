# 🧠 SkillsHub — AI-Powered Skills Intelligence Platform

> Built for the hackathon: Claude-powered resume extraction + semantic natural language talent search.

---

## 🚀 Quick Setup (5 minutes)

### 1. Prerequisites
- Python 3.10+ installed
- Git installed
- An OpenRouter API key → get one free at https://openrouter.ai/keys

### 2. Clone & Install

```bash
git clone <your-repo-url>
cd skillshub
pip install -r requirements.txt
```

### 3. Set your API key

**Option A — Create a `.env` file** (recommended):
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Option B — Set environment variable directly:**
```bash
# Mac/Linux:
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Windows:
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 4. Run the app

```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## 🔑 Demo Login Credentials

| Role | Email | Password |
|------|-------|----------|
| HR Admin | hr@company.com | hr123 |
| Employee | rahul.sharma@company.com | emp123 |
| Employee | priya.menon@company.com | emp123 |
| Employee | sneha.patil@company.com | emp123 |

---

## ✨ Features

### Hard Problem #1 — Smart Profile Ingestion
- Upload a PDF resume OR paste plain text
- Claude extracts: skills, proficiency levels, years of experience, projects, certifications
- Claude infers related skills (e.g. Next.js → React automatically inferred)
- Extracted profiles land in a **review queue** — HR approves before adding to database
- HR can adjust proficiency levels during review

### Hard Problem #2 — Semantic Natural Language Search
- HR types a real-world query in plain English
- Claude semantically understands intent (not just keywords)
- Returns **ranked results with match scores (0–100%)** and **plain-English explanations**
- Example queries built in for demo

### Core Features
- ✅ Role-based access (HR vs Employee separate experiences)
- ✅ 15 pre-seeded realistic employee profiles for demo
- ✅ Employee directory with filters (location, availability, department)
- ✅ Full profile view with skills by category, projects, certifications
- ✅ Employee self-service: view/edit own profile, add skills, update availability
- ✅ HR dashboard with company-wide stats and top skills

---

## 🏗 Architecture

```
skillshub/
├── app.py              # Main Streamlit app, login, routing
├── requirements.txt
├── data/
│   ├── seed_data.py    # 15 realistic employee profiles + test users
│   └── db.json         # Auto-created JSON database (persistent)
├── utils/
│   ├── db.py           # All database operations
│   └── claude_ai.py    # Claude API calls (extraction + search)
└── pages/
    ├── dashboard.py    # HR dashboard
    ├── search.py       # Natural language search
    ├── directory.py    # Employee directory
    ├── review_queue.py # HR review & approval
    ├── upload.py       # Resume upload & extraction
    └── my_profile.py   # Employee profile view
```

**Tech stack:**
- **Frontend/UI:** Streamlit (Python)
- **AI:** OpenRouter (meta-llama/llama-3.3-70b-instruct) for extraction & search
- **Database:** JSON file (no setup needed)
- **PDF parsing:** pypdf

---

## 🎯 Demo Flow (for judges)

1. **Login as HR** → see dashboard with 15 pre-seeded employees
2. **Search Talent** → try: *"Who can lead a React project with WebSocket experience?"*
3. See ranked results with match scores and explanations
4. **Go to Upload Resume** → paste a sample resume → watch Claude extract skills in ~10s
5. **Review Queue** → approve the extracted profile (adjust proficiency if needed)
6. **Login as Employee** → see personal profile, edit availability, add skills

---

## 🔮 What's Next (stretch goals not yet built)
- Team builder mode (describe a project, get a team recommendation)
- Skill gap analysis across the company
- Conversational search (refine results in chat)
- GitHub integration (infer skills from public repos)
- Bulk CSV import
