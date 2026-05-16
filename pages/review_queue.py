import streamlit as st
from utils.db import get_pending_profiles, approve_profile, reject_profile, update_pending_profile

def show_review_queue():
    st.markdown("# 📋 Review Queue")
    st.markdown("Review and approve AI-extracted profiles before they're added to the database.")
    
    pending = get_pending_profiles()
    
    if not pending:
        st.success("🎉 All caught up! No profiles waiting for review.")
        return
    
    st.info(f"**{len(pending)} profile(s)** awaiting review")
    st.markdown("---")
    
    for profile in pending:
        with st.expander(f"👤 {profile.get('name', 'Unknown')} — {profile.get('title', '—')} · {profile.get('location', '—')}", expanded=True):
            _show_review_card(profile)


def _show_review_card(profile):
    st.markdown(f"**Email:** {profile.get('email', '—')}  |  **Experience:** {profile.get('years_experience', 0)} years  |  **Availability:** {profile.get('availability', '—')}")
    st.markdown(f"> {profile.get('summary', 'No summary available.')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🛠 Extracted Skills**")
        for s in profile.get("skills", []):
            badge_cls = f"badge-{s['proficiency']}"
            st.markdown(
                f"<span class='badge {badge_cls}'>{s['name']}</span> "
                f"<span style='font-size:12px; color:#64748b;'>{s['proficiency']} · {s['years']}yr</span>",
                unsafe_allow_html=True
            )
        
        if profile.get("inferred_skills"):
            st.markdown("**💡 Inferred Skills**")
            for inf in profile["inferred_skills"]:
                st.markdown(f"<span class='badge' style='background:#f3e8ff;color:#7c3aed;'>{inf}</span>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("**📁 Projects**")
        for p in profile.get("projects", []):
            st.markdown(f"• **{p.get('name','')}** — {p.get('role','')} ({p.get('duration','')})")
            st.caption(", ".join(p.get("tech", [])))
        
        if profile.get("certifications"):
            st.markdown("**🏅 Certifications**")
            for c in profile["certifications"]:
                st.markdown(f"🏅 {c}")
    
    st.markdown("---")
    
    # Quick edit proficiency
    st.markdown("**Quick Edit: Adjust skill proficiency if needed**")
    skills = profile.get("skills", [])
    updated_skills = []
    cols = st.columns(min(len(skills), 4)) if skills else []
    
    for i, s in enumerate(skills):
        with cols[i % 4] if cols else st.container():
            new_prof = st.selectbox(
                s["name"],
                ["novice", "intermediate", "expert"],
                index=["novice", "intermediate", "expert"].index(s.get("proficiency", "intermediate")),
                key=f"rq_skill_{profile['id']}_{i}"
            )
            updated_skills.append({**s, "proficiency": new_prof})
    
    # Action buttons
    action_col1, action_col2, action_col3 = st.columns([1, 1, 3])
    
    with action_col1:
        if st.button("✅ Approve", key=f"approve_{profile['id']}", type="primary", use_container_width=True):
            # Save any edits first
            updated = {**profile, "skills": updated_skills}
            update_pending_profile(updated)
            approve_profile(profile["id"])
            st.success(f"✅ **{profile['name']}** has been approved and added to the database!")
            st.rerun()
    
    with action_col2:
        if st.button("❌ Reject", key=f"reject_{profile['id']}", use_container_width=True):
            reject_profile(profile["id"])
            st.warning(f"Profile for **{profile['name']}** has been rejected.")
            st.rerun()
