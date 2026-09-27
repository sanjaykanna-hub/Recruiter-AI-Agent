import os
import sys

import streamlit as st
import pandas as pd


# ============================================================
# PROJECT PATH SETUP
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.join(
    PROJECT_ROOT,
    "backend"
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ============================================================
# BACKEND IMPORTS
# ============================================================

from backend.database import (
    init_database,
    create_job,
    get_jobs,
    get_job,
    get_applications_for_job,
    get_application,
    update_application_status
)


# ============================================================
# DATABASE
# ============================================================

init_database()


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Recruiter AI - Recruiter Dashboard",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🤖 Recruiter AI")

st.caption(
    "AI-powered candidate screening, ranking and comparison dashboard"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Recruiter Panel")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Create Job",
        "Candidate Comparison"
    ]
)


# ============================================================
# CREATE JOB
# ============================================================

if page == "Create Job":

    st.header("➕ Create New Job")

    st.write(
        "Create a job requirement that candidates can apply for "
        "through the Candidate Portal."
    )

    job_title = st.text_input(
        "Job Title",
        placeholder="React Frontend Developer"
    )

    job_description = st.text_area(
        "Complete Job Description",
        height=450,
        placeholder=(
            "Paste the complete job description here...\n\n"
            "Include required skills, preferred skills, "
            "responsibilities, qualifications and experience."
        )
    )

    if st.button(
        "Create Job",
        type="primary",
        use_container_width=True
    ):

        if not job_title.strip():

            st.error(
                "Please enter a job title."
            )

        elif not job_description.strip():

            st.error(
                "Please enter a job description."
            )

        else:

            job_id = create_job(
                job_title.strip(),
                job_description.strip()
            )

            st.success(
                f"Job created successfully! Job ID: {job_id}"
            )

            st.info(
                "Candidates can now apply for this job "
                "through the Candidate Portal."
            )


# ============================================================
# RECRUITER DASHBOARD
# ============================================================

elif page == "Dashboard":

    st.header("📊 Recruiter Dashboard")

    # --------------------------------------------------------
    # GET ACTIVE JOBS
    # --------------------------------------------------------

    jobs = get_jobs(
        active_only=True
    )

    if not jobs:

        st.info(
            "No active jobs are available."
        )

        st.write(
            "Go to **Create Job** to create your first job."
        )

        st.stop()

    # --------------------------------------------------------
    # JOB SELECTION
    # --------------------------------------------------------

    job_options = {
        f"{job['title']} — Job #{job['job_id']}":
        job["job_id"]
        for job in jobs
    }

    selected_job_label = st.selectbox(
        "Select Job",
        list(job_options.keys())
    )

    selected_job_id = job_options[
        selected_job_label
    ]

    job = get_job(
        selected_job_id
    )

    # --------------------------------------------------------
    # JOB HEADER
    # --------------------------------------------------------

    st.subheader(
        f"💼 {job['title']}"
    )

    with st.expander(
        "View Job Description"
    ):

        st.write(
            job["description"]
        )

    # --------------------------------------------------------
    # GET ALL APPLICATIONS
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # This retrieves EVERY application stored for this job.
    #
    # Therefore every new candidate is automatically included
    # in the cumulative ranking.
    #
    # --------------------------------------------------------

    applications = get_applications_for_job(
        selected_job_id
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    total_candidates = len(
        applications
    )

    shortlisted = len([
        candidate
        for candidate in applications
        if candidate["status"] == "Shortlisted"
    ])

    under_review = len([
        candidate
        for candidate in applications
        if candidate["status"] == "Under Review"
    ])

    not_eligible = len([
        candidate
        for candidate in applications
        if candidate["status"] == "Not Eligible"
    ])

    st.divider()

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "👥 Total Applicants",
        total_candidates
    )

    metric2.metric(
        "✅ Shortlisted",
        shortlisted
    )

    metric3.metric(
        "⏳ Under Review",
        under_review
    )

    metric4.metric(
        "❌ Not Eligible",
        not_eligible
    )

    # --------------------------------------------------------
    # NO APPLICATIONS
    # --------------------------------------------------------

    if not applications:

        st.divider()

        st.info(
            "No candidates have applied for this job yet."
        )

        st.write(
            "Share the Candidate Portal with applicants "
            "so they can upload their resumes."
        )

        st.stop()

    # ========================================================
    # CANDIDATE RANKING
    # ========================================================

    st.divider()

    st.header("🏆 Candidate Ranking")

    st.caption(
        "Candidates are ranked against all applications "
        "received for this job."
    )

    # --------------------------------------------------------
    # RANKING DATA
    # --------------------------------------------------------

    ranking_data = []

    for candidate in applications:

        ranking_data.append({

            "Rank":
                candidate["rank"],

            "Candidate":
                candidate["name"],

            "Application ID":
                f"APP-{candidate['application_id']:04d}",

            "Overall Score":
                round(
                    float(
                        candidate["overall_score"] or 0
                    ),
                    2
                ),

            "Required Skills":
                round(
                    float(
                        candidate["required_skill_score"] or 0
                    ),
                    2
                ),

            "Preferred Skills":
                round(
                    float(
                        candidate["preferred_skill_score"] or 0
                    ),
                    2
                ),

            "Experience":
                round(
                    float(
                        candidate["experience_score"] or 0
                    ),
                    2
                ),

            "Education":
                round(
                    float(
                        candidate["education_score"] or 0
                    ),
                    2
                ),

            "Evidence":
                round(
                    float(
                        candidate["evidence_score"] or 0
                    ),
                    2
                ),

            "Status":
                candidate["status"]
        })


    ranking_df = pd.DataFrame(
        ranking_data
    )


    # --------------------------------------------------------
    # DISPLAY RANKING
    # --------------------------------------------------------

    st.dataframe(
        ranking_df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # SCORE CHART
    # ========================================================

    st.subheader(
        "📈 Candidate Score Distribution"
    )

    chart_data = pd.DataFrame({

        "Candidate": [
            (
                f"#{candidate['rank']} "
                f"{candidate['name']} "
                f"(APP-{candidate['application_id']:04d})"
            )
            for candidate in applications
        ],

        "Overall Score": [
            float(
                candidate["overall_score"] or 0
            )
            for candidate in applications
        ]
    })


    chart_data = chart_data.set_index(
        "Candidate"
    )


    st.bar_chart(
        chart_data
    )


    # ========================================================
    # CANDIDATE DETAILS
    # ========================================================

    st.divider()

    st.header("🔎 Detailed Candidate Evaluation")

    candidate_options = {}

    for candidate in applications:

        application_id = candidate[
            "application_id"
        ]

        rank = candidate[
            "rank"
        ]

        name = candidate[
            "name"
        ]

        score = float(
            candidate[
                "overall_score"
            ] or 0
        )

        label = (
            f"#{rank} — {name} "
            f"(APP-{application_id:04d}) "
            f"— {score:.2f}%"
        )

        candidate_options[
            label
        ] = application_id


    selected_candidate_label = st.selectbox(
        "Select Candidate",
        list(candidate_options.keys())
    )


    selected_application_id = candidate_options[
        selected_candidate_label
    ]


    candidate = get_application(
        selected_application_id
    )


    if candidate:

        # ----------------------------------------------------
        # CANDIDATE HEADER
        # ----------------------------------------------------

        candidate_rank = next(
            (
                item["rank"]
                for item in applications
                if item["application_id"]
                == selected_application_id
            ),
            "-"
        )


        candidate_score = float(
            candidate["overall_score"] or 0
        )


        st.subheader(
            f"#{candidate_rank} — "
            f"{candidate['name']}"
        )


        # ----------------------------------------------------
        # SUMMARY METRICS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "Rank",
            candidate_rank
        )


        col2.metric(
            "Overall Score",
            f"{candidate_score:.2f}%"
        )


        col3.metric(
            "Status",
            candidate["status"]
        )


        col4.metric(
            "Application ID",
            f"APP-{selected_application_id:04d}"
        )


        st.write(
            f"**Email:** {candidate['email']}"
        )


        st.write(
            f"**Resume:** {candidate['resume_filename']}"
        )


        # ----------------------------------------------------
        # SCORE BREAKDOWN
        # ----------------------------------------------------

        st.subheader(
            "📊 AI Score Breakdown"
        )


        score_breakdown = pd.DataFrame({

            "Evaluation": [

                "Required Skills",

                "Preferred Skills",

                "Overall Skills",

                "Keyword Match",

                "Evidence Verification",

                "Hybrid Skills",

                "Experience",

                "Education",

                "Final Candidate Score"
            ],

            "Score": [

                candidate[
                    "required_skill_score"
                ],

                candidate[
                    "preferred_skill_score"
                ],

                candidate[
                    "overall_skill_score"
                ],

                candidate[
                    "keyword_score"
                ],

                candidate[
                    "evidence_score"
                ],

                candidate[
                    "hybrid_skill_score"
                ],

                candidate[
                    "experience_score"
                ],

                candidate[
                    "education_score"
                ],

                candidate[
                    "final_score"
                ]
            ]
        })


        score_breakdown[
            "Score"
        ] = score_breakdown[
            "Score"
        ].apply(
            lambda value:
            f"{float(value or 0):.2f}%"
        )


        st.dataframe(
            score_breakdown,
            use_container_width=True,
            hide_index=True
        )


        # ----------------------------------------------------
        # SKILL ANALYSIS
        # ----------------------------------------------------

        skill_col1, skill_col2 = st.columns(2)


        with skill_col1:

            st.subheader(
                "✅ Matched Skills"
            )


            matched_skills = candidate.get(
                "matched_skills",
                []
            )


            if matched_skills:

                for skill in matched_skills:

                    st.success(
                        str(skill)
                    )

            else:

                st.info(
                    "No matched skills available."
                )


        with skill_col2:

            st.subheader(
                "❌ Missing Skills"
            )


            missing_skills = candidate.get(
                "missing_skills",
                []
            )


            if missing_skills:

                for skill in missing_skills:

                    st.warning(
                        str(skill)
                    )

            else:

                st.success(
                    "No missing skills."
                )


        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        st.subheader(
            "🔎 Evidence Analysis"
        )


        evidence = candidate.get(
            "evidence",
            []
        )


        if evidence:

            st.json(
                evidence
            )

        else:

            st.info(
                "No evidence details available."
            )


        # ----------------------------------------------------
        # RECRUITER STATUS UPDATE
        # ----------------------------------------------------

        st.subheader(
            "👤 Recruiter Decision"
        )


        statuses = [
            "Shortlisted",
            "Under Review",
            "Not Eligible"
        ]


        current_status = candidate[
            "status"
        ]


        if current_status in statuses:

            default_index = statuses.index(
                current_status
            )

        else:

            default_index = 1


        new_status = st.selectbox(
            "Application Status",
            statuses,
            index=default_index
        )


        if st.button(
            "Update Candidate Status",
            type="primary"
        ):

            update_application_status(
                selected_application_id,
                new_status
            )

            st.success(
                "Candidate status updated successfully."
            )

            st.rerun()


# ============================================================
# CANDIDATE COMPARISON
# ============================================================

elif page == "Candidate Comparison":

    st.header("⚖️ Candidate Comparison")

    st.caption(
        "Compare 2–4 candidates who applied for the same job."
    )

    # --------------------------------------------------------
    # GET JOBS
    # --------------------------------------------------------

    jobs = get_jobs(
        active_only=True
    )


    if not jobs:

        st.info(
            "No active jobs are available."
        )

        st.stop()


    # --------------------------------------------------------
    # JOB SELECTION
    # --------------------------------------------------------

    job_options = {
        f"{job['title']} — Job #{job['job_id']}":
        job["job_id"]
        for job in jobs
    }


    selected_job_label = st.selectbox(
        "Select Job",
        list(job_options.keys())
    )


    selected_job_id = job_options[
        selected_job_label
    ]


    selected_job = get_job(
        selected_job_id
    )


    # --------------------------------------------------------
    # GET ALL APPLICATIONS
    # --------------------------------------------------------

    applications = get_applications_for_job(
        selected_job_id
    )


    if len(applications) < 2:

        st.info(
            "At least two candidates are required "
            "for comparison."
        )

        st.stop()


    # --------------------------------------------------------
    # UNIQUE CANDIDATE LABELS
    # --------------------------------------------------------
    #
    # Application ID is included so candidates with the same
    # name do not create duplicate DataFrame columns.
    #
    # Example:
    #
    # Sanjaykanna SV (APP-0001)
    # Sanjaykanna SV (APP-0004)
    #
    # --------------------------------------------------------

    candidate_options = {}


    for candidate in applications:

        application_id = candidate[
            "application_id"
        ]

        rank = candidate[
            "rank"
        ]

        name = candidate[
            "name"
        ]

        score = float(
            candidate[
                "overall_score"
            ] or 0
        )


        label = (
            f"#{rank} — "
            f"{name} "
            f"(APP-{application_id:04d}) "
            f"— {score:.2f}%"
        )


        candidate_options[
            label
        ] = application_id


    # --------------------------------------------------------
    # MULTI SELECT
    # --------------------------------------------------------

    selected_candidates = st.multiselect(
        "Select 2–4 candidates",
        list(candidate_options.keys()),
        max_selections=4
    )


    if len(selected_candidates) < 2:

        st.info(
            "Select at least two candidates "
            "to compare them."
        )

        st.stop()


    # --------------------------------------------------------
    # LOAD RECORDS
    # --------------------------------------------------------

    selected_records = []


    for label in selected_candidates:

        application_id = candidate_options[
            label
        ]


        record = get_application(
            application_id
        )


        if record:

            selected_records.append(
                record
            )


    if len(selected_records) < 2:

        st.error(
            "Unable to load enough candidate records."
        )

        st.stop()


    # ========================================================
    # COMPARISON HEADER
    # ========================================================

    st.divider()


    st.subheader(
        f"📊 Comparing Candidates — "
        f"{selected_job['title']}"
    )


    # --------------------------------------------------------
    # UNIQUE COLUMN NAMES
    # --------------------------------------------------------

    comparison_names = []


    for candidate in selected_records:

        unique_name = (
            f"{candidate['name']} "
            f"(APP-{candidate['application_id']:04d})"
        )


        comparison_names.append(
            unique_name
        )


    # ========================================================
    # COMPARISON DATA
    # ========================================================

    comparison_data = {

        "Required Skills": [],

        "Preferred Skills": [],

        "Overall Skills": [],

        "Keyword Match": [],

        "Evidence": [],

        "Hybrid Skills": [],

        "Experience": [],

        "Education": [],

        "Final Score": []
    }


    for candidate in selected_records:

        comparison_data[
            "Required Skills"
        ].append(
            float(
                candidate[
                    "required_skill_score"
                ] or 0
            )
        )


        comparison_data[
            "Preferred Skills"
        ].append(
            float(
                candidate[
                    "preferred_skill_score"
                ] or 0
            )
        )


        comparison_data[
            "Overall Skills"
        ].append(
            float(
                candidate[
                    "overall_skill_score"
                ] or 0
            )
        )


        comparison_data[
            "Keyword Match"
        ].append(
            float(
                candidate[
                    "keyword_score"
                ] or 0
            )
        )


        comparison_data[
            "Evidence"
        ].append(
            float(
                candidate[
                    "evidence_score"
                ] or 0
            )
        )


        comparison_data[
            "Hybrid Skills"
        ].append(
            float(
                candidate[
                    "hybrid_skill_score"
                ] or 0
            )
        )


        comparison_data[
            "Experience"
        ].append(
            float(
                candidate[
                    "experience_score"
                ] or 0
            )
        )


        comparison_data[
            "Education"
        ].append(
            float(
                candidate[
                    "education_score"
                ] or 0
            )
        )


        comparison_data[
            "Final Score"
        ].append(
            float(
                candidate[
                    "final_score"
                ] or 0
            )
        )


    # ========================================================
    # DATAFRAME
    # ========================================================

    comparison_df = pd.DataFrame(
        comparison_data,
        index=comparison_names
    )


    # Transpose:
    #
    # Evaluation | Candidate A | Candidate B
    #
    comparison_df = comparison_df.T


    # --------------------------------------------------------
    # FORMAT
    # --------------------------------------------------------

    comparison_display_df = (
        comparison_df.copy()
    )


    for column in comparison_display_df.columns:

        comparison_display_df[
            column
        ] = comparison_display_df[
            column
        ].apply(
            lambda value:
            f"{float(value):.2f}%"
        )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    st.dataframe(
        comparison_display_df,
        use_container_width=True
    )


    # ========================================================
    # SCORE CHART
    # ========================================================

    st.subheader(
        "📈 Overall Candidate Scores"
    )


    chart_data = pd.DataFrame({

        "Candidate": [

            (
                f"#{candidate['application_id']} "
                f"{candidate['name']} "
                f"(APP-{candidate['application_id']:04d})"
            )

            for candidate in selected_records
        ],

        "Overall Score": [

            float(
                candidate[
                    "final_score"
                ] or 0
            )

            for candidate in selected_records
        ]
    })


    chart_data = chart_data.set_index(
        "Candidate"
    )


    st.bar_chart(
        chart_data
    )


    # ========================================================
    # DETAILED COMPARISON
    # ========================================================

    st.divider()


    st.subheader(
        "🔎 Detailed Candidate Analysis"
    )


    for candidate in selected_records:

        application_id = candidate[
            "application_id"
        ]

        candidate_name = candidate[
            "name"
        ]

        final_score = float(
            candidate[
                "final_score"
            ] or 0
        )


        rank = next(
            (
                item["rank"]
                for item in applications
                if item["application_id"]
                == application_id
            ),
            "-"
        )


        with st.expander(
            f"#{rank} — "
            f"{candidate_name} "
            f"(APP-{application_id:04d}) "
            f"— {final_score:.2f}%",
            expanded=True
        ):

            # ------------------------------------------------
            # SUMMARY
            # ------------------------------------------------

            col1, col2, col3, col4 = st.columns(4)


            col1.metric(
                "Rank",
                rank
            )


            col2.metric(
                "Overall Score",
                f"{final_score:.2f}%"
            )


            col3.metric(
                "Status",
                candidate["status"]
            )


            col4.metric(
                "Application ID",
                f"APP-{application_id:04d}"
            )


            st.write(
                f"**Email:** {candidate['email']}"
            )


            st.write(
                f"**Resume:** "
                f"{candidate['resume_filename']}"
            )


            # ------------------------------------------------
            # SCORE BREAKDOWN
            # ------------------------------------------------

            st.markdown(
                "### 📊 Score Breakdown"
            )


            detailed_scores = pd.DataFrame({

                "Evaluation": [

                    "Required Skills",

                    "Preferred Skills",

                    "Overall Skills",

                    "Keyword Match",

                    "Evidence",

                    "Hybrid Skills",

                    "Experience",

                    "Education",

                    "Final Score"
                ],

                "Score": [

                    candidate[
                        "required_skill_score"
                    ],

                    candidate[
                        "preferred_skill_score"
                    ],

                    candidate[
                        "overall_skill_score"
                    ],

                    candidate[
                        "keyword_score"
                    ],

                    candidate[
                        "evidence_score"
                    ],

                    candidate[
                        "hybrid_skill_score"
                    ],

                    candidate[
                        "experience_score"
                    ],

                    candidate[
                        "education_score"
                    ],

                    candidate[
                        "final_score"
                    ]
                ]
            })


            detailed_scores[
                "Score"
            ] = detailed_scores[
                "Score"
            ].apply(
                lambda value:
                f"{float(value or 0):.2f}%"
            )


            st.dataframe(
                detailed_scores,
                use_container_width=True,
                hide_index=True
            )


            # ------------------------------------------------
            # SKILLS
            # ------------------------------------------------

            skill_col1, skill_col2 = st.columns(2)


            with skill_col1:

                st.markdown(
                    "### ✅ Matched Skills"
                )


                matched = candidate.get(
                    "matched_skills",
                    []
                )


                if matched:

                    for skill in matched:

                        st.success(
                            str(skill)
                        )

                else:

                    st.info(
                        "No matched skills available."
                    )


            with skill_col2:

                st.markdown(
                    "### ❌ Missing Skills"
                )


                missing = candidate.get(
                    "missing_skills",
                    []
                )


                if missing:

                    for skill in missing:

                        st.warning(
                            str(skill)
                        )

                else:

                    st.success(
                        "No missing skills."
                    )


            # ------------------------------------------------
            # EVIDENCE
            # ------------------------------------------------

            st.markdown(
                "### 🔎 Evidence Analysis"
            )


            evidence = candidate.get(
                "evidence",
                []
            )


            if evidence:

                st.json(
                    evidence
                )

            else:

                st.info(
                    "No evidence details available."
                )