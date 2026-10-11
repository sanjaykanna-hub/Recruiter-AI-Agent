import streamlit as st

import pandas as pd

import json

import re



from datetime import date, time



from backend.database import (

    get_jobs,

    create_job,

    get_job,

    update_job_criteria,

    get_applications_for_job,

    get_application,

    update_application_status,

    create_interview,

    get_interviews_for_application

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

        "Candidate Comparison"

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
        "LinkedIn": r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s\"'<>]+",
        "GitHub": r"(?:https?://)?(?:www\.)?github\.com/[^\s\"'<>]+",
    }
    for label, pattern in patterns.items():
        if label not in links:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = make_clickable_url(match.group(0).rstrip(".,);]}"))
                if url:
                    links[label] = url
    urls = re.findall(r"https?://[^\s\"'<>]+", text, re.IGNORECASE)
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

            use_container_width=True,

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

            # EXISTING INTERVIEWS

            # =================================================



            st.subheader(

                "📋 Scheduled Interviews"

            )



            interviews = get_interviews_for_application(

                candidate["id"]

            )



            if not interviews:



                st.info(

                    "No interview scheduled for this candidate."

                )



            else:



                for interview in interviews:



                    with st.container():



                        st.markdown(

                            f"""

                            ### {interview['interview_type']} Interview



                            **Date:** {interview['interview_date']}



                            **Time:** {interview['interview_time']}



                            **Interviewer:** {interview['interviewer']}



                            **Status:** {interview['status']}

                            """

                        )



                        if interview[

                            "meeting_link"

                        ]:



                            meeting_url = (

                                interview[

                                    "meeting_link"

                                ]

                            )



                            if not meeting_url.startswith(

                                (

                                    "http://",

                                    "https://"

                                )

                            ):



                                meeting_url = (

                                    "https://"

                                    + meeting_url

                                )



                            st.link_button(

                                "🔗 Join Interview",

                                meeting_url

                            )



                        if interview["notes"]:



                            st.write(

                                f"**Notes:** "

                                f"{interview['notes']}"

                            )



                        st.divider()





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