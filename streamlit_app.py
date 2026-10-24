
import streamlit as st

st.set_page_config(
    page_title="Recruiter AI Agent",
    page_icon="🤖",
    layout="wide",
)

recruiter_page = st.Page(
    "recruiter_app.py",
    title="Recruiter Dashboard",
    icon="🧑‍💼",
    default=True,
)

candidate_page = st.Page(
    "candidate_app.py",
    title="Candidate Portal",
    icon="👤",
)

page = st.navigation([recruiter_page, candidate_page])
page.run()
