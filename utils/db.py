import json
import os
import copy
from data.seed_data import SEED_EMPLOYEES, USERS

# Write DB to user's home directory (~\skillshub_data\db.json)
# This avoids Windows permission issues with protected folders like C:\Users\<appname>
DB_DIR = os.path.join(os.path.expanduser("~"), "skillshub_data")
DB_PATH = os.path.join(DB_DIR, "db.json")

def _load_db():
    if not os.path.exists(DB_PATH):
        _init_db()
    with open(DB_PATH, "r") as f:
        return json.load(f)

def _save_db(db):
    os.makedirs(DB_DIR, exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def _init_db():
    db = {
        "employees": {e["id"]: e for e in SEED_EMPLOYEES},
        "pending_profiles": {},
        "users": USERS
    }
    _save_db(db)

def get_all_employees(approved_only=True):
    db = _load_db()
    emps = list(db["employees"].values())
    if approved_only:
        return [e for e in emps if e.get("approved", False)]
    return emps

def get_employee_by_id(emp_id):
    db = _load_db()
    return db["employees"].get(emp_id)

def get_employee_by_email(email):
    db = _load_db()
    for emp in db["employees"].values():
        if emp.get("email") == email:
            return emp
    return None

def save_employee(employee):
    db = _load_db()
    db["employees"][employee["id"]] = employee
    _save_db(db)

def add_employee_direct(profile):
    """HR-added employees bypass review and go straight to the DB as approved."""
    db = _load_db()
    profile["approved"] = True
    if profile.get("email"):
        db["users"][profile["email"]] = {
            "password": "emp123",
            "role": "employee",
            "name": profile["name"],
            "employee_id": profile["id"]
        }
    db["employees"][profile["id"]] = profile
    _save_db(db)

def add_pending_profile(profile):
    db = _load_db()
    db["pending_profiles"][profile["id"]] = profile
    _save_db(db)

def get_pending_profiles():
    db = _load_db()
    return [p for p in db["pending_profiles"].values() if p.get("status") != "rejected"]

def get_submission_by_email(email):
    """Return the latest submission (pending or rejected) for a given employee email."""
    db = _load_db()
    for p in db["pending_profiles"].values():
        if p.get("email") == email:
            return p
    return None

def get_pending_profile(profile_id):
    db = _load_db()
    return db["pending_profiles"].get(profile_id)

def approve_profile(profile_id):
    db = _load_db()
    profile = db["pending_profiles"].pop(profile_id, None)
    if profile:
        profile["approved"] = True
        if profile.get("email"):
            db["users"][profile["email"]] = {
                "password": "emp123",
                "role": "employee",
                "name": profile["name"],
                "employee_id": profile["id"]
            }
        db["employees"][profile["id"]] = profile
        _save_db(db)
        return profile
    return None

def reject_profile(profile_id):
    db = _load_db()
    profile = db["pending_profiles"].get(profile_id)
    if profile:
        profile["status"] = "rejected"
        db["pending_profiles"][profile_id] = profile
        _save_db(db)

def update_pending_profile(profile):
    db = _load_db()
    db["pending_profiles"][profile["id"]] = profile
    _save_db(db)

def get_user(email):
    db = _load_db()
    return db["users"].get(email)

def save_session_token(token: str, email: str):
    db = _load_db()
    db.setdefault("session_tokens", {})[token] = email
    _save_db(db)

def get_email_from_token(token: str) -> str:
    db = _load_db()
    return db.get("session_tokens", {}).get(token, "")

def delete_session_token(token: str):
    db = _load_db()
    db.get("session_tokens", {}).pop(token, None)
    _save_db(db)

def get_stats():
    db = _load_db()
    employees = list(db["employees"].values())
    pending = [p for p in db["pending_profiles"].values() if p.get("status") != "rejected"]
    all_skills = []
    for e in employees:
        all_skills.extend([s["name"] for s in e.get("skills", [])])
    return {
        "total_employees": len(employees),
        "pending_reviews": len(pending),
        "available": len([e for e in employees if e.get("availability") == "available"]),
        "total_skills": len(set(all_skills)),
        "top_skills": _top_skills(employees)
    }

def _top_skills(employees):
    from collections import Counter
    counter = Counter()
    for e in employees:
        for s in e.get("skills", []):
            counter[s["name"]] += 1
    return counter.most_common(8)
