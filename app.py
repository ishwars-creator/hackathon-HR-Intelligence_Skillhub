import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import secrets
from utils.db import get_user, get_stats, get_pending_profiles, save_session_token, get_email_from_token, delete_session_token
import extra_streamlit_components as stx

st.set_page_config(
    page_title="SkillsHub",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3, .stMetric label {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Hide only the branding parts inside the header, not the whole header */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background: transparent !important; border: none !important;}
header [data-testid="stToolbar"] {visibility: hidden;}

/* Remove top dead space */
.main .block-container {
    padding-top: 0.5rem !important;
    margin-top: -3rem !important;
}

/* Sidebar always visible — force open, hide all toggle buttons */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    transform: none !important;
    margin-left: 0 !important;
    min-width: 244px !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    display: block !important;
    transform: none !important;
    margin-left: 0 !important;
}
[data-testid="stSidebar"] button[kind="header"],
[data-testid="stSidebar"] button[data-testid="baseButton-header"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Hide auto-generated pages/ navigation */
[data-testid="stSidebarNav"] {display: none;}
[data-testid="stSidebarNavItems"] {display: none;}
[data-testid="stSidebarNavSeparator"] {display: none;}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}
[data-testid="stSidebar"] * {color: #e2e8f0 !important;}
[data-testid="stSidebar"] .stRadio label {
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(99,102,241,0.2);
}

/* Active nav button (primary type in sidebar) */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
/* Inactive nav buttons */
[data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
    background: rgba(99,102,241,0.2) !important;
    border-color: rgba(99,102,241,0.4) !important;
}

/* Cards */
.skill-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    transition: box-shadow 0.2s;
}
.skill-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

/* Metric override */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Skill badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    margin: 2px;
}
.badge-expert { background: #dcfce7; color: #166534; }
.badge-intermediate { background: #dbeafe; color: #1e40af; }
.badge-novice { background: #fef9c3; color: #854d0e; }

/* Score bar */
.score-bar-container {
    background: #f1f5f9;
    border-radius: 8px;
    height: 8px;
    width: 100%;
    margin: 6px 0;
}
.score-bar {
    height: 8px;
    border-radius: 8px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
}

/* Availability badges */
.avail-yes { color: #16a34a; font-weight: 600; }
.avail-no  { color: #dc2626; font-weight: 600; }

/* Search result card */
.result-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #6366f1;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.result-card:hover { box-shadow: 0 4px 16px rgba(99,102,241,0.1); }
</style>
""", unsafe_allow_html=True)

# ── Cookie Manager ───────────────────────────────────────────
cookie_manager = stx.CookieManager(key="skillshub_cookies")

# ── Session State ────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ── Restore session from URL token (survives browser refresh) ─
if not st.session_state.logged_in:
    token = st.query_params.get("token", "")
    if token:
        email = get_email_from_token(token)
        if email:
            user = get_user(email)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = {**user, "email": email}
                st.session_state["_session_token"] = token


# ── Login Screen ─────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom: 32px;'>
            <div style='font-size: 48px;'>🧠</div>
            <h1 style='font-family: Space Grotesk; font-size: 36px; font-weight: 700; color: #0f172a; margin: 8px 0 4px;'>SkillsHub</h1>
            <p style='color: #64748b; font-size: 16px; margin: 0;'>AI-Powered Skills Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("#### Sign In")
            email = st.text_input("Email", placeholder="hr@company.com or rahul.sharma@company.com")
            password = st.text_input("Password", type="password", placeholder="hr123 or emp123")
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

            if submitted:
                email_clean    = email.strip().lower()
                password_clean = password.strip()
                user = get_user(email_clean)
                if user and user["password"] == password_clean:
                    token = secrets.token_hex(16)
                    save_session_token(token, email_clean)
                    st.session_state.logged_in = True
                    st.session_state.user = {**user, "email": email_clean}
                    st.session_state["_session_token"] = token
                    st.query_params["token"] = token
                    st.rerun()
                else:
                    st.error("Invalid credentials. Try hr@company.com / hr123")
            
            st.markdown("""
            <div style='margin-top: 20px; padding: 14px; background: #f8fafc; border-radius: 10px; font-size: 13px; color: #475569;'>
            <b>Demo credentials:</b><br>
            🏢 <b>HR:</b> hr@company.com / hr123<br>
            👤 <b>Employee:</b> rahul.sharma@company.com / emp123
            </div>
            """, unsafe_allow_html=True)


# ── Sidebar Navigation ────────────────────────────────────────
def show_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style='padding: 16px 0 24px;'>
            <div style='font-size: 24px; font-weight: 700; font-family: Space Grotesk; color: white;'>🧠 SkillsHub</div>
            <div style='margin-top: 12px; padding: 10px 12px; background: rgba(255,255,255,0.08); border-radius: 8px;'>
                <div style='font-size: 13px; opacity: 0.6;'>Signed in as</div>
                <div style='font-weight: 600; font-size: 14px;'>{user['name']}</div>
                <div style='font-size: 11px; opacity: 0.5; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px;'>
                    {'HR Team' if user['role'] == 'hr' else 'Employee'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if user["role"] == "hr":
            pending_count = len(get_pending_profiles())
            pages = ["Dashboard", "Search Talent", "Employee Directory", "Review Queue"]
            labels = [
                "📊  Dashboard",
                "🔍  Search Talent",
                "👥  Employee Directory",
                f"📋  Review Queue {'🔴' if pending_count > 0 else ''}",
            ]
        else:
            pages = ["My Profile", "Upload Resume"]
            labels = ["👤  My Profile", "📤  Upload Resume"]
        
        st.markdown("**Navigation**")
        active_page = st.session_state.page
        # HR upload is accessed from directory — keep Directory highlighted
        if user["role"] == "hr" and active_page == "Upload Resume":
            active_page = "Employee Directory"
        for page, label in zip(pages, labels):
            is_active = active_page == page
            if st.button(label, key=f"nav_{page}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪  Sign Out", use_container_width=True):
            try:
                cookie_manager.delete("skillshub_user")
            except Exception:
                pass
            token = st.session_state.get("_session_token", "")
            if token:
                delete_session_token(token)
            st.query_params.clear()
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "Dashboard"
            st.rerun()


# ── Main App Router ───────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        show_login()
        return
    
    show_sidebar()
    
    user = st.session_state.user
    page = st.session_state.page
    
    if user["role"] == "hr":
        if page == "Dashboard":
            from pages.dashboard import show_dashboard
            show_dashboard()
        elif page == "Search Talent":
            from pages.search import show_search
            show_search()
        elif page == "Employee Directory":
            from pages.directory import show_directory
            show_directory()
        elif page == "Review Queue":
            from pages.review_queue import show_review_queue
            show_review_queue()
        elif page == "Upload Resume":
            from pages.upload import show_upload
            show_upload()
    else:
        if page == "My Profile":
            from pages.my_profile import show_my_profile
            show_my_profile()
        elif page == "Upload Resume":
            from pages.upload import show_upload
            show_upload()
        elif page == "Employee Directory":
            from pages.directory import show_directory
            show_directory()
        else:
            from pages.my_profile import show_my_profile
            show_my_profile()


if __name__ == "__main__":
    main()
