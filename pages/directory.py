import streamlit as st
from utils.db import get_all_employees

PROFICIENCY_ORDER = {"expert": 0, "intermediate": 1, "novice": 2}

def show_directory():
    user = st.session_state.get("user", {})
    is_hr = user.get("role") == "hr"

    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown("# 👥 Employee Directory")
    with col_btn:
        if is_hr:
            st.markdown("<div style='padding-top:14px;'>", unsafe_allow_html=True)
            if st.button("📤 Upload Resume", type="primary", use_container_width=True):
                st.session_state.page = "Upload Resume"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    employees = get_all_employees()
    
    # ── Filters ──────────────────────────────────────────────
    with st.expander("🔧 Filter & Search", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            name_filter = st.text_input("Search by name", placeholder="e.g. Rahul")
        with fc2:
            locations = ["All"] + sorted(set(e.get("location", "") for e in employees if e.get("location")))
            loc_filter = st.selectbox("Location", locations)
        with fc3:
            avail_filter = st.selectbox("Availability", ["All", "Available", "On Project"])
        with fc4:
            dept_filter_options = ["All"] + sorted(set(e.get("department", "") for e in employees if e.get("department")))
            dept_filter = st.selectbox("Department", dept_filter_options)

    # Apply filters
    filtered = employees
    if name_filter:
        filtered = [e for e in filtered if name_filter.lower() in e["name"].lower()]
    if loc_filter != "All":
        filtered = [e for e in filtered if e.get("location") == loc_filter]
    if avail_filter == "Available":
        filtered = [e for e in filtered if e.get("availability") == "available"]
    elif avail_filter == "On Project":
        filtered = [e for e in filtered if e.get("availability") == "on_project"]
    if dept_filter != "All":
        filtered = [e for e in filtered if e.get("department") == dept_filter]

    st.markdown(f"**{len(filtered)} employees** found")
    st.markdown("---")

    if not filtered:
        st.info("No employees match the current filters.")
        return

    # ── Employee Cards ────────────────────────────────────────
    for emp in filtered:
        avail_html = (
            '<span style="color:#16a34a; font-weight:600;">✅ Available</span>'
            if emp.get("availability") == "available"
            else '<span style="color:#dc2626; font-weight:600;">🔴 On Project</span>'
        )

        top_skills = sorted(emp.get("skills", []), key=lambda s: PROFICIENCY_ORDER.get(s["proficiency"], 9))[:5]
        skills_html = " ".join([
            f"<span class='badge badge-{s['proficiency']}'>{s['name']}</span>"
            for s in top_skills
        ])

        certs = emp.get("certifications", [])
        certs_text = " · ".join(["🏅 " + c for c in certs[:2]]) if certs else ""

        with st.container():
            col_info, col_stats, col_btn = st.columns([5, 2, 1])

            with col_info:
                st.markdown(f"""
                <div class='skill-card'>
                    <div style='font-size:16px; font-weight:700; color:#0f172a;'>{emp['name']}</div>
                    <div style='color:#64748b; font-size:13px; margin-top:2px;'>
                        {emp.get('title','—')} &nbsp;·&nbsp; 📍 {emp.get('location','—')} &nbsp;·&nbsp; {emp.get('department','—')}
                    </div>
                    <div style='margin:8px 0 4px;'>{skills_html}</div>
                    {f"<div style='font-size:12px; color:#64748b; margin-top:4px;'>{certs_text}</div>" if certs_text else ""}
                </div>
                """, unsafe_allow_html=True)

            with col_stats:
                st.markdown(f"<div style='padding-top:14px; text-align:right;'>{avail_html}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#94a3b8; font-size:12px; text-align:right;'>{emp.get('years_experience',0)} yrs exp</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#94a3b8; font-size:12px; text-align:right;'>{len(emp.get('projects',[]))} project(s)</div>", unsafe_allow_html=True)

            with col_btn:
                st.markdown("<div style='padding-top:14px;'>", unsafe_allow_html=True)
                if st.button("View", key=f"view_{emp['id']}"):
                    st.session_state["viewed_employee"] = emp["id"]
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Expanded profile view
        if st.session_state.get("viewed_employee") == emp["id"]:
            _show_full_profile(emp)
            if st.button("Close", key=f"close_{emp['id']}"):
                st.session_state["viewed_employee"] = None
                st.rerun()


def _show_full_profile(emp):
    with st.container():
        st.markdown(f"""
        <div style='background:#f0f9ff; border:1px solid #bae6fd; border-radius:12px; padding:20px; margin:8px 0 16px;'>
            <h3 style='margin:0 0 4px; color:#0f172a;'>{emp['name']}</h3>
            <p style='color:#0284c7; margin:0 0 12px;'>{emp.get('title','—')} · {emp.get('location','—')} · {emp.get('department','—')}</p>
            <p style='color:#334155; font-size:14px;'>{emp.get('summary','')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🛠 Skills", "📁 Projects", "🏅 Certifications"])
        
        with tab1:
            categories = {}
            for s in emp.get("skills", []):
                cat = s.get("category", "other")
                categories.setdefault(cat, []).append(s)
            
            for cat, skills in sorted(categories.items()):
                st.markdown(f"**{cat.title()}**")
                cols = st.columns(4)
                for i, s in enumerate(skills):
                    with cols[i % 4]:
                        badge_cls = f"badge-{s['proficiency']}"
                        st.markdown(f"""
                        <div style='border:1px solid #e2e8f0; border-radius:8px; padding:8px 10px; margin-bottom:6px; text-align:center;'>
                            <div style='font-weight:600; font-size:13px;'>{s['name']}</div>
                            <span class='badge {badge_cls}'>{s['proficiency']}</span>
                            <div style='font-size:11px; color:#94a3b8; margin-top:2px;'>{s['years']} yr(s)</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            if emp.get("inferred_skills"):
                st.markdown("**Inferred Skills** *(auto-detected)*")
                for inf in emp["inferred_skills"]:
                    st.markdown(f"<span class='badge' style='background:#f3e8ff;color:#7c3aed;'>{inf}</span>", unsafe_allow_html=True)
        
        with tab2:
            for p in emp.get("projects", []):
                with st.container():
                    st.markdown(f"**{p['name']}** — *{p['role']}* ({p['duration']})")
                    st.caption("Tech: " + ", ".join(p.get("tech", [])))
                    st.markdown("---")
        
        with tab3:
            certs = emp.get("certifications", [])
            if certs:
                for c in certs:
                    st.markdown(f"🏅 {c}")
            else:
                st.info("No certifications listed.")
