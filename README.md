# 🧠 SkillsHub — AI-Powered Skills Intelligence Platform

> Hackathon project: Upload a resume → Claude extracts skills automatically → HR searches talent in plain English.

**Live demo:** runs on `http://localhost:8501` after setup below.

---

## 📋 Table of Contents
- [Features](#-features)
- [Quick Start — Docker](#-quick-start--docker-recommended)
- [Quick Start — Local Python](#-quick-start--local-python)
- [Demo Credentials](#-demo-credentials)
- [Demo Flow](#-demo-flow-for-judges)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)

---

## ✨ Features

| Feature | Description |
|---|---|
| **AI Resume Extraction** | Upload PDF or paste text — Claude extracts skills, proficiency, projects, certifications |
| **Skill Inference** | Claude infers implied skills (e.g. Next.js → React inferred automatically) |
| **Natural Language Search** | *"Find a backend dev in Pune with Java and payments experience"* — returns ranked matches with scores |
| **HR Review Queue** | Employee-submitted profiles go to HR for approval; HR-uploaded resumes go directly to DB |
| **Role-Based Access** | Separate HR and Employee experiences |
| **Employee Self-Service** | Employees view/edit profile, add skills, update availability, track submission status |
| **Company Dashboard** | HR sees headcount, availability stats, top skills across the company |
| **Persistent Sessions** | Stay logged in across browser refreshes |

---

## 🐳 Quick Start — Docker (Recommended)

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### 1. Clone the repo
```bash
git clone https://github.com/ishwars-creator/hackathon-HR-Intelligence_Skillhub.git
cd hackathon-HR-Intelligence_Skillhub
```

### 2. Get a free OpenRouter API key
Sign up at **https://openrouter.ai/keys** — it's free, no credit card needed.

### 3. Create a `.env` file
```bash
# Create .env in the project root
echo OPENROUTER_API_KEY=sk-or-v1-your-key-here > .env
```

Or create the file manually with this content:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 4. Build and run
```bash
docker compose up --build
```

### 5. Open the app
Visit **http://localhost:8501**

> Data is stored in a Docker named volume and persists across container restarts.

---

## 🐍 Quick Start — Local Python

**Prerequisites:** Python 3.10+

### 1. Clone and install
```bash
git clone https://github.com/ishwars-creator/hackathon-HR-Intelligence_Skillhub.git
cd hackathon-HR-Intelligence_Skillhub
pip install -r requirements.txt
```

### 2. Create `.env` file
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 3. Run
```bash
streamlit run app.py
```

Open **http://localhost:8501**

---

## 🔑 Demo Credentials

| Role | Email | Password |
|---|---|---|
| **HR Admin** | hr@company.com | hr123 |
| **Employee** | rahul.sharma@company.com | emp123 |
| **Employee** | priya.menon@company.com | emp123 |
| **Employee** | sneha.patil@company.com | emp123 |

> 15 employees are pre-seeded in the database for demo purposes.

---

## 🎯 Demo Flow (for judges)

### As HR:
1. Login with `hr@company.com / hr123`
2. **Dashboard** → see company-wide stats (headcount, availability, top skills)
3. **Search Talent** → try natural language queries:
   - *"Who can lead a React project that also needs WebSocket experience?"*
   - *"Find a backend dev in Pune with Java and payment gateway experience"*
   - *"Python developer with machine learning experience, available now"*
4. See ranked results with **match scores (0–100%)** and plain-English explanations
5. **Employee Directory → Upload Resume** → upload a PDF resume → Claude extracts skills in ~20s
6. Profile is added **directly to the directory** (HR bypasses review queue)
7. **Review Queue** → approve or reject employee-submitted profiles

### As Employee:
1. Login with `rahul.sharma@company.com / emp123`
2. **My Profile** → view skills, projects, certifications
3. **Edit Profile** → update availability, add/remove skills, edit experience
4. **Upload Resume** → submit an updated resume → HR gets notified for review
5. **My Profile** → see submission status (Pending / Approved / Rejected)

---

## 📁 Project Structure

```
skillshub/
├── app.py                  # Entry point: login, session, sidebar routing
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── data/
│   ├── seed_data.py        # 15 pre-seeded employees + demo user accounts
│   └── __init__.py
├── utils/
│   ├── claude_ai.py        # AI: resume extraction + semantic search
│   └── db.py               # All database operations (JSON file store)
└── pages/
    ├── dashboard.py        # HR: company stats + recent employees
    ├── search.py           # HR: natural language talent search
    ├── directory.py        # HR: employee directory with filters
    ├── review_queue.py     # HR: approve / reject submitted profiles
    ├── upload.py           # HR + Employee: resume upload & AI extraction
    └── my_profile.py       # Employee: profile view, edit, submission status
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **UI** | Streamlit (Python) |
| **AI / LLM** | OpenRouter API → `openai/gpt-oss-120b:free` |
| **PDF Parsing** | pypdf |
| **Database** | JSON file (zero setup, Docker volume for persistence) |
| **Session** | Token-based (stored in DB + URL query param) |
| **Containerisation** | Docker + Docker Compose |

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | ✅ Yes | Free key from https://openrouter.ai/keys |

---

## 📝 Notes

- The `.env` file is **gitignored** — never committed. Each person running the app needs their own key.
- The database (`db.json`) is created automatically on first run inside the Docker volume.
- Free OpenRouter models are used — extraction takes ~15–30 seconds depending on model load.
