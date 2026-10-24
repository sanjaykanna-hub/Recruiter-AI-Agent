
import streamlit as st

st.set_page_config(
    page_title="Recruiter AI Agent",
    page_icon="🤖",
    layout="wide",
)

pages = {
    "Recruitment Portal": [
        st.Page(
            "recruter.py",
            title="Recruiter Dashboard",
            icon="🧑‍💼",
            default=True,
        ),
        st.Page(
            "candidate_app.py",
            title="Candidate Portal",
            icon="👤",
        ),
    ]
}

selected_page = st.navigation(pages)
selected_page.run()
