import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

# Load the project's .env file before importing modules that read API keys.
PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)

import streamlit as st

import pandas as pd

import json

import re

from datetime import date, time

try:
    from backend.recruitment_agent import screen_candidate_with_agent
    AGENT_IMPORT_ERROR = None
except Exception as agent_import_error:
    screen_candidate_with_agent = None
    AGENT_IMPORT_ERROR = str(agent_import_error)

from backend.database import (

    get_jobs,

    create_job,

    get_job,

    update_job_criteria,

    get_applications_for_job,

    get_application,

    update_application_status,

    create_interview,

    get_interviews_for_application,
    reschedule_interview,
    cancel_interview,
    get_candidate

)

# ============================================================

# PAGE CONFIGURATION

# ============================================================

st.set_page_config(

    page_title="Recruiter AI Agent",

    page_icon="🤖",

    layout="wide"

)

# ============================================================

# HEADER

# ============================================================

st.title("🤖 Recruiter AI Agent")

st.caption(

    "AI-powered candidate screening, ranking and recruitment management"

)

# ============================================================

# SIDEBAR

# ============================================================

st.sidebar.title("Recruiter Portal")

page = st.sidebar.radio(

    "Navigation",

    [

        "Dashboard",

        "Create Job",

        "Candidate Comparison",
        "Agentic AI Screening"

    ]

)

# ============================================================

# HELPER FUNCTIONS

# ============================================================

def format_score(value):

    try:

        return f"{float(value):.2f}%"

    except Exception:

        return "0.00%"

def normalize_skill(skill):

    return (

        str(skill)

        .strip()

        .lower()

        .replace(".", "")

        .replace("-", "")

        .replace("_", "")

        .replace(" ", "")

    )

def skills_to_text(skills):

    if not skills:

        return "None"

    return ", ".join(

        str(skill)

        for skill in skills

    )

def safe_json(value, default=None):

    if default is None:

        default = []

    if value is None:

        return default

    if isinstance(value, (list, dict)):

        return value

    try:

        return json.loads(value)

    except Exception:

        return default

def make_clickable_url(url):

    if not url:

        return None

    url = str(url).strip()

    if not url:

        return None

    if not url.startswith(

        ("http://", "https://")

    ):

        url = "https://" + url

    return url

def extract_resume_links(evaluation):

    """Extract LinkedIn, GitHub, and other URLs from saved evaluation data."""

    if not isinstance(evaluation, dict):

        return {}

    links = {}

    for label, key in (("LinkedIn", "linkedin"), ("GitHub", "github")):

        value = evaluation.get(key)

        if isinstance(value, str) and value.strip():

            url = make_clickable_url(value)

            if url:

                links[label] = url

    text = json.dumps(evaluation, ensure_ascii=False)

    patterns = {

        "LinkedIn": r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s\"\'<>]+",

        "GitHub": r"(?:https?://)?(?:www\.)?github\.com/[^\s\"\'<>]+",

    }

    for label, pattern in patterns.items():

        if label not in links:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:

                url = make_clickable_url(match.group(0).rstrip(".,);]}"))

                if url:

                    links[label] = url

    urls = re.findall(r"https?://[^\s\"\'<>]+", text, re.IGNORECASE)

    other = []

    for value in urls:

        url = value.rstrip(".,);]}")

        lower = url.lower()

        if "linkedin.com" not in lower and "github.com" not in lower and url not in other:

            other.append(url)

    for index, url in enumerate(other[:5], start=1):

        links[f"Website {index}"] = url

    return links

# ============================================================

# CREATE JOB

# ============================================================

if page == "Create Job":

    st.header("Create New Job")

    title = st.text_input(

        "Job Title",

        placeholder="React Frontend Developer"

    )

    description = st.text_area(

        "Job Description",

        height=250,

        placeholder=(

            "Enter the complete job description, "

            "responsibilities and qualifications..."

        )

    )

    st.subheader("Screening Criteria")

    minimum_score = st.slider(

        "Minimum Screening Score",

        min_value=0,

        max_value=100,

        value=70,

        step=5

    )

    required_text = st.text_area(

        "Required Skills",

        placeholder=(

            "React.js\n"

            "JavaScript\n"

            "HTML\n"

            "CSS\n"

            "Git"

        ),

        height=150

    )

    preferred_text = st.text_area(

        "Preferred Skills",

        placeholder=(

            "TypeScript\n"

            "Redux\n"

            "Next.js"

        ),

        height=120

    )

    if st.button(

        "Create Job",

        type="primary"

    ):

        if not title.strip():

            st.error(

                "Please enter a job title."

            )

        elif not description.strip():

            st.error(

                "Please enter a job description."

            )

        else:

            required_skills = [

                skill.strip()

                for skill in required_text.splitlines()

                if skill.strip()

            ]

            preferred_skills = [

                skill.strip()

                for skill in preferred_text.splitlines()

                if skill.strip()

            ]

            job_id = create_job(

                title=title.strip(),

                description=description.strip(),

                minimum_score=minimum_score,

                required_skills=required_skills,

                preferred_skills=preferred_skills

            )

            st.success(

                f"Job created successfully! Job ID: {job_id}"

            )

# ============================================================

# DASHBOARD

# ============================================================

