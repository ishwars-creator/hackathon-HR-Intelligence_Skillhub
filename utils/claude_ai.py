import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from json_repair import repair_json

load_dotenv()

# Models for structured extraction — accuracy over speed, no tiny models
MODELS_FAST = [
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "deepseek/deepseek-v4-flash:free",
]

# Models for semantic reasoning tasks
MODELS_QUALITY = [
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "deepseek/deepseek-v4-flash:free",
]

def _get_client():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not set.\n\n"
            "Get a free key at https://openrouter.ai/keys\n"
            "Then run:  set OPENROUTER_API_KEY=sk-or-your-key-here\n"
            "And restart the app."
        )
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=40.0,
    )

def _call_ai(prompt: str, models: list = None, max_tokens: int = 2000) -> str:
    client = _get_client()
    last_error = None
    for model in (models or MODELS_QUALITY):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError(f"Empty response from {model}")
            return content.strip()
        except Exception as e:
            last_error = e
    raise last_error or RuntimeError("All models failed")

def _clean_json(raw: str) -> str:
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw)
    raw = raw.strip()
    start = next((i for i, c in enumerate(raw) if c in ('{', '[')), 0)
    return repair_json(raw[start:])


def extract_skills_from_resume(resume_text: str) -> dict:
    prompt = f"""You are a skills extraction expert. Analyze the following resume and extract structured information.

RESUME TEXT:
{resume_text}

Return ONLY a valid JSON object with this exact structure (no markdown, no explanation, no code fences):
{{
  "name": "Full name",
  "email": "email if found, else empty string",
  "title": "job title / current role",
  "location": "city if mentioned",
  "years_experience": <number, estimate total years>,
  "summary": "2-3 sentence professional summary",
  "skills": [
    {{
      "name": "skill name",
      "category": "one of: language/framework/platform/tool/database/domain/practice/library/technology",
      "proficiency": "one of: novice/intermediate/expert",
      "years": <number>
    }}
  ],
  "projects": [
    {{
      "name": "project name",
      "duration": "e.g. 6 months",
      "role": "their role",
      "tech": ["tech1", "tech2"]
    }}
  ],
  "certifications": ["cert1", "cert2"],
  "inferred_skills": ["skill1", "skill2"]
}}

Rules:
- proficiency: novice = less than 1yr, intermediate = 1-3yr, expert = 3+yr
- inferred_skills: skills strongly implied but not stated (e.g. Next.js implies React)
- Return ONLY the JSON, nothing else"""

    raw = _call_ai(prompt, models=MODELS_FAST)
    return json.loads(_clean_json(raw))


def semantic_search(query: str, employees: list) -> list:
    emp_summaries = []
    for e in employees:
        skills_str = ", ".join([
            f"{s['name']} ({s['proficiency']}, {s['years']}yr)"
            for s in e.get("skills", [])
        ])
        projects_str = "; ".join([
            f"{p['name']} as {p['role']}"
            for p in e.get("projects", [])
        ])
        availability = "Available" if e.get("availability") == "available" else "On project"
        inferred = ", ".join(e.get("inferred_skills", []))
        last_end = e.get("last_project_end", "")
        emp_summaries.append(
            f"ID:{e['id']} | {e['name']} | {e['title']} | {e.get('location','?')} | "
            f"{e.get('years_experience',0)}yrs exp | {availability}\n"
            f"  Skills: {skills_str}\n"
            f"  Inferred skills: {inferred}\n"
            f"  Projects: {projects_str}\n"
            f"  Last project end: {last_end or '—'}\n"
            f"  Certs: {', '.join(e.get('certifications', []))}"
        )

    employees_text = "\n\n".join(emp_summaries)

    prompt = f"""You are a talent intelligence system. A recruiter has asked:

QUERY: "{query}"

EMPLOYEE DATABASE:
{employees_text}

Analyze each employee against the query and return ONLY a valid JSON array (no markdown, no code fences).
Only include employees who are relevant (score 40+). Sort by score descending.

Return exactly this format:
[
  {{
    "id": "emp_xxx",
    "score": <0-100 integer>,
    "reason": "1-2 sentence plain-English explanation mentioning specific skills/experience",
    "highlights": ["key strength 1", "key strength 2", "key strength 3"]
  }}
]

Scoring: 90+ = near-perfect, 70-89 = strong, 50-69 = partial, below 40 = omit.
Use semantic understanding, not just keywords.
Return ONLY the JSON array."""

    raw = _call_ai(prompt, models=MODELS_QUALITY, max_tokens=4000)
    results = json.loads(_clean_json(raw))

    emp_map = {e["id"]: e for e in employees}
    enriched = []
    for r in results:
        emp = emp_map.get(r["id"])
        if emp:
            enriched.append({
                **emp,
                "match_score": int(r["score"]),
                "match_reason": r["reason"],
                "highlights": r.get("highlights", [])
            })
    return enriched
