import streamlit as st
from utils.db import get_all_employees
from utils.claude_ai import semantic_search

EXAMPLE_QUERIES = [
    "Who can lead a React project that also needs WebSocket experience?",
    "Find me a backend dev in Pune with at least 3 years of Java and any payment gateway integration",
    "Senior frontend folks who are currently available",
    "Who knows Kubernetes and has cloud migration experience?",
    "Find someone with mobile development skills for a healthcare app",
    "Python developer with machine learning experience, available now",
]

def show_search():
    st.markdown("# 🔍 Search Talent")
    st.markdown("Ask in plain English — no keywords needed. Claude understands your intent.")

    # ── Example queries ──────────────────────────────────────
    st.markdown("**💡 Try an example:**")
    cols = st.columns(3)
    for i, q in enumerate(EXAMPLE_QUERIES):
        with cols[i % 3]:
            if st.button(q[:55] + "…" if len(q) > 55 else q, key=f"ex_{i}", use_container_width=True):
                st.session_state["search_query"] = q
                st.session_state["search_input"] = q   # sync the text area
                st.session_state["run_search"] = True   # auto-trigger search

    st.markdown("---")

    # ── Search box ───────────────────────────────────────────
    query = st.text_area(
        "Your search query",
        placeholder="e.g. Who can lead a React project that also needs WebSocket experience?",
        height=80,
        key="search_input"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
    with col2:
        show_available_only = st.checkbox("Show available only", value=False)

    auto_search = st.session_state.pop("run_search", False)

    if (search_clicked or auto_search) and query.strip():
        st.session_state["search_query"] = query
        with st.spinner("🧠 Claude is analyzing your query and ranking candidates..."):
            employees = get_all_employees(approved_only=True)
            if show_available_only:
                employees = [e for e in employees if e.get("availability") == "available"]
            
            try:
                results = semantic_search(query, employees)
                st.session_state["search_results"] = results
                st.session_state["search_query_used"] = query
            except Exception as ex:
                st.error(f"Search failed: {ex}")
                return

    # ── Results ──────────────────────────────────────────────
    if "search_results" in st.session_state and st.session_state["search_results"]:
        results = st.session_state["search_results"]
        q_used = st.session_state.get("search_query_used", "")
        
        st.markdown(f"Found **{len(results)} matches** · sorted by relevance")
        st.markdown("---")
        
        for i, emp in enumerate(results):
            score = int(emp.get("match_score", 0))
            reason = emp.get("match_reason", "")
            highlights = emp.get("highlights", [])
            
            # Score color
            if score >= 85:
                score_color = "#16a34a"
                score_label = "Excellent Match"
            elif score >= 70:
                score_color = "#2563eb"
                score_label = "Strong Match"
            elif score >= 50:
                score_color = "#d97706"
                score_label = "Partial Match"
            else:
                score_color = "#dc2626"
                score_label = "Weak Match"
            
            avail_text = "✅ Available" if emp.get("availability") == "available" else "🔴 On Project"
            highlights_html = " ".join([f"<span class='badge badge-expert'>{h}</span>" for h in highlights[:5]])
            
            st.markdown(f"""
            <div class='result-card'>
                <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                    <div style='flex:1;'>
                        <div style='font-size:18px; font-weight:700; color:#0f172a;'>#{i+1} {emp['name']}</div>
                        <div style='color:#64748b; font-size:14px; margin-top:2px;'>
                            {emp.get('title','—')} · {emp.get('location','—')} · {emp.get('years_experience',0)} yrs exp · {avail_text}
                        </div>
                    </div>
                    <div style='text-align:right; min-width: 120px;'>
                        <div style='font-size:28px; font-weight:700; color:{score_color};'>{score}%</div>
                        <div style='font-size:11px; color:{score_color}; font-weight:600;'>{score_label}</div>
                    </div>
                </div>
                <div class='score-bar-container' style='margin: 8px 0;'>
                    <div class='score-bar' style='width:{score}%; background: linear-gradient(90deg, {score_color}88, {score_color});'></div>
                </div>
                <div style='background:#f8fafc; border-radius:8px; padding:10px 14px; margin: 10px 0; border-left:3px solid {score_color};'>
                    <div style='font-size:13px; color:#334155;'>💬 <b>Why this match:</b> {reason}</div>
                </div>
                <div style='margin-top:8px;'><b style='font-size:12px; color:#64748b;'>KEY STRENGTHS:</b> {highlights_html}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"View full profile — {emp['name']}"):
                _show_mini_profile(emp)
        
    elif "search_results" in st.session_state and not st.session_state["search_results"]:
        st.info("No matches found. Try broadening your query.")


def _show_mini_profile(emp):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Skills**")
        for s in emp.get("skills", []):
            badge_class = f"badge-{s['proficiency']}"
            st.markdown(f"<span class='badge {badge_class}'>{s['name']}</span> {s['proficiency']} · {s['years']}yr", unsafe_allow_html=True)
    with col2:
        st.markdown("**Projects**")
        for p in emp.get("projects", []):
            st.markdown(f"**{p['name']}** — {p['role']} ({p['duration']})")
            st.caption(", ".join(p.get("tech", [])))
        if emp.get("certifications"):
            st.markdown("**Certifications**")
            for c in emp["certifications"]:
                st.markdown(f"🏅 {c}")