elif page == "Dashboard":

    st.header("Recruiter Dashboard")

    jobs = get_jobs()

    if not jobs:

        st.info(

            "No jobs have been created yet. "

            "Create a job first."

        )

        st.stop()

    job_options = {

        f"{job['title']} (ID: {job['id']})":

        job["id"]

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

    if not job:

        st.error(

            "Unable to load selected job."

        )

        st.stop()

    # ========================================================

    # JOB INFORMATION

    # ========================================================

    st.subheader(

        f"📋 {job['title']}"

    )

    with st.expander(

        "View Job Description",

        expanded=True

    ):

        st.write(

            job["description"]

        )

    # ========================================================

    # SCREENING CRITERIA

    # ========================================================

    st.subheader(

        "⚙️ Screening Criteria"

    )

    criteria_col1, criteria_col2 = st.columns(2)

    with criteria_col1:

        st.write(

            f"**Minimum Score:** "

            f"{job['minimum_score']}%"

        )

        st.write(

            "**Required Skills:**"

        )

        if job["required_skills"]:

            for skill in job["required_skills"]:

                st.write(

                    f"• {skill}"

                )

        else:

            st.write("None")

    with criteria_col2:

        st.write(

            "**Preferred Skills:**"

        )

        if job["preferred_skills"]:

            for skill in job["preferred_skills"]:

                st.write(

                    f"• {skill}"

                )

        else:

            st.write("None")

    # ========================================================

    # UPDATE CRITERIA

    # ========================================================

    with st.expander(

        "Edit Screening Criteria"

    ):

        new_minimum_score = st.slider(

            "Minimum Score",

            min_value=0,

            max_value=100,

            value=int(

                job["minimum_score"]

            ),

            step=5,

            key=f"minimum_{job['id']}"

        )

        new_required_text = st.text_area(

            "Required Skills — one per line",

            value="\n".join(

                job["required_skills"]

            ),

            key=f"required_{job['id']}"

        )

        new_preferred_text = st.text_area(

            "Preferred Skills — one per line",

            value="\n".join(

                job["preferred_skills"]

            ),

            key=f"preferred_{job['id']}"

        )

        if st.button(

            "Save Screening Criteria",

            key=f"save_criteria_{job['id']}"

        ):

            new_required = [

                skill.strip()

                for skill in new_required_text.splitlines()

                if skill.strip()

            ]

            new_preferred = [

                skill.strip()

                for skill in new_preferred_text.splitlines()

                if skill.strip()

            ]

            update_job_criteria(

                job_id=job["id"],

                minimum_score=new_minimum_score,

                required_skills=new_required,

                preferred_skills=new_preferred

            )

            st.success(

                "Screening criteria updated."

            )

            st.rerun()

    # ========================================================

    # APPLICATIONS

    # ========================================================

    applications = get_applications_for_job(

        job["id"]

    )

    st.subheader(

        "Candidate Pipeline"

    )

    if not applications:

        st.info(

            "No candidates have applied for this job yet."

        )

        st.stop()

    # ========================================================

    # METRICS

    # ========================================================

    total = len(applications)

    shortlisted = sum(

        1

        for app in applications

        if app["status"] == "Shortlisted"

    )

    under_review = sum(

        1

        for app in applications

        if app["status"] == "Under Review"

    )

    not_eligible = sum(

        1

        for app in applications

        if app["status"] == "Not Eligible"

    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(

        "Total Applicants",

        total

    )

    col2.metric(

        "Shortlisted",

        shortlisted

    )

    col3.metric(

        "Under Review",

        under_review

    )

    col4.metric(

        "Not Eligible",

        not_eligible

    )

    # ========================================================

    # FILTERS

    # ========================================================

    st.subheader(

        "🔎 Candidate Filters"

    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:

        status_filter = st.selectbox(

            "Status",

            [

                "All",

                "Shortlisted",

                "Under Review",

                "Not Eligible"

            ]

        )

    with filter_col2:

        minimum_filter = st.slider(

            "Minimum Score",

            min_value=0,

            max_value=100,

            value=0,

            step=5

        )

    with filter_col3:

        sort_option = st.selectbox(

            "Sort By",

            [

                "Overall Score",

                "Required Skills",

                "Experience",

                "Education",

                "Evidence"

            ]

        )

    filtered = applications.copy()

    if status_filter != "All":

        filtered = [

            app

            for app in filtered

            if app["status"] == status_filter

        ]

    filtered = [

        app

        for app in filtered

        if float(

            app.get(

                "final_candidate_score",

                0

            ) or 0

        ) >= minimum_filter

    ]

    sort_mapping = {

        "Overall Score":

            "final_candidate_score",

        "Required Skills":

            "required_skill_score",

        "Experience":

            "experience_score",

        "Education":

            "education_score",

        "Evidence":

            "evidence_score"

    }

    sort_key = sort_mapping[

        sort_option

    ]

    filtered.sort(

        key=lambda x: float(

            x.get(

                sort_key,

                0

            ) or 0

        ),

        reverse=True

    )

    # ========================================================

    # RANKING TABLE

    # ========================================================

    st.subheader(

        "🏆 Candidate Ranking"

    )

    if not filtered:

        st.warning(

            "No candidates match the current filters."

        )

    else:

        table_data = []

        for rank, candidate in enumerate(

            filtered,

            start=1

        ):

            table_data.append({

                "Rank":

                    rank,

                "Candidate":

                    candidate["name"],

                "Application ID":

                    candidate["application_id"],

                "Overall Score":

                    format_score(

                        candidate[

                            "final_candidate_score"

                        ]

                    ),

                "Required Skills":

                    format_score(

                        candidate[

                            "required_skill_score"

                        ]

                    ),

                "Preferred Skills":

                    format_score(

                        candidate[

                            "preferred_skill_score"

                        ]

                    ),

                "Experience":

                    format_score(

                        candidate[

                            "experience_score"

                        ]

                    ),

                "Education":

                    format_score(

                        candidate[

                            "education_score"

                        ]

                    ),

                "Evidence":

                    format_score(

                        candidate[

                            "evidence_score"

                        ]

                    ),

                "Status":

                    candidate["status"]

            })

        df = pd.DataFrame(

            table_data

        )

        st.dataframe(

            df,

            width="stretch",

            hide_index=True

        )

    # ========================================================

    # SCORE CHART

    # ========================================================

    if filtered:

        st.subheader(

            "📊 Candidate Scores"

        )

        chart_data = pd.DataFrame({

            "Candidate": [

                f"#{index + 1} "

                f"{candidate['name']}"

                for index, candidate

                in enumerate(filtered)

            ],

            "Score": [

                float(

                    candidate.get(

                        "final_candidate_score",

                        0

                    ) or 0

                )

                for candidate in filtered

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

    st.subheader(

        "👤 Candidate Details"

    )

    candidate_options = {

        f"{candidate['name']} "

        f"(Application #{candidate['application_id']})":

        candidate["application_id"]

        for candidate in filtered

    }

    if candidate_options:

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

            st.markdown(

                f"### {candidate['name']}"

            )

            info_col1, info_col2, info_col3 = st.columns(3)

            with info_col1:

                st.write(

                    f"**Email:** "

                    f"{candidate['email']}"

                )

            with info_col2:

                st.write(

                    f"**Application ID:** "

                    f"{candidate['id']}"

                )

            with info_col3:

                st.write(

                    f"**Status:** "

                    f"{candidate['status']}"

                )

            # =================================================

            # SCORE BREAKDOWN

            # =================================================

            st.subheader(

                "Score Breakdown"

            )

            score_data = {

                "Required Skills":

                    candidate[

                        "required_skill_score"

                    ],

                "Preferred Skills":

                    candidate[

                        "preferred_skill_score"

                    ],

                "Overall Skills":

                    candidate[

                        "overall_skill_score"

                    ],

                "Keyword":

                    candidate[

                        "keyword_score"

                    ],

                "Evidence":

                    candidate[

                        "evidence_score"

                    ],

                "Hybrid Skills":

                    candidate[

                        "hybrid_skill_score"

                    ],

                "Experience":

                    candidate[

                        "experience_score"

                    ],

                "Education":

                    candidate[

                        "education_score"

                    ],

                "Final Score":

                    candidate[

                        "final_candidate_score"

                    ]

            }

            score_df = pd.DataFrame({

                "Metric":

                    list(score_data.keys()),

                "Score":

                    list(score_data.values())

            })

            st.dataframe(

                score_df,

                use_container_width=True,

                hide_index=True

            )

            # =================================================

            # SKILLS

            # =================================================

            skills_col1, skills_col2 = st.columns(2)

            with skills_col1:

                st.subheader(

                    "✅ Matched Skills"

                )

                matched = (

                    candidate.get(

                        "matched_required_skills"

                    )

                    or candidate.get(

                        "matched_skills"

                    )

                    or []

                )

                if matched:

                    for skill in matched:

                        st.write(

                            f"• {skill}"

                        )

                else:

                    st.write(

                        "No matched skills found."

                    )

            with skills_col2:

                st.subheader(

                    "❌ Missing Skills"

                )

                missing = (

                    candidate.get(

                        "missing_required_skills"

                    )

                    or candidate.get(

                        "missing_skills"

                    )

                    or []

                )

                if missing:

                    for skill in missing:

                        st.write(

                            f"• {skill}"

                        )

                else:

                    st.write(

                        "No missing skills."

                    )

            # =================================================

            # AI EVALUATION

            # =================================================

            st.subheader(

                "🤖 AI Evaluation"

            )

            evaluation = candidate.get(

                "evaluation_json"

            )

            if evaluation:

                # -------------------------------------------------

                # Candidate information

                # -------------------------------------------------

                candidate_name = evaluation.get(

                    "name",

                    candidate.get(

                        "name",

                        "Unknown"

                    )

                )

                candidate_email = evaluation.get(

                    "email",

                    candidate.get(

                        "email",

                        ""

                    )

                )

                candidate_phone = evaluation.get(

                    "phone",

                    ""

                )

                candidate_location = evaluation.get(

                    "location",

                    ""

                )

                # -------------------------------------------------

                # PROFESSIONAL LINKS

                # -------------------------------------------------

                resume_links = extract_resume_links(

                    evaluation

                )

                if resume_links:

                    st.markdown(

                        "#### 🔗 Professional Links"

                    )

                    link_columns = st.columns(

                        len(resume_links)

                    )

                    for column, (

                        label,

                        url

                    ) in zip(

                        link_columns,

                        resume_links.items()

                    ):

                        with column:

                            if label == "LinkedIn":

                                icon = "🔗"

                            elif label == "GitHub":

                                icon = "💻"

                            else:

                                icon = "🌐"

                            st.link_button(

                                f"{icon} Open {label}",

                                url,

                                use_container_width=True

                            )

                # -------------------------------------------------

                # CANDIDATE PROFILE

                # -------------------------------------------------

                st.markdown(

                    "#### 👤 Candidate Profile"

                )

                profile_col1, profile_col2, profile_col3 = st.columns(3)

                with profile_col1:

                    st.write(

                        "**Name**"

                    )

                    st.write(

                        candidate_name

                    )

                with profile_col2:

                    st.write(

                        "**Email**"

                    )

                    if candidate_email:

                        st.markdown(

                            f"[{candidate_email}]"

                            f"(mailto:{candidate_email})"

                        )

                    else:

                        st.write(

                            "Not available"

                        )

                with profile_col3:

                    st.write(

                        "**Phone**"

                    )

                    if candidate_phone:

                        st.markdown(

                            f"[{candidate_phone}]"

                            f"(tel:{candidate_phone})"

                        )

                    else:

                        st.write(

                            "Not available"

                        )

                if candidate_location:

                    st.write(

                        f"📍 **Location:** "

                        f"{candidate_location}"

                    )

                # -------------------------------------------------

                # AI MATCH SUMMARY

                # -------------------------------------------------

                st.markdown(

                    "#### 🎯 AI Match Summary"

                )

                summary_col1, summary_col2, summary_col3 = st.columns(3)

                final_score = float(

                    evaluation.get(

                        "final_score",

                        candidate.get(

                            "final_candidate_score",

                            0

                        )

                    ) or 0

                )

                required_score = float(

                    evaluation.get(

                        "required_skill_score",

                        candidate.get(

                            "required_skill_score",

                            0

                        )

                    ) or 0

                )

                hybrid_score = float(

                    evaluation.get(

                        "hybrid_skill_score",

                        candidate.get(

                            "hybrid_skill_score",

                            0

                        )

                    ) or 0

                )

                with summary_col1:

                    st.metric(

                        "🎯 Final Match",

                        f"{final_score:.2f}%"

                    )

                with summary_col2:

                    st.metric(

                        "🧠 Required Skills",

                        f"{required_score:.2f}%"

                    )

                with summary_col3:

                    st.metric(

                        "🔍 Verified Skills",

                        f"{hybrid_score:.2f}%"

                    )

                # -------------------------------------------------

                # REQUIRED SKILL ANALYSIS

                # -------------------------------------------------

                st.markdown(

                    "#### 🛠️ Required Skill Analysis"

                )

                required_skills = safe_json(

                    evaluation.get(

                        "required_skills"

                    ),

                    []

                )

                matched_skills = safe_json(

                    evaluation.get(

                        "matched_required"

                    )

                    or evaluation.get(

                        "matched_skills"

                    ),

                    []

                )

                missing_skills = safe_json(

                    evaluation.get(

                        "missing_skills"

                    ),

                    []

                )

                skill_rows = []

                for skill in required_skills:

                    normalized_skill = normalize_skill(

                        skill

                    )

                    matched = any(

                        normalize_skill(

                            matched_skill

                        ) == normalized_skill

                        for matched_skill

                        in matched_skills

                    )

                    missing = any(

                        normalize_skill(

                            missing_skill

                        ) == normalized_skill

                        for missing_skill

                        in missing_skills

                    )

                    if matched:

                        status = "✅ Matched"

                        explanation = (

                            "Skill found in candidate resume"

                        )

                    elif missing:

                        status = "❌ Missing"

                        explanation = (

                            "Required skill was not found"

                        )

                    else:

                        status = "⚠️ Unverified"

                        explanation = (

                            "Skill could not be confidently verified"

                        )

                    skill_rows.append({

                        "Required Skill":

                            skill,

                        "Status":

                            status,

                        "AI Assessment":

                            explanation

                    })

                if skill_rows:

                    skill_df = pd.DataFrame(

                        skill_rows

                    )

                    st.dataframe(

                        skill_df,

                        use_container_width=True,

                        hide_index=True

                    )

                else:

                    st.info(

                        "No required skill analysis available."

                    )

                # -------------------------------------------------

                # MATCHED / MISSING SKILLS

                # -------------------------------------------------

                skill_col1, skill_col2 = st.columns(2)

                with skill_col1:

                    st.markdown(

                        "##### ✅ Matched Skills"

                    )

                    if matched_skills:

                        for skill in matched_skills:

                            st.success(

                                str(skill)

                            )

                    else:

                        st.info(

                            "No matched skills."

                        )

                with skill_col2:

                    st.markdown(

                        "##### ❌ Missing Skills"

                    )

                    if missing_skills:

                        for skill in missing_skills:

                            st.error(

                                str(skill)

                            )

                    else:

                        st.success(

                            "No missing required skills."

                        )

                # -------------------------------------------------

                # EXPERIENCE & EDUCATION

                # -------------------------------------------------

                st.markdown(

                    "#### 🎓 Experience & Education"

                )

                exp_col1, exp_col2, exp_col3 = st.columns(3)

                experience = evaluation.get(

                    "experience",

                    0

                )

                experience_score = float(

                    evaluation.get(

                        "experience_score",

                        candidate.get(

                            "experience_score",

                            0

                        )

                    ) or 0

                )

                education_score = float(

                    evaluation.get(

                        "education_score",

                        candidate.get(

                            "education_score",

                            0

                        )

                    ) or 0

                )

                with exp_col1:

                    st.metric(

                        "Experience",

                        f"{experience} years"

                    )

                with exp_col2:

                    st.metric(

                        "Experience Score",

                        f"{experience_score:.1f}%"

                    )

                with exp_col3:

                    st.metric(

                        "Education Score",

                        f"{education_score:.1f}%"

                    )

                # -------------------------------------------------

                # AI VERIFIED EVIDENCE

                # -------------------------------------------------

                st.markdown(

                    "#### 🔎 AI Verified Evidence"

                )

                evidence = safe_json(

                    evaluation.get(

                        "evidence"

                    ),

                    []

                )

                if isinstance(

                    evidence,

                    dict

                ):

                    evidence = list(

                        evidence.values()

                    )

                if evidence:

                    for item in evidence:

                        if not isinstance(

                            item,

                            dict

                        ):

                            continue

                        skill = item.get(

                            "skill",

                            "Unknown Skill"

                        )

                        verified = item.get(

                            "verified",

                            False

                        )

                        evidence_data = (

                            item.get(

                                "evidence"

                            ) or {}

                        )

                        section = evidence_data.get(

                            "section",

                            "Resume"

                        )

                        confidence = float(

                            evidence_data.get(

                                "score",

                                0

                            ) or 0

                        )

                        evidence_text = (

                            evidence_data.get(

                                "text",

                                ""

                            )

                        )

                        if verified:

                            status = "✅ Verified"

                        else:

                            status = "❌ Not Verified"

                        with st.expander(

                            f"{status} — {skill} "

                            f"(Confidence: "

                            f"{confidence:.2f}%)"

                        ):

                            st.write(

                                f"**Resume Section:** "

                                f"{section}"

                            )

                            if evidence_text:

                                st.write(

                                    "**Supporting Evidence:**"

                                )

                                st.info(

                                    evidence_text

                                )

                            else:

                                st.write(

                                    "No supporting evidence found."

                                )

                else:

                    st.info(

                        "No detailed evidence available."

                    )

                # -------------------------------------------------

                # DETAILED AI SCORES

                # -------------------------------------------------

                st.markdown(

                    "#### 📊 Detailed AI Scores"

                )

                detailed_scores = {

                    "Required Skill Score":

                        evaluation.get(

                            "required_skill_score",

                            candidate.get(

                                "required_skill_score",

                                0

                            )

                        ),

                    "Preferred Skill Score":

                        evaluation.get(

                            "preferred_skill_score",

                            candidate.get(

                                "preferred_skill_score",

                                0

                            )

                        ),

                    "Overall Skill Score":

                        evaluation.get(

                            "overall_skill_score",

                            candidate.get(

                                "overall_skill_score",

                                0

                            )

                        ),

                    "Keyword Score":

                        evaluation.get(

                            "keyword_skill_score",

                            evaluation.get(

                                "keyword_score",

                                candidate.get(

                                    "keyword_score",

                                    0

                                )

                            )

                        ),

                    "Semantic Evidence":

                        evaluation.get(

                            "semantic_evidence_score",

                            candidate.get(

                                "evidence_score",

                                0

                            )

                        ),

                    "Hybrid Skill Score":

                        evaluation.get(

                            "hybrid_skill_score",

                            candidate.get(

                                "hybrid_skill_score",

                                0

                            )

                        ),

                    "Experience Score":

                        evaluation.get(

                            "experience_score",

                            candidate.get(

                                "experience_score",

                                0

                            )

                        ),

                    "Education Score":

                        evaluation.get(

                            "education_score",

                            candidate.get(

                                "education_score",

                                0

                            )

                        ),

                    "Final Score":

                        evaluation.get(

                            "final_score",

                            candidate.get(

                                "final_candidate_score",

                                0

                            )

                        )

                }

                score_table = []

                for metric, value in detailed_scores.items():

                    try:

                        numeric_value = float(

                            value or 0

                        )

                    except Exception:

                        numeric_value = 0

                    score_table.append({

                        "AI Metric":

                            metric,

                        "Score":

                            f"{numeric_value:.2f}%"

                    })

                st.dataframe(

                    pd.DataFrame(

                        score_table

                    ),

                    use_container_width=True,

                    hide_index=True

                )

                # -------------------------------------------------

                # RAW JSON - DEVELOPER ONLY

                # -------------------------------------------------

                with st.expander(

                    "🔧 Developer: View Raw AI Evaluation"

                ):

                    st.json(

                        evaluation

                    )

            else:

                st.info(

                    "No detailed AI evaluation available."

                )

            # =================================================

            # MANUAL STATUS

            # =================================================

            st.subheader(

                "Recruiter Decision"

            )

            status_options = [

                "Shortlisted",

                "Under Review",

                "Not Eligible",

                "Rejected",

                "Interview Scheduled",

                "Selected"

            ]

            current_status = candidate["status"]

            if current_status in status_options:

                current_index = (

                    status_options.index(

                        current_status

                    )

                )

            else:

                current_index = 1

            new_status = st.selectbox(

                "Update Candidate Status",

                status_options,

                index=current_index,

                key=f"status_select_{candidate['id']}"

            )

            if st.button(

                "Save Candidate Status",

                key=f"status_{candidate['id']}"

            ):

                update_application_status(

                    candidate["id"],

                    new_status

                )

                st.success(

                    "Candidate status updated."

                )

                st.rerun()

            # =================================================

            # INTERVIEW SCHEDULING

            # =================================================

            st.divider()

            st.subheader(

                "📅 Interview Scheduling"

            )

            with st.form(

                f"schedule_interview_{candidate['id']}"

            ):

                interview_date = st.date_input(

                    "Interview Date",

                    value=date.today(),

                    min_value=date.today()

                )

                interview_time = st.time_input(

                    "Interview Time",

                    value=time(10, 0)

                )

                interview_type = st.selectbox(

                    "Interview Type",

                    [

                        "Technical",

                        "HR",

                        "Managerial",

                        "Technical + HR"

                    ]

                )

                interviewer = st.text_input(

                    "Interviewer Name",

                    placeholder="Enter interviewer name"

                )

                meeting_link = st.text_input(

                    "Meeting Link",

                    placeholder=(

                        "https://meet.google.com/..."

                    )

                )

                notes = st.text_area(

                    "Interview Notes",

                    placeholder=(

                        "Additional instructions "

                        "or interview notes..."

                    )

                )

                schedule_button = st.form_submit_button(

                    "📅 Schedule Interview",

                    type="primary"

                )

                if schedule_button:

                    if not interviewer.strip():

                        st.error(

                            "Please enter the interviewer name."

                        )

                    else:

                        interview_id = create_interview(

                            application_id=

                                candidate["id"],

                            interview_date=

                                str(interview_date),

                            interview_time=

                                str(interview_time),

                            interview_type=

                                interview_type,

                            interviewer=

                                interviewer.strip(),

                            meeting_link=

                                meeting_link.strip(),

                            notes=

                                notes.strip()

                        )

                        update_application_status(

                            candidate["id"],

                            "Interview Scheduled"

                        )

                        st.success(

                            "Interview scheduled successfully!"

                        )

                        st.info(

                            f"Interview ID: {interview_id}"

                        )

                        st.rerun()

            # =================================================

            # =================================================
            # EXISTING INTERVIEWS + MANAGEMENT
            # =================================================
            st.subheader("📋 Scheduled Interviews")

            interviews = get_interviews_for_application(candidate["id"])

            if not interviews:
                st.info("No interview scheduled for this candidate.")

            for interview in interviews:
                interview_id = interview["id"]

                with st.container(border=True):
                    st.markdown(f"### {interview['interview_type']} Interview")
                    st.write(f"**Interview ID:** {interview_id}")
                    st.write(f"**Date:** {interview['interview_date']}")
                    st.write(f"**Time:** {interview['interview_time']}")
                    st.write(f"**Interviewer:** {interview['interviewer']}")
                    st.write(f"**Status:** {interview['status']}")

                    if interview.get("meeting_link"):
                        meeting_url = interview["meeting_link"].strip()
                        if not meeting_url.startswith(("http://", "https://")):
                            meeting_url = "https://" + meeting_url
                        if interview["status"] == "Scheduled":
                            st.link_button("🔗 Join Interview", meeting_url)

                    if interview.get("notes"):
                        st.write(f"**Notes:** {interview['notes']}")

                    if interview["status"] == "Scheduled":
                        with st.expander("✏️ Reschedule Interview"):
                            with st.form(f"reschedule_form_{interview_id}"):
                                try:
                                    current_date = date.fromisoformat(
                                        str(interview["interview_date"])
                                    )
                                except (ValueError, TypeError):
                                    current_date = date.today()
                                selected_date = max(date.today(), current_date)

                                new_date = st.date_input(
                                    "New Interview Date",
                                    value=selected_date,
                                    min_value=date.today(),
                                    key=f"new_date_{interview_id}",
                                )

                                try:
                                    current_time = time.fromisoformat(
                                        str(interview["interview_time"])
                                    )
                                except (ValueError, TypeError):
                                    current_time = time(10, 0)

                                new_time = st.time_input(
                                    "New Interview Time",
                                    value=current_time,
                                    key=f"new_time_{interview_id}",
                                )

                                interview_types = [
                                    "Technical", "HR", "Managerial", "Technical + HR"
                                ]
                                current_type = interview.get("interview_type", "Technical")
                                type_index = (
                                    interview_types.index(current_type)
                                    if current_type in interview_types else 0
                                )
                                new_type = st.selectbox(
                                    "Interview Type",
                                    interview_types,
                                    index=type_index,
                                    key=f"new_type_{interview_id}",
                                )
                                new_interviewer = st.text_input(
                                    "Interviewer",
                                    value=interview.get("interviewer", ""),
                                    key=f"new_interviewer_{interview_id}",
                                )
                                new_link = st.text_input(
                                    "Meeting Link",
                                    value=interview.get("meeting_link", ""),
                                    key=f"new_link_{interview_id}",
                                )
                                new_notes = st.text_area(
                                    "Notes",
                                    value=interview.get("notes", ""),
                                    key=f"new_notes_{interview_id}",
                                )
                                save_reschedule = st.form_submit_button(
                                    "Save New Schedule", type="primary"
                                )

                                if save_reschedule:
                                    if not new_interviewer.strip():
                                        st.error("Please enter the interviewer name.")
                                    else:
                                        try:
                                            result = reschedule_interview(
                                                interview_id=interview_id,
                                                interview_date=str(new_date),
                                                interview_time=new_time.strftime("%H:%M:%S"),
                                                interview_type=new_type,
                                                interviewer=new_interviewer.strip(),
                                                meeting_link=new_link.strip(),
                                                notes=new_notes.strip(),
                                            )
                                            st.success("Interview schedule updated.")
                                            if result["email_sent"]:
                                                st.success("Rescheduling email sent successfully.")
                                            else:
                                                st.warning(
                                                    "Schedule updated, but the email could not be sent. "
                                                    "Check the terminal."
                                                )
                                            st.rerun()
                                        except Exception as exc:
                                            st.error(f"Could not reschedule: {exc}")

                        with st.expander("🛑 Cancel Interview"):
                            st.warning(
                                "Cancellation keeps the interview record in the database "
                                "but changes its status to Cancelled."
                            )
                            confirm_cancel = st.checkbox(
                                "I confirm that I want to cancel this interview.",
                                key=f"confirm_cancel_{interview_id}",
                            )
                            if st.button(
                                "Confirm Cancellation",
                                key=f"cancel_interview_{interview_id}",
                                type="secondary",
                                disabled=not confirm_cancel,
                            ):
                                try:
                                    result = cancel_interview(interview_id)
                                    st.success("Interview cancelled.")
                                    if result["email_sent"]:
                                        st.success("Cancellation email sent successfully.")
                                    else:
                                        st.warning(
                                            "Interview cancelled, but the email could not be sent. "
                                            "Check the terminal."
                                        )
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"Could not cancel interview: {exc}")
                    else:
                        st.caption(
                            "This interview is no longer scheduled, so it cannot be "
                            "rescheduled or cancelled again."
                        )

# ============================================================

# CANDIDATE COMPARISON

# ============================================================

elif page == "Candidate Comparison":

    st.header(

        "📊 Candidate Comparison"

    )

    jobs = get_jobs()

    if not jobs:

        st.info(

            "Create a job first."

        )

        st.stop()

    job_options = {

        f"{job['title']} "

        f"(ID: {job['id']})":

        job["id"]

        for job in jobs

    }

    selected_job_label = st.selectbox(

        "Select Job",

        list(job_options.keys())

    )

    selected_job_id = job_options[

        selected_job_label

    ]

    applications = get_applications_for_job(

        selected_job_id

    )

    if not applications:

        st.info(

            "No candidates available for comparison."

        )

        st.stop()

    candidate_options = {

        f"{candidate['name']} "

        f"(Application #{candidate['application_id']})":

        candidate["application_id"]

        for candidate in applications

    }

    selected_labels = st.multiselect(

        "Select 2–4 Candidates",

        list(candidate_options.keys()),

        max_selections=4

    )

    if len(selected_labels) < 2:

        st.info(

            "Select at least 2 candidates."

        )

    else:

        selected_ids = [

            candidate_options[label]

            for label in selected_labels

        ]

        selected_candidates = [

            get_application(application_id)

            for application_id

            in selected_ids

        ]

        st.subheader(

            "Candidate Comparison"

        )

        comparison = {}

        for candidate in selected_candidates:

            label = (

                f"{candidate['name']} "

                f"(#{candidate['id']})"

            )

            comparison[label] = {

                "Overall Score":

                    candidate[

                        "final_candidate_score"

                    ],

                "Required Skills":

                    candidate[

                        "required_skill_score"

                    ],

                "Preferred Skills":

                    candidate[

                        "preferred_skill_score"

                    ],

                "Experience":

                    candidate[

                        "experience_score"

                    ],

                "Education":

                    candidate[

                        "education_score"

                    ],

                "Evidence":

                    candidate[

                        "evidence_score"

                    ]

            }

        comparison_df = pd.DataFrame(

            comparison

        )

        st.dataframe(

            comparison_df,

            use_container_width=True

        )

        # ====================================================

        # SCORE COMPARISON

        # ====================================================

        st.subheader(

            "Score Comparison"

        )

        chart_data = pd.DataFrame({

            candidate["name"]: {

                "Overall Score":

                    float(

                        candidate[

                            "final_candidate_score"

                        ] or 0

                    ),

                "Required Skills":

                    float(

                        candidate[

                            "required_skill_score"

                        ] or 0

                    ),

                "Experience":

                    float(

                        candidate[

                            "experience_score"

                        ] or 0

                    ),

                "Education":

                    float(

                        candidate[

                            "education_score"

                        ] or 0

                    ),

                "Evidence":

                    float(

                        candidate[

                            "evidence_score"

                        ] or 0

                    )

            }

            for candidate in selected_candidates

        })

        st.bar_chart(

            chart_data

        )

        # ====================================================

        # CANDIDATE SKILLS

        # ====================================================

        st.subheader(

            "Candidate Skills"

        )

        for candidate in selected_candidates:

            st.markdown(

                f"### {candidate['name']}"

            )

            matched = (

                candidate.get(

                    "matched_required_skills"

                )

                or candidate.get(

                    "matched_skills"

                )

                or []

            )

            missing = (

                candidate.get(

                    "missing_required_skills"

                )

                or candidate.get(

                    "missing_skills"

                )

                or []

            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(

                    "**Matched Skills**"

                )

                for skill in matched:

                    st.write(

                        f"✅ {skill}"

                    )

            with col2:

                st.write(

                    "**Missing Skills**"

                )

                for skill in missing:

                    st.write(

                        f"❌ {skill}"

                    )

            st.divider()

# ============================================================
# AGENTIC AI SCREENING
# ============================================================

elif page == "Agentic AI Screening":

    st.header("🤖 Agentic AI Screening")
    st.caption(
        "Run your existing LangChain recruitment agent against candidates "
        "for a selected job. Results are recommendations for recruiter review."
    )

    if screen_candidate_with_agent is None:
        st.error("The recruitment agent could not be imported.")
        st.code(AGENT_IMPORT_ERROR or "Unknown import error")
        st.info(
            "Check backend/recruitment_agent.py and its dependencies, "
            "including LangChain, langchain-google-genai, and GOOGLE_API_KEY."
        )
        st.stop()

    jobs = get_jobs()

    if not jobs:
        st.info("Create a job before running agentic screening.")
        st.stop()

    job_options = {
        f"{job['title']} (ID: {job['id']})": job["id"]
        for job in jobs
    }
    selected_job_label = st.selectbox(
        "Select job to screen candidates for",
        list(job_options.keys()),
        key="agent_screen_job",
    )
    selected_job = get_job(job_options[selected_job_label])

    if not selected_job:
        st.error("Unable to load the selected job.")
        st.stop()

    applications = get_applications_for_job(selected_job["id"])

    if not applications:
        st.info("No candidates have applied for this job yet.")
        st.stop()

    app_options = {
        f"{app.get('name', 'Candidate')} (Application #{app.get('application_id', app.get('id', '?'))})":
            app.get("application_id", app.get("id"))
        for app in applications
    }

    selected_candidate_labels = st.multiselect(
        "Select candidates to evaluate",
        list(app_options.keys()),
        default=list(app_options.keys()),
        key=f"agent_candidates_{selected_job['id']}",
    )

    st.warning(
        "Agent screening may call the configured Gemini API and can take time. "
        "It will not automatically change candidate statuses."
    )

    if st.button(
        "Run Agentic Screening",
        type="primary",
        disabled=not selected_candidate_labels,
        key=f"run_agent_screening_{selected_job['id']}",
    ):
        if not os.getenv("GOOGLE_API_KEY", "").strip():
            st.error("GOOGLE_API_KEY is not configured in this terminal/environment.")
        else:
            results = []
            progress = st.progress(0)
            status_area = st.empty()
            total_selected = len(selected_candidate_labels)

            for index, label in enumerate(selected_candidate_labels, start=1):
                application_id = app_options[label]
                status_area.write(f"Screening {label} ({index}/{total_selected})…")

                try:
                    application = get_application(application_id)
                    if not application:
                        raise ValueError("Application record could not be loaded.")

                    candidate_id = application.get("candidate_id")
                    candidate_profile = (
                        get_candidate(candidate_id) if candidate_id is not None else None
                    )

                    resume_path = (
                        (candidate_profile or {}).get("resume_path")
                        or application.get("resume_path")
                        or application.get("candidate_resume_path")
                    )

                    if not resume_path:
                        raise ValueError(
                            "No resume path was found for this application. "
                            "Check that get_candidate() returns resume_path."
                        )

                    if not os.path.isfile(resume_path):
                        raise FileNotFoundError(
                            f"Resume file does not exist at: {resume_path}"
                        )

                    evaluation = screen_candidate_with_agent(
                        resume_path,
                        selected_job.get("description", ""),
                    )

                    if not isinstance(evaluation, dict):
                        raise ValueError("The agent returned an invalid evaluation.")

                    score_value = evaluation.get(
                        "final_candidate_score",
                        evaluation.get("final_score", evaluation.get("score")),
                    )
                    try:
                        score_value = float(score_value)
                    except (TypeError, ValueError):
                        score_value = None

                    results.append({
                        "Candidate": application.get("name", label),
                        "Application ID": application_id,
                        "Agent Score": score_value,
                        "Status": "Completed",
                        "Evaluation": evaluation,
                    })

                except Exception as error:
                    results.append({
                        "Candidate": label,
                        "Application ID": application_id,
                        "Agent Score": None,
                        "Status": f"Failed: {error}",
                        "Evaluation": None,
                    })

                progress.progress(index / total_selected)

            st.session_state["agent_screening_results"] = results
            st.session_state["agent_screening_job_id"] = selected_job["id"]
            status_area.empty()
            progress.empty()
            st.rerun()

    saved_results = st.session_state.get("agent_screening_results", [])
    saved_job_id = st.session_state.get("agent_screening_job_id")

    if saved_results and saved_job_id == selected_job["id"]:
        st.subheader("Agent Screening Results")

        summary_rows = []
        for result in saved_results:
            summary_rows.append({
                "Candidate": result["Candidate"],
                "Application ID": result["Application ID"],
                "Agent Score": (
                    f"{result['Agent Score']:.2f}%"
                    if result["Agent Score"] is not None
                    else "N/A"
                ),
                "Result": result["Status"],
            })

        st.dataframe(
            pd.DataFrame(summary_rows),
            use_container_width=True,
            hide_index=True,
        )

        def _as_list(value):
            """Normalize list-like evaluation fields for readable display."""
            if value is None:
                return []
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return []
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                    if isinstance(parsed, dict):
                        return [f"{key}: {val}" for key, val in parsed.items()]
                except Exception:
                    pass
                return [part.strip() for part in value.split(",") if part.strip()]
            if isinstance(value, dict):
                return [f"{key}: {val}" for key, val in value.items()]
            if isinstance(value, (list, tuple, set)):
                return list(value)
            return [value]

        def _first_value(data, *keys):
            for key in keys:
                value = data.get(key)
                if value not in (None, "", [], {}):
                    return value
            return None

        def _format_score(value):
            if value is None:
                return "N/A"
            try:
                number = float(value)
                # Evaluation scores are usually percentages; avoid displaying
                # a misleading percentage if the score is already on a 0–1 scale.
                if 0 <= number <= 1:
                    number *= 100
                return f"{number:.1f}%"
            except (TypeError, ValueError):
                return str(value)

        for result in saved_results:
            with st.expander(
                f"{result['Candidate']} — {result['Status']}",
                expanded=(result["Status"] == "Completed"),
            ):
                evaluation = result.get("Evaluation")
                if not isinstance(evaluation, dict):
                    st.error(result["Status"])
                    continue

                # Present the result as a recruiter-friendly summary first.
                score = _first_value(
                    evaluation, "final_candidate_score", "final_score", "score", "overall_score"
                )
                recommendation = _first_value(
                    evaluation, "recommendation", "hiring_recommendation", "candidate_recommendation", "match_level"
                )
                summary = _first_value(
                    evaluation, "summary", "overall_summary", "candidate_summary", "assessment"
                )

                score_col, recommendation_col, app_col = st.columns(3)
                score_col.metric("Overall Match Score", _format_score(score if score is not None else result.get("Agent Score")))
                recommendation_col.metric("Recommendation", str(recommendation or "Recruiter review"))
                app_col.metric("Application ID", str(result.get("Application ID", "N/A")))

                if summary:
                    st.markdown("**Recruiter summary**")
                    st.write(str(summary))
                else:
                    st.caption("Review the evidence and skill breakdown below. The model did not provide a separate summary.")

                matched = _as_list(_first_value(
                    evaluation, "matched_skills", "matching_skills", "skills_matched", "matched_required_skills"
                ))
                missing = _as_list(_first_value(
                    evaluation, "missing_skills", "skills_missing", "missing_required_skills", "gaps"
                ))
                preferred = _as_list(_first_value(
                    evaluation, "preferred_skills", "matched_preferred_skills", "preferred_skills_matched"
                ))

                st.markdown("#### Skills assessment")
                skill_col1, skill_col2 = st.columns(2)
                with skill_col1:
                    st.markdown("**✅ Matched skills**")
                    if matched:
                        for skill in matched:
                            st.markdown(f"- {skill}")
                    else:
                        st.caption("No matched-skills list was provided in the evaluation.")
                with skill_col2:
                    st.markdown("**⚠️ Missing or unverified skills**")
                    if missing:
                        for skill in missing:
                            st.markdown(f"- {skill}")
                    else:
                        st.caption("No missing-skills list was provided in the evaluation.")

                if preferred:
                    st.markdown("**Preferred skills**")
                    st.write(", ".join(str(item) for item in preferred))

                # Display common component scores as metrics when present.
                component_fields = [
                    ("Required skills", ("required_skill_score", "required_skills_score")),
                    ("Preferred skills", ("preferred_skill_score", "preferred_skills_score")),
                    ("Experience", ("experience_score",)),
                    ("Education", ("education_score",)),
                    ("Evidence", ("evidence_score", "skill_evidence_score")),
                ]
                component_values = []
                for label, keys in component_fields:
                    value = _first_value(evaluation, *keys)
                    if value is not None:
                        component_values.append((label, value))
                if component_values:
                    st.markdown("#### Score breakdown")
                    metric_cols = st.columns(min(len(component_values), 5))
                    for index, (label, value) in enumerate(component_values):
                        metric_cols[index % len(metric_cols)].metric(label, _format_score(value))

                evidence = _first_value(
                    evaluation, "evidence", "skill_evidence", "matched_evidence", "evidence_summary", "reasoning"
                )
                if evidence:
                    st.markdown("#### Resume evidence")
                    if isinstance(evidence, (dict, list)):
                        st.write(evidence)
                    else:
                        st.write(str(evidence))

                # Keep raw JSON available for debugging/auditing, but collapsed by default.
                with st.expander("View technical evaluation data (JSON)"):
                    st.json(evaluation)

        st.info(
            "These are AI-assisted recommendations. Review the resume evidence "
            "and evaluation before making a hiring decision. Candidate statuses "
            "have not been changed by this page."
        )

