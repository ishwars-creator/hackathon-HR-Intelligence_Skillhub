import streamlit as st
from utils.db import get_stats, get_all_employees, get_pending_profiles

def show_dashboard():
    st.markdown("# 📊 Dashboard")
    st.markdown("Welcome back! Here's your skills intelligence overview.")
    
    stats = get_stats()
    
    # ── Top Metrics ──────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Employees", stats["total_employees"])
    with c2:
        st.metric("Available Now", stats["available"], help="Not currently on a project")
    with c3:
        st.metric("Pending Reviews", stats["pending_reviews"], 
                  delta="Action needed" if stats["pending_reviews"] > 0 else None,
                  delta_color="inverse")
    with c4:
        st.metric("Unique Skills", stats["total_skills"])

    st.markdown("---")

    col1, col2 = st.columns([1.4, 1])
    
    with col1:
        st.markdown("### 👥 Recent Employees")
        employees = get_all_employees()[:6]
        for e in employees:
            avail_html = (
                '<span class="avail-yes">● Available</span>' 
                if e.get("availability") == "available" 
                else '<span class="avail-no">● On Project</span>'
            )
            top_skills = ", ".join([s["name"] for s in e.get("skills", [])[:4]])
            st.markdown(f"""
            <div class='skill-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <div style='font-weight:600; font-size:15px; color:#0f172a;'>{e['name']}</div>
                        <div style='color:#64748b; font-size:13px;'>{e.get('title','—')} · {e.get('location','—')}</div>
                        <div style='color:#94a3b8; font-size:12px; margin-top:4px;'>{top_skills}</div>
                    </div>
                    <div style='text-align:right;'>
                        {avail_html}
                        <div style='color:#94a3b8; font-size:12px; margin-top:4px;'>{e.get('years_experience',0)} yrs exp</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🏆 Top Skills in Company")
        for skill, count in stats["top_skills"]:
            pct = int((count / stats["total_employees"]) * 100)
            st.markdown(f"""
            <div style='margin-bottom:10px;'>
                <div style='display:flex; justify-content:space-between; font-size:13px;'>
                    <span style='font-weight:500; color:#1e293b;'>{skill}</span>
                    <span style='color:#64748b;'>{count} people</span>
                </div>
                <div class='score-bar-container'>
                    <div class='score-bar' style='width:{min(pct*2, 100)}%;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Pending review alert
        pending = get_pending_profiles()
        if pending:
            st.markdown("### 🔔 Needs Attention")
            st.warning(f"**{len(pending)} profile(s)** awaiting your review in the Review Queue.")
            if st.button("Go to Review Queue →"):
                st.session_state.page = "Review Queue"
                st.rerun()
