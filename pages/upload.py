import streamlit as st
import uuid
import io
from utils.claude_ai import extract_skills_from_resume
from utils.db import add_pending_profile, add_employee_direct, get_employee_by_email


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception:
        return ""


def show_upload():
    user = st.session_state.user
    is_hr = user["role"] == "hr"

    st.markdown("# 📤 Upload Resume")
    st.markdown("Upload a PDF resume and Claude will automatically extract skills, experience, and projects.")

    tab1, tab2 = st.tabs(["📄 Upload PDF", "📝 Paste Text"])

    with tab1:
        uploaded_file = st.file_uploader("Choose a PDF resume", type=["pdf"])
        if uploaded_file:
            with st.spinner("Reading PDF..."):
                pdf_bytes = uploaded_file.read()
                resume_text = _extract_text_from_pdf(pdf_bytes)

            if resume_text:
                st.success(f"✅ PDF read successfully ({len(resume_text)} characters)")
                with st.expander("Preview extracted text"):
                    st.text(resume_text[:1500] + ("..." if len(resume_text) > 1500 else ""))
                if st.button("🧠 Extract Skills with Claude", type="primary"):
                    _run_extraction(resume_text, is_hr)
            else:
                st.error("Could not extract text from this PDF. Try the 'Paste Text' tab instead.")

    with tab2:
        st.markdown("Paste the resume content (from PDF, LinkedIn, or plain text):")
        resume_text_input = st.text_area("Resume text", height=300,
            placeholder="Paste resume content here — work experience, skills, education, projects...")
        if st.button("🧠 Extract Skills with Claude", type="primary", key="extract_text"):
            if resume_text_input.strip():
                _run_extraction(resume_text_input, is_hr)
            else:
                st.warning("Please paste some resume content first.")

    if st.session_state.get("extraction_done") and "extracted_profile" in st.session_state:
        _show_extracted_profile(st.session_state["extracted_profile"], is_hr)


def _run_extraction(resume_text: str, is_hr: bool):
    error = None
    profile = None
    with st.spinner("🧠 Claude is analyzing the resume... This takes about 30 seconds."):
        try:
            profile = extract_skills_from_resume(resume_text)
        except Exception as e:
            error = str(e)

    if error:
        st.error(f"Extraction failed: {error}")
        return

    st.success("✅ Skills extracted! Review the profile below.")
    st.session_state["extracted_profile"] = profile
    st.session_state["extraction_done"] = True
    st.rerun()


def _show_extracted_profile(profile: dict, is_hr: bool):
    st.markdown("---")
    st.markdown("## 🔍 Extracted Profile (Review & Edit)")
    
    # Editable basic info
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=profile.get("name", ""))
        title = st.text_input("Job Title", value=profile.get("title", ""))
        email = st.text_input("Email", value=profile.get("email", ""))
    with col2:
        location = st.text_input("Location", value=profile.get("location", ""))
        years_exp = st.number_input("Years of Experience", min_value=0.0, max_value=40.0,
                                     value=float(profile.get("years_experience", 0)), step=0.5)
        availability = st.selectbox("Availability", ["available", "on_project"])
    
    summary = st.text_area("Summary", value=profile.get("summary", ""), height=80)
    
    # Skills table
    st.markdown("### 🛠 Extracted Skills")
    st.info("Review the skills below. You can adjust proficiency levels before submitting.")
    
    skills = profile.get("skills", [])
    edited_skills = []
    
    for i, skill in enumerate(skills):
        cols = st.columns([3, 2, 2, 1])
        with cols[0]:
            sname = st.text_input("Skill", value=skill["name"], key=f"sname_{i}", label_visibility="collapsed")
        with cols[1]:
            _cats = ["language", "framework", "platform", "tool", "database", "domain", "practice", "library", "technology"]
            _cat_val = skill.get("category", "tool")
            _cat_idx = _cats.index(_cat_val) if _cat_val in _cats else _cats.index("tool")
            scat = st.selectbox("Category", _cats, index=_cat_idx,
                key=f"scat_{i}", label_visibility="collapsed")
        with cols[2]:
            sprof = st.selectbox("Proficiency", ["novice", "intermediate", "expert"],
                index=["novice", "intermediate", "expert"].index(skill.get("proficiency", "intermediate")),
                key=f"sprof_{i}", label_visibility="collapsed")
        with cols[3]:
            syrs = st.number_input("Yrs", min_value=0.0, max_value=20.0, value=float(skill.get("years", 1)),
                                    key=f"syrs_{i}", label_visibility="collapsed")
        edited_skills.append({"name": sname, "category": scat, "proficiency": sprof, "years": syrs})
    
    # Inferred skills
    if profile.get("inferred_skills"):
        st.markdown("### 💡 Inferred Skills")
        st.caption("These skills were inferred by Claude based on the resume — not explicitly stated.")
        for inf in profile["inferred_skills"]:
            st.markdown(f"<span class='badge' style='background:#f3e8ff;color:#7c3aed;'>{inf}</span>", unsafe_allow_html=True)
    
    # Projects
    st.markdown("### 📁 Projects")
    for p in profile.get("projects", []):
        st.markdown(f"**{p.get('name', '')}** — {p.get('role', '')} ({p.get('duration', '')})")
    
    # Submit
    st.markdown("---")
    btn_label = "✅ Add to Directory" if is_hr else "✅ Submit for Review"
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(btn_label, type="primary", use_container_width=True):
            if not name or not email:
                st.error("Name and email are required.")
                return

            final = {
                "id": f"emp_{str(uuid.uuid4())[:8]}",
                "name": name,
                "email": email,
                "title": title,
                "location": location,
                "years_experience": years_exp,
                "availability": availability,
                "department": "Engineering",
                "summary": summary,
                "skills": edited_skills,
                "projects": profile.get("projects", []),
                "certifications": profile.get("certifications", []),
                "inferred_skills": profile.get("inferred_skills", []),
                "approved": is_hr,
                "role": "employee",
                "last_project_end": None
            }

            if is_hr:
                add_employee_direct(final)
                st.success(f"✅ **{name}** added directly to the employee directory!")
            else:
                final["status"] = "pending"
                add_pending_profile(final)
                st.success(f"✅ Profile for **{name}** submitted to the review queue! HR will approve it shortly.")

            st.session_state.pop("extracted_profile", None)
            st.session_state.pop("extraction_done", None)
            st.balloons()
    with col2:
        if is_hr:
            st.info("As HR, this profile will be added directly to the employee directory — no review needed.")
        else:
            st.info("Profile goes into a review queue. HR will approve before it's added to the main database.")
