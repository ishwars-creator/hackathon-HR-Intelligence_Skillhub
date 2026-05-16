import streamlit as st
from utils.db import get_employee_by_email, save_employee, get_submission_by_email

def show_my_profile():
    user = st.session_state.user

    if st.session_state.pop("profile_saved", False):
        st.toast("✅ Profile saved successfully!", icon="✅")

    emp = get_employee_by_email(user["email"])

    # ── Submission status banner ──────────────────────────────
    submission = get_submission_by_email(user["email"])
    if submission:
        status = submission.get("status", "pending")
        if status == "rejected":
            st.markdown("""
<div style='background:#fef2f2; border:1px solid #fca5a5; border-left:4px solid #dc2626;
     border-radius:10px; padding:14px 18px; margin-bottom:16px;'>
    <div style='font-weight:700; color:#dc2626; font-size:15px;'>❌ Resume Submission Rejected</div>
    <div style='color:#7f1d1d; font-size:13px; margin-top:4px;'>
        Your submitted resume was reviewed and not approved. Please upload an updated resume for re-review.
    </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div style='background:#fffbeb; border:1px solid #fcd34d; border-left:4px solid #f59e0b;
     border-radius:10px; padding:14px 18px; margin-bottom:16px;'>
    <div style='font-weight:700; color:#92400e; font-size:15px;'>⏳ Resume Under Review</div>
    <div style='color:#78350f; font-size:13px; margin-top:4px;'>
        Your resume has been submitted and is awaiting HR approval. You'll see your full profile once approved.
    </div>
</div>""", unsafe_allow_html=True)

    if not emp:
        st.info("Your profile hasn't been set up yet. Use the **Upload Resume** tab to create it.")
        return
    
    st.markdown(f"# 👤 My Profile")
    
    avail_color = "#16a34a" if emp.get("availability") == "available" else "#dc2626"
    avail_text = "✅ Available" if emp.get("availability") == "available" else "🔴 On Project"
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; border-radius: 16px; padding: 28px; margin-bottom: 24px;'>
        <div style='font-size: 28px; font-weight: 700; font-family: Space Grotesk;'>{emp['name']}</div>
        <div style='font-size: 16px; opacity: 0.7; margin-top: 4px;'>{emp.get('title','—')} · {emp.get('location','—')} · {emp.get('department','—')}</div>
        <div style='margin-top: 12px; font-size: 14px; opacity: 0.6;'>{emp.get('summary','')}</div>
        <div style='margin-top: 16px;'>
            <span style='color: {avail_color}; font-weight: 600;'>{avail_text}</span>
            <span style='opacity: 0.5; margin: 0 12px;'>|</span>
            <span style='opacity: 0.6;'>{emp.get('years_experience', 0)} years experience</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🛠 Skills", "📁 Projects", "🏅 Certifications", "✏️ Edit Profile"])
    
    with tab1:
        st.markdown("### My Skills")
        
        # Group by category
        categories = {}
        for s in emp.get("skills", []):
            cat = s.get("category", "other")
            categories.setdefault(cat, []).append(s)
        
        for cat, skills in sorted(categories.items()):
            st.markdown(f"**{cat.title()}**")
            skill_cols = st.columns(4)
            for i, s in enumerate(skills):
                with skill_cols[i % 4]:
                    badge_cls = f"badge-{s['proficiency']}"
                    st.markdown(f"""
                    <div style='border:1px solid #e2e8f0; border-radius:10px; padding:10px; text-align:center; margin-bottom:8px;'>
                        <div style='font-weight:600;'>{s['name']}</div>
                        <span class='badge {badge_cls}'>{s['proficiency']}</span>
                        <div style='font-size:11px; color:#94a3b8; margin-top:4px;'>{s['years']} yr(s)</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("")
        
        if emp.get("inferred_skills"):
            st.markdown("**💡 AI-Inferred Skills**")
            st.caption("Skills Claude inferred you likely have based on your stated skills.")
            for inf in emp["inferred_skills"]:
                st.markdown(f"<span class='badge' style='background:#f3e8ff;color:#7c3aed;'>{inf}</span>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Project History")
        for p in emp.get("projects", []):
            with st.container():
                st.markdown(f"#### {p['name']}")
                st.markdown(f"**Role:** {p['role']}  |  **Duration:** {p['duration']}")
                if p.get("tech"):
                    st.markdown("**Technologies:** " + ", ".join(p["tech"]))
                st.markdown("---")
    
    with tab3:
        st.markdown("### Certifications")
        certs = emp.get("certifications", [])
        if certs:
            for c in certs:
                st.markdown(f"🏅 **{c}**")
        else:
            st.info("No certifications added yet.")
    
    with tab4:
        st.markdown("### ✏️ Edit Your Profile")

        # ── Basic Info ────────────────────────────────────────
        st.markdown("#### Basic Information")
        bi1, bi2, bi3 = st.columns(3)
        with bi1:
            new_name  = st.text_input("Full Name",   value=emp.get("name", ""))
            new_title = st.text_input("Job Title",   value=emp.get("title", ""))
        with bi2:
            new_dept     = st.text_input("Department", value=emp.get("department", "Engineering"))
            new_location = st.text_input("Location",   value=emp.get("location", ""))
        with bi3:
            new_years_exp = st.number_input("Years of Experience", min_value=0.0, max_value=40.0,
                                             value=float(emp.get("years_experience", 0)), step=0.5)
            new_avail = st.selectbox("Availability",
                ["available", "on_project"],
                index=0 if emp.get("availability") == "available" else 1)

        new_summary = st.text_area("Summary", value=emp.get("summary", ""), height=90)

        st.markdown("---")

        # ── Edit / Remove Existing Skills ─────────────────────
        st.markdown("#### 🛠 Edit Existing Skills")
        existing_skills = emp.get("skills", [])
        kept_skills = []

        if existing_skills:
            hc = st.columns([3, 2, 2, 1])
            hc[0].markdown("**Skill**"); hc[1].markdown("**Proficiency**")
            hc[2].markdown("**Years**");  hc[3].markdown("**Remove**")

            for i, s in enumerate(existing_skills):
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                with c1:
                    st.markdown(f"<div style='padding:7px 0;font-weight:500'>{s['name']}</div>",
                                unsafe_allow_html=True)
                with c2:
                    prof = st.selectbox("", ["novice", "intermediate", "expert"],
                        index=["novice","intermediate","expert"].index(s.get("proficiency","intermediate")),
                        key=f"ep_{i}", label_visibility="collapsed")
                with c3:
                    yrs = st.number_input("", min_value=0.0, max_value=20.0,
                        value=float(s.get("years", 1)), step=0.5,
                        key=f"ey_{i}", label_visibility="collapsed")
                with c4:
                    remove = st.checkbox("", key=f"er_{i}", label_visibility="collapsed")

                if not remove:
                    kept_skills.append({**s, "proficiency": prof, "years": yrs})
        else:
            st.caption("No skills yet — add one below.")

        st.markdown("---")

        # ── Add New Skill ─────────────────────────────────────
        st.markdown("#### ➕ Add New Skill")
        nc1, nc2, nc3, nc4 = st.columns(4)
        with nc1:
            new_skill_name = st.text_input("Skill name", placeholder="e.g. GraphQL")
        with nc2:
            new_skill_cat  = st.selectbox("Category",
                ["language","framework","platform","tool","database","domain","practice","library","technology"])
        with nc3:
            new_skill_prof = st.selectbox("Proficiency", ["novice","intermediate","expert"])
        with nc4:
            new_skill_yrs  = st.number_input("Years", min_value=0.0, max_value=20.0, value=1.0, step=0.5)

        st.markdown("---")

        # ── Certifications ────────────────────────────────────
        st.markdown("#### 🏅 Certifications")
        st.caption("One certification per line — edit or delete directly.")
        certs_text = st.text_area("Certifications", label_visibility="collapsed",
            value="\n".join(emp.get("certifications", [])), height=100,
            placeholder="e.g. AWS Certified Developer\nCKA")

        # ── Save ──────────────────────────────────────────────
        if st.button("💾 Save Changes", type="primary"):
            final_skills = kept_skills[:]
            if new_skill_name.strip():
                final_skills.append({
                    "name": new_skill_name.strip(),
                    "category": new_skill_cat,
                    "proficiency": new_skill_prof,
                    "years": new_skill_yrs,
                })
            new_certs = [c.strip() for c in certs_text.splitlines() if c.strip()]

            updated_emp = {
                **emp,
                "name":             new_name,
                "title":            new_title,
                "department":       new_dept,
                "location":         new_location,
                "years_experience": new_years_exp,
                "availability":     new_avail,
                "summary":          new_summary,
                "skills":           final_skills,
                "certifications":   new_certs,
            }
            save_employee(updated_emp)
            st.session_state.user = {**st.session_state.user, "name": new_name}
            st.session_state["profile_saved"] = True
            st.rerun()
