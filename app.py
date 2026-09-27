import os
import sys
import tempfile

import streamlit as st


# ============================================================
# BACKEND PATH
# ============================A================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.join(
    BASE_DIR,
    "backend"
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ============================================================
# BACKEND IMPORT
# ============================================================

from candidate_evaluator import evaluate_candidate


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Recruiter AI Agent",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 30px;
    }

    .candidate-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }

    .score {
        font-size: 30px;
        font-weight: 700;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 Recruiter AI Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered resume screening and candidate matching'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

st.markdown(
    "## 📋 Job Description"
)

job_description = st.text_area(
    "Enter the job description",
    height=220,
    placeholder=(
        "Example:\n\n"
        "Python Developer with experience in JavaScript, "
        "React, MongoDB, Git and Data Analysis. "
        "Knowledge of HTML, CSS and SQL is preferred."
    )
)


# ============================================================
# RESUME UPLOAD
# ============================================================

st.markdown(
    "## 📄 Upload Resumes"
)

uploaded_files = st.file_uploader(
    "Upload candidate resumes in PDF format",
    type=["pdf"],
    accept_multiple_files=True
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button(
    "🔍 Analyze Candidates",
    type="primary",
    use_container_width=True
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    # --------------------------------
    # Validation
    # --------------------------------

    if not job_description.strip():

        st.warning(
            "Please enter a job description."
        )

        st.stop()

    if not uploaded_files:

        st.warning(
            "Please upload at least one resume."
        )

        st.stop()

    # --------------------------------
    # Start analysis
    # --------------------------------

    results = []

    progress = st.progress(0)

    status = st.empty()

    total = len(uploaded_files)

    # --------------------------------
    # Process resumes
    # --------------------------------

    for index, uploaded_file in enumerate(
        uploaded_files
    ):

        status.info(
            f"Analyzing {uploaded_file.name}..."
        )

        temp_path = None

        try:

            # ----------------------------
            # Save uploaded PDF temporarily
            # ----------------------------

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name

            # ----------------------------
            # Run existing evaluator
            # ----------------------------

            result = evaluate_candidate(
                temp_path,
                job_description
            )

            # Keep filename
            result["resume_filename"] = (
                uploaded_file.name
            )

            results.append(result)

        except Exception as e:

            st.error(
                f"Error analyzing "
                f"{uploaded_file.name}: {e}"
            )

        finally:

            # ----------------------------
            # Remove temporary file
            # ----------------------------

            if temp_path and os.path.exists(
                temp_path
            ):

                os.remove(
                    temp_path
                )

        progress.progress(
            (index + 1) / total
        )

    status.success(
        "Candidate analysis completed."
    )

    # ========================================================
    # SORT BY FINAL SCORE
    # ========================================================

    results.sort(
        key=lambda x: x.get(
            "final_score",
            0
        ),
        reverse=True
    )


    # ========================================================
    # SAVE RESULTS IN SESSION
    # ========================================================

    st.session_state[
        "candidate_results"
    ] = results


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "candidate_results" in st.session_state:

    results = st.session_state[
        "candidate_results"
    ]

    if not results:

        st.error(
            "No candidates could be evaluated."
        )

        st.stop()


    # ========================================================
    # SUMMARY
    # ========================================================

    st.markdown(
        "## 🏆 Candidate Ranking"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Candidates",
            len(results)
        )

    with col2:

        st.metric(
            "Top Candidate",
            results[0]["name"]
        )

    with col3:

        st.metric(
            "Top Score",
            f'{results[0]["final_score"]}%'
        )


    st.divider()


    # ========================================================
    # RANKING TABLE
    # ========================================================

    ranking_data = []

    for rank, result in enumerate(
        results,
        start=1
    ):

        ranking_data.append({

            "Rank":
                rank,

            "Candidate":
                result["name"],

            "Final Score":
                f'{result["final_score"]}%',

            "Required Skills":
                f'{result["required_skill_score"]}%',

            "Preferred Skills":
                f'{result["preferred_skill_score"]}%',

            "Evidence":
                f'{result["semantic_evidence_score"]}%',

            "Experience":
                f'{result["experience"]} years'

        })


    st.dataframe(
        ranking_data,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # CANDIDATE DETAILS
    # ========================================================

    st.markdown(
        "## 👤 Candidate Details"
    )


    for rank, result in enumerate(
        results,
        start=1
    ):

        name = result.get(
            "name",
            "Unknown Candidate"
        )

        score = result.get(
            "final_score",
            0
        )

        with st.expander(
            f"#{rank}  {name}  —  {score}%"
        ):

            # --------------------------------
            # Basic information
            # --------------------------------

            st.markdown(
                "### Candidate Information"
            )

            info_col1, info_col2 = st.columns(2)

            with info_col1:

                st.write(
                    f"**Name:** "
                    f"{result.get('name', 'N/A')}"
                )

                st.write(
                    f"**Email:** "
                    f"{result.get('email', 'N/A')}"
                )

                st.write(
                    f"**Phone:** "
                    f"{result.get('phone', 'N/A')}"
                )

            with info_col2:

                st.write(
                    f"**Location:** "
                    f"{result.get('location', 'N/A')}"
                )

                st.write(
                    f"**Experience:** "
                    f"{result.get('experience', 0)} years"
                )

                st.write(
                    f"**Resume:** "
                    f"{result.get('resume_filename', 'N/A')}"
                )


            st.divider()


            # --------------------------------
            # Scores
            # --------------------------------

            st.markdown(
                "### 📊 Candidate Scores"
            )

            score1, score2, score3, score4 = st.columns(4)

            with score1:

                st.metric(
                    "Final Score",
                    f'{result["final_score"]}%'
                )

            with score2:

                st.metric(
                    "Required Skills",
                    f'{result["required_skill_score"]}%'
                )

            with score3:

                st.metric(
                    "Preferred Skills",
                    f'{result["preferred_skill_score"]}%'
                )

            with score4:

                st.metric(
                    "Evidence",
                    f'{result["semantic_evidence_score"]}%'
                )


            # --------------------------------
            # Matched skills
            # --------------------------------

            st.markdown(
                "### ✅ Matched Required Skills"
            )

            matched_required = result.get(
                "matched_required",
                []
            )

            if matched_required:

                st.success(
                    ", ".join(
                        matched_required
                    )
                )

            else:

                st.write(
                    "No required skills matched."
                )


            # --------------------------------
            # Missing skills
            # --------------------------------

            st.markdown(
                "### ❌ Missing Required Skills"
            )

            missing_skills = result.get(
                "missing_skills",
                []
            )

            if missing_skills:

                st.error(
                    ", ".join(
                        missing_skills
                    )
                )

            else:

                st.success(
                    "No missing required skills."
                )


            # --------------------------------
            # Preferred skills
            # --------------------------------

            st.markdown(
                "### ⭐ Matched Preferred Skills"
            )

            matched_preferred = result.get(
                "matched_preferred",
                []
            )

            if matched_preferred:

                st.info(
                    ", ".join(
                        matched_preferred
                    )
                )

            else:

                st.write(
                    "No preferred skills matched."
                )


            # --------------------------------
            # Verified Evidence
            # --------------------------------

            st.markdown(
                "### 🔎 Verified Skill Evidence"
            )

            evidence_list = result.get(
                "evidence",
                []
            )

            if not evidence_list:

                st.write(
                    "No evidence available."
                )

            else:

                for item in evidence_list:

                    skill = item.get(
                        "skill",
                        "Unknown"
                    )

                    verified = item.get(
                        "verified",
                        False
                    )

                    evidence = item.get(
                        "evidence"
                    )

                    if verified and evidence:

                        st.write(
                            f"**{skill}** — "
                            f"✅ VERIFIED"
                        )

                        evidence_col1, evidence_col2 = (
                            st.columns(2)
                        )

                        with evidence_col1:

                            st.write(
                                f"Section: "
                                f"{evidence.get('section', 'N/A')}"
                            )

                            st.write(
                                f"Semantic Score: "
                                f"{evidence.get('score', 0)}%"
                            )

                        with evidence_col2:

                            st.write(
                                f"Quality: "
                                f"{evidence.get('quality', 'N/A')}"
                            )

                            st.write(
                                f"Evidence Strength: "
                                f"{evidence.get('verified_score', 0)}%"
                            )

                        st.caption(
                            evidence.get(
                                "text",
                                ""
                            )
                        )

                    else:

                        st.write(
                            f"**{skill}** — "
                            f"❌ NOT VERIFIED"
                        )

                    st.divider()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="text-align:center; color:#777; padding:30px;">
        Recruiter AI Agent • AI-powered candidate screening
    </div>
    """,
    unsafe_allow_html=True
)