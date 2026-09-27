import os
import sys
import tempfile

import streamlit as st


# ============================================================
# PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.join(
    PROJECT_ROOT,
    "backend"
)


if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT
    )


if BACKEND_DIR not in sys.path:

    sys.path.insert(
        0,
        BACKEND_DIR
    )


# ============================================================
# BACKEND
# ============================================================

from backend.database import (
    init_database,
    get_jobs,
    get_job,
    create_candidate,
    create_application,
    save_evaluation
)


from backend.recruitment_agent import (
    screen_candidate_with_agent
)


init_database()


# ============================================================
# PAGE
# ============================================================

st.set_page_config(

    page_title="Recruiter AI - Candidate Portal",

    page_icon="🤖",

    layout="centered"
)


st.title(
    "🤖 Recruiter AI"
)

st.subheader(
    "Candidate Application Portal"
)

st.write(
    "Select a position and upload your resume. "
    "The Recruitment AI Agent will automatically "
    "screen your application."
)


# ============================================================
# JOBS
# ============================================================

jobs = get_jobs(
    active_only=True
)


if not jobs:

    st.warning(
        "No active jobs are currently available."
    )

    st.stop()


job_options = {

    f"{job['title']} — Job #{job['job_id']}":
    job["job_id"]

    for job in jobs
}


selected_job_label = st.selectbox(

    "Select Position",

    list(
        job_options.keys()
    )
)


selected_job_id = job_options[
    selected_job_label
]


job = get_job(
    selected_job_id
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

with st.expander(
    "View Job Description",
    expanded=True
):

    st.write(
        job["description"]
    )


# ============================================================
# SCREENING INFORMATION
# ============================================================

with st.expander(
    "View General Screening Requirements"
):

    minimum_score = float(
        job.get(
            "minimum_score",
            70
        )
    )


    st.write(
        f"Minimum screening score: "
        f"**{minimum_score:.0f}%**"
    )


    required_skills = job.get(
        "required_skills",
        []
    )


    if required_skills:

        st.write(
            "**Required skills:** "
            + ", ".join(
                required_skills
            )
        )


# ============================================================
# CANDIDATE DETAILS
# ============================================================

st.divider()

st.header(
    "Candidate Details"
)


candidate_name = st.text_input(
    "Full Name"
)


candidate_email = st.text_input(
    "Email Address"
)


# ============================================================
# RESUME
# ============================================================

uploaded_resume = st.file_uploader(

    "Upload Resume",

    type=[
        "pdf"
    ]
)


# ============================================================
# HELPERS
# ============================================================

def get_score(
    result
):

    if not isinstance(
        result,
        dict
    ):

        return 0.0


    for key in [

        "final_candidate_score",

        "final_score",

        "score"
    ]:

        if key in result:

            try:

                return float(
                    result[key]
                )

            except Exception:

                pass


    return 0.0


def get_list(
    result,
    keys
):

    if not isinstance(
        result,
        dict
    ):

        return []


    for key in keys:

        if key not in result:

            continue


        value = result[key]


        if isinstance(
            value,
            list
        ):

            return value


        if isinstance(
            value,
            str
        ):

            if value.strip():

                return [
                    value
                ]


    return []


def normalize_skill(
    skill
):

    return str(
        skill
    ).strip().lower()


def determine_status(
    result,
    job
):

    score = get_score(
        result
    )


    required_skills = job.get(
        "required_skills",
        []
    )


    matched_skills = get_list(

        result,

        [
            "matched_required_skills",

            "matched_skills"
        ]
    )


    missing_required_from_result = get_list(

        result,

        [
            "missing_required_skills",

            "missing_required"
        ]
    )


    # --------------------------------------------------------
    # If the evaluation pipeline explicitly identifies
    # missing required skills, use that information.
    # --------------------------------------------------------

    if missing_required_from_result:

        return (
            "Not Eligible",
            missing_required_from_result
        )


    # --------------------------------------------------------
    # Recruiter-defined required skills.
    #
    # This is a conservative matching check. We only mark a
    # skill as missing when the evaluation result has enough
    # information to identify it.
    # --------------------------------------------------------

    matched_normalized = {

        normalize_skill(skill)

        for skill in matched_skills
    }


    missing_recruiter_skills = []


    for required_skill in required_skills:

        normalized_required = normalize_skill(
            required_skill
        )


        if normalized_required in matched_normalized:

            continue


        # Check partial skill-name matching.

        found = False


        for matched_skill in matched_normalized:

            if (

                normalized_required in matched_skill

                or

                matched_skill in normalized_required
            ):

                found = True

                break


        if not found:

            missing_recruiter_skills.append(
                required_skill
            )


    # --------------------------------------------------------
    # Required skill failure
    # --------------------------------------------------------

    if missing_recruiter_skills:

        return (
            "Not Eligible",
            missing_recruiter_skills
        )


    # --------------------------------------------------------
    # Minimum score
    # --------------------------------------------------------

    if score >= float(
        job.get(
            "minimum_score",
            70
        )
    ):

        return (
            "Shortlisted",
            []
        )


    return (
        "Under Review",
        []
    )


# ============================================================
# SUBMIT
# ============================================================

st.divider()


submit = st.button(

    "🚀 Submit Application & Screen Resume",

    type="primary",

    use_container_width=True
)


if submit:

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not candidate_name.strip():

        st.error(
            "Please enter your name."
        )

        st.stop()


    if not candidate_email.strip():

        st.error(
            "Please enter your email."
        )

        st.stop()


    if uploaded_resume is None:

        st.error(
            "Please upload your resume."
        )

        st.stop()


    # --------------------------------------------------------
    # SAVE TEMP RESUME
    # --------------------------------------------------------

    temp_dir = os.path.join(

        tempfile.gettempdir(),

        "recruiter_ai_agent"
    )


    os.makedirs(

        temp_dir,

        exist_ok=True
    )


    filename = (

        uploaded_resume.name

        .replace(
            " ",
            "_"
        )

        .replace(
            "/",
            "_"
        )

        .replace(
            "\\",
            "_"
        )
    )


    resume_path = os.path.join(

        temp_dir,

        filename
    )


    try:

        with open(

            resume_path,

            "wb"

        ) as file:

            file.write(
                uploaded_resume.getbuffer()
            )


    except Exception as error:

        st.error(
            f"Unable to save resume: {error}"
        )

        st.stop()


    # --------------------------------------------------------
    # AI AGENT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🤖 Recruitment AI Agent"
    )


    progress = st.empty()


    try:

        progress.info(
            "Analyzing job requirements..."
        )


        progress.info(
            "Analyzing candidate resume..."
        )


        result = screen_candidate_with_agent(

            resume_path,

            job["description"]
        )


        progress.info(
            "Calculating candidate eligibility..."
        )


        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        score = get_score(
            result
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status, missing_required = (
            determine_status(
                result,
                job
            )
        )


        # ----------------------------------------------------
        # SKILLS
        # ----------------------------------------------------

        matched_skills = get_list(

            result,

            [
                "matched_required_skills",

                "matched_skills"
            ]
        )


        missing_skills = get_list(

            result,

            [
                "missing_required_skills",

                "missing_skills"
            ]
        )


        # Add recruiter-defined missing skills
        # without duplicating them.

        for skill in missing_required:

            if skill not in missing_skills:

                missing_skills.append(
                    skill
                )


        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        candidate_id = create_candidate(

            name=candidate_name.strip(),

            email=candidate_email.strip(),

            resume_filename=uploaded_resume.name,

            resume_path=resume_path
        )


        application_id = create_application(

            job_id=selected_job_id,

            candidate_id=candidate_id,

            status=status,

            overall_score=score
        )


        save_evaluation(

            application_id,

            result
        )


        progress.success(
            "AI screening completed!"
        )


        # ====================================================
        # RESULT
        # ====================================================

        st.divider()

        st.header(
            "Application Result"
        )


        col1, col2 = st.columns(2)


        with col1:

            st.metric(

                "AI Match Score",

                f"{score:.2f}%"
            )


        with col2:

            st.metric(

                "Status",

                status
            )


        st.write(
            f"**Application ID:** "
            f"APP-{application_id:04d}"
        )


        if status == "Shortlisted":

            st.success(

                "🎉 Your application has been "
                "shortlisted based on the current "
                "screening criteria."
            )


        elif status == "Under Review":

            st.info(

                "⏳ Your application is currently "
                "under review."
            )


        else:

            st.warning(

                "Your application is currently "
                "not eligible based on the defined "
                "screening requirements."
            )


        # ----------------------------------------------------
        # MATCHED
        # ----------------------------------------------------

        st.subheader(
            "✅ Matched Skills"
        )


        if matched_skills:

            for skill in matched_skills:

                st.success(
                    str(skill)
                )

        else:

            st.info(
                "No matched skills detected."
            )


        # ----------------------------------------------------
        # MISSING
        # ----------------------------------------------------

        if missing_skills:

            st.subheader(
                "❌ Missing Skills"
            )


            for skill in missing_skills:

                st.warning(
                    str(skill)
                )


        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        with st.expander(
            "View AI Evaluation Details"
        ):

            st.json(
                result
            )


        st.caption(

            "Your application has been saved and "
            "included in the candidate pool for "
            "this position."
        )


    except Exception as error:

        progress.empty()


        st.error(
            "The Recruitment AI Agent could not "
            "complete the screening."
        )


        st.exception(
            error
        )