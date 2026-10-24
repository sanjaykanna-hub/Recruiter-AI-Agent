import streamlit as st
import os
import json
from datetime import datetime

from backend.database import (
    init_database,
    create_candidate_account,
    authenticate_candidate,
    change_candidate_password,
    reset_candidate_password,
    get_candidate_security_question,
    get_candidate,
    update_candidate_resume,
    get_jobs,
    create_application,
    get_candidate_applications,
    get_candidate_notifications,
    mark_notification_read,
    save_feedback,
    get_interviews_for_application,
    save_evaluation,
)

from backend.candidate_evaluator import evaluate_candidate


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Recruiter AI - Candidate Portal",
    page_icon="💼",
    layout="wide"
)

init_database()

RESUME_DIR = os.path.join("data", "resumes")
os.makedirs(RESUME_DIR, exist_ok=True)


# ============================================================
# SESSION STATE
# ============================================================

if "candidate_logged_in" not in st.session_state:
    st.session_state.candidate_logged_in = False

if "candidate_user" not in st.session_state:
    st.session_state.candidate_user = None

if "candidate_page" not in st.session_state:
    st.session_state.candidate_page = "Dashboard"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_json(value):
    if value is None:
        return {}

    if isinstance(value, (dict, list)):
        return value

    try:
        return json.loads(value)
    except Exception:
        return {}


def normalize_skill_list(value):
    if not value:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):

        parsed = safe_json(value)

        if isinstance(parsed, list):
            return parsed

        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return []


def get_application_score(application):
    score = application.get("final_score")

    if score is None:
        score = application.get("overall_score", 0)

    try:
        return float(score or 0)
    except Exception:
        return 0.0


# ============================================================
# AI IMPROVEMENT SUGGESTIONS
# ============================================================

def generate_improvement_suggestions(application):

    suggestions = []

    matched_skills = normalize_skill_list(
        application.get("matched_skills")
    )

    missing_skills = normalize_skill_list(
        application.get("missing_skills")
    )

    required_score = float(
        application.get("required_skill_score") or 0
    )

    experience_score = float(
        application.get("experience_score") or 0
    )

    education_score = float(
        application.get("education_score") or 0
    )

    # Missing skills
    if missing_skills:

        suggestions.append({
            "priority": "High",
            "title": "Improve missing skills",
            "message": (
                "The following skills were not detected strongly "
                "enough in your resume: "
                + ", ".join(map(str, missing_skills))
                + "."
            )
        })

    # Required skills
    if required_score < 70:

        suggestions.append({
            "priority": "High",
            "title": "Increase your required skill match",
            "message": (
                "Your required-skill score is below 70%. "
                "Add relevant projects, internships, certifications "
                "or practical experience that demonstrate the required skills."
            )
        })

    # Experience
    if experience_score < 60:

        suggestions.append({
            "priority": "Medium",
            "title": "Strengthen your experience section",
            "message": (
                "Add internships, academic projects, freelance work "
                "or professional experience. Explain your role, "
                "technologies used and the result of your work."
            )
        })

    # Education
    if education_score < 60:

        suggestions.append({
            "priority": "Medium",
            "title": "Improve education details",
            "message": (
                "Clearly mention your degree, specialization, "
                "university and graduation details."
            )
        })

    # Evidence
    if not matched_skills:

        suggestions.append({
            "priority": "Medium",
            "title": "Add stronger skill evidence",
            "message": (
                "Instead of only listing skills, provide projects "
                "or experience that demonstrate how you used them."
            )
        })

    # Good profile
    if not suggestions:

        suggestions.append({
            "priority": "Low",
            "title": "Keep improving",
            "message": (
                "Your profile currently has a good match. "
                "Continue adding projects, certifications and "
                "measurable achievements."
            )
        })

    return suggestions


# ============================================================
# JOB RECOMMENDATIONS
# ============================================================

def get_recommended_jobs(candidate_id):

    applications = get_candidate_applications(
        candidate_id
    )

    applied_job_ids = {
        application["job_id"]
        for application in applications
    }

    jobs = get_jobs(active_only=True)

    candidate_skills = set()

    for application in applications:

        matched = normalize_skill_list(
            application.get("matched_skills")
        )

        for skill in matched:

            candidate_skills.add(
                str(skill).lower().strip()
            )

    recommendations = []

    for job in jobs:

        if job["job_id"] in applied_job_ids:
            continue

        required = normalize_skill_list(
            job.get("required_skills")
        )

        preferred = normalize_skill_list(
            job.get("preferred_skills")
        )

        all_skills = required + preferred

        if not all_skills:
            continue

        matches = []

        for skill in all_skills:

            if str(skill).lower().strip() in candidate_skills:
                matches.append(skill)

        score = (
            len(matches) / len(all_skills) * 100
            if all_skills
            else 0
        )

        recommendations.append({
            "job": job,
            "score": score,
            "matches": matches
        })

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations[:5]


# ============================================================
# FEEDBACK EMAIL
# ============================================================

def send_feedback_email(
    candidate_name,
    candidate_email,
    category,
    message
):

    api_key = os.getenv("RESEND_API_KEY")

    if not api_key:

        return (
            False,
            "Feedback saved. Email service is not configured yet."
        )

    try:

        import requests

        payload = {
            "from": "Recruiter AI <onboarding@resend.dev>",
            "to": [
                "sanjay27.8.2006@gmail.com"
            ],
            "subject": (
                f"Recruiter AI Feedback - {category}"
            ),
            "html": f"""
                <h2>Recruiter AI Feedback</h2>

                <p>
                    <strong>Candidate:</strong>
                    {candidate_name}
                </p>

                <p>
                    <strong>Email:</strong>
                    {candidate_email}
                </p>

                <p>
                    <strong>Category:</strong>
                    {category}
                </p>

                <hr>

                <p>{message}</p>
            """
        }

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=15
        )

        if response.status_code in [200, 201]:

            return (
                True,
                "Feedback sent successfully."
            )

        return (
            False,
            "Feedback was saved, but email delivery failed."
        )

    except Exception:

        return (
            False,
            "Feedback was saved, but email delivery failed."
        )


# ============================================================
# LOGIN / REGISTER
# ============================================================

def show_login_page():

    st.markdown(
               """
        <div style="text-align: center; padding: 40px 0 20px 0;">
            <h1>💼 Recruiter AI</h1>
            <p style="font-size: 18px;">Candidate Portal</p>
            <p>
                Apply for jobs, track your applications
                and get AI career guidance.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    login_tab, register_tab, forgot_tab = st.tabs([
        "Login",
        "Create Account",
        "Forgot Password"
    ])

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader("Candidate Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if not email or not password:

                st.warning(
                    "Please enter your email and password."
                )

            else:

                user = authenticate_candidate(
                    email,
                    password
                )

                if user:

                    st.session_state.candidate_logged_in = True

                    st.session_state.candidate_user = user

                    st.session_state.candidate_page = "Dashboard"

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

    # ========================================================
    # REGISTER
    # ========================================================

    with register_tab:

        st.subheader("Create Candidate Account")

        name = st.text_input(
            "Full Name",
            key="register_name"
        )

        email = st.text_input(
            "Email Address",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm_password"
        )

        security_questions = [
            "What was the name of your first school?",
            "What city were you born in?",
            "What was the name of your first pet?",
            "What is the first name of your oldest cousin?",
        ]
        security_question = st.selectbox(
            "Choose a security question",
            security_questions,
            key="register_security_question",
        )
        security_answer = st.text_input(
            "Your answer (remember it exactly)",
            key="register_security_answer",
            help="Your answer is stored as a hash and is used to verify password resets.",
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not name or not email or not password or not security_answer.strip():

                st.warning(
                    "Please fill in all fields, including your security answer."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            else:

                candidate_id = create_candidate_account(
                    name.strip(),
                    email.strip().lower(),
                    password,
                    security_question,
                    security_answer,
                )

                if candidate_id:

                    st.success(
                        "Account created successfully. "
                        "You can now login."
                    )

                else:

                    st.error(
                        "An account with this email already exists."
                    )


    # ========================================================
    # FORGOT PASSWORD - SECURITY QUESTION RESET
    # ========================================================

    with forgot_tab:
        st.subheader("Reset your password")
        st.write(
            "Enter your account email and answer the security question you selected when creating your account."
        )

        reset_email = st.text_input(
            "Account email",
            key="forgot_password_email",
        ).strip().lower()

        if st.button(
            "Find my security question",
            key="load_security_question",
            use_container_width=True,
        ):
            if not reset_email or "@" not in reset_email:
                st.warning("Enter a valid email address.")
                st.session_state.pop("password_reset_question", None)
                st.session_state.pop("password_reset_email", None)
            else:
                question = get_candidate_security_question(reset_email)
                if question:
                    st.session_state["password_reset_email"] = reset_email
                    st.session_state["password_reset_question"] = question
                    st.success("Security question found. Answer it to continue.")
                else:
                    st.error(
                        "No security question is set for this account. Existing accounts may need to be updated or recreated with the new registration form."
                    )
                    st.session_state.pop("password_reset_question", None)
                    st.session_state.pop("password_reset_email", None)

        if st.session_state.get("password_reset_question") and st.session_state.get("password_reset_email") == reset_email:
            st.info(f"**Security question:** {st.session_state['password_reset_question']}")
            with st.form("security_question_reset_form"):
                security_answer = st.text_input("Your answer", key="forgot_security_answer")
                new_reset_password = st.text_input("New password", type="password", key="forgot_new_password")
                confirm_reset_password = st.text_input("Confirm new password", type="password", key="forgot_confirm_new_password")
                reset_submitted = st.form_submit_button("Verify answer and reset password", use_container_width=True)

            if reset_submitted:
                if not security_answer.strip() or not new_reset_password or not confirm_reset_password:
                    st.warning("Please complete all fields.")
                elif len(new_reset_password) < 6:
                    st.warning("Password must contain at least 6 characters.")
                elif new_reset_password != confirm_reset_password:
                    st.error("The passwords do not match.")
                else:
                    try:
                        reset_ok = reset_candidate_password(
                            st.session_state["password_reset_email"],
                            security_answer,
                            new_reset_password,
                        )
                        if reset_ok:
                            st.success("Password reset successfully. Return to Login and sign in with your new password.")
                            for key in ("password_reset_email", "password_reset_question", "forgot_security_answer", "forgot_new_password", "forgot_confirm_new_password"):
                                st.session_state.pop(key, None)
                        else:
                            st.error("The security answer is incorrect, or this account has no saved security answer. Your password was not changed.")
                    except Exception as error:
                        st.error("Password reset failed. Please try again.")
                        st.exception(error)


# ============================================================
# SIDEBAR
# ============================================================

def show_sidebar():

    user = st.session_state.candidate_user

    with st.sidebar:

        st.title("Recruiter AI")

        st.caption(
            f"Welcome, {user['name']}"
        )

        st.divider()

        pages = [
            "Dashboard",
            "Find Jobs",
            "My Applications",
            "Notifications",
            "AI Improvement",
            "Recommended Jobs",
            "Feedback",
            "Change Password"
        ]

        for page in pages:

            if st.button(
                page,
                use_container_width=True
            ):

                st.session_state.candidate_page = page

                st.rerun()

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.candidate_logged_in = False

            st.session_state.candidate_user = None

            st.session_state.candidate_page = "Dashboard"

            st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    user = st.session_state.candidate_user

    candidate_id = user["candidate_id"]

    applications = get_candidate_applications(
        candidate_id
    )

    notifications = get_candidate_notifications(
        candidate_id
    )

    unread_notifications = [
        notification
        for notification in notifications
        if not notification["is_read"]
    ]

    st.title("Candidate Dashboard")

    st.write(
        f"Welcome back, **{user['name']}** 👋"
    )

    # ========================================================
    # METRICS
    # ========================================================

    total_applications = len(applications)

    shortlisted = len([
        application
        for application in applications
        if application["status"].lower() == "shortlisted"
    ])

    interviews = len([
        application
        for application in applications
        if "interview" in application["status"].lower()
    ])

    rejected = len([
        application
        for application in applications
        if application["status"].lower() == "rejected"
    ])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Applications",
        total_applications
    )

    col2.metric(
        "Shortlisted",
        shortlisted
    )

    col3.metric(
        "Interviews",
        interviews
    )

    col4.metric(
        "Rejected",
        rejected
    )

    st.divider()

    # ========================================================
    # LATEST NOTIFICATION
    # ========================================================

    if unread_notifications:

        st.subheader("🔔 Latest Notification")

        notification = unread_notifications[0]

        st.info(
            f"**{notification['title']}**\n\n"
            f"{notification['message']}"
        )

    # ========================================================
    # APPLICATIONS
    # ========================================================

    st.subheader("Recent Applications")

    if not applications:

        st.info(
            "You haven't applied for any jobs yet."
        )

        if st.button("Find Jobs"):

            st.session_state.candidate_page = "Find Jobs"

            st.rerun()

        return

    for application in applications[:5]:

        score = get_application_score(
            application
        )

        with st.container(border=True):

            col1, col2, col3 = st.columns([
                2,
                1,
                1
            ])

            with col1:

                st.subheader(
                    application["job_title"]
                )

                st.caption(
                    "Applied: "
                    + application["created_at"][:10]
                )

            with col2:

                st.metric(
                    "AI Match",
                    f"{score:.1f}%"
                )

            with col3:

                st.write("**Status**")

                status = application["status"]

                if status.lower() == "shortlisted":

                    st.success(status)

                elif status.lower() == "rejected":

                    st.error(status)

                else:

                    st.info(status)


# ============================================================
# FIND JOBS
# ============================================================

def show_find_jobs():

    user = st.session_state.candidate_user

    candidate_id = user["candidate_id"]

    st.title("Find Jobs")

    st.write(
        "Find active jobs and apply using your resume."
    )

    # ========================================================
    # RESUME
    # ========================================================

    candidate = get_candidate(
        candidate_id
    )

    if not candidate:

        st.error(
            "Candidate profile could not be found."
        )

        return

    if not candidate["resume_path"]:

        st.warning(
            "Please upload your resume before applying."
        )

        uploaded_resume = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx"]
        )

        if uploaded_resume:

            extension = os.path.splitext(
                uploaded_resume.name
            )[1]

            filename = (
                f"{candidate_id}_"
                f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
                f"{extension}"
            )

            resume_path = os.path.join(
                RESUME_DIR,
                filename
            )

            with open(
                resume_path,
                "wb"
            ) as file:

                file.write(
                    uploaded_resume.getbuffer()
                )

            update_candidate_resume(
                candidate_id,
                uploaded_resume.name,
                resume_path
            )

            st.success(
                "Resume uploaded successfully."
            )

            st.rerun()

    else:

        st.success(
            f"Resume uploaded: "
            f"{candidate['resume_filename']}"
        )

    st.divider()

    # ========================================================
    # JOBS
    # ========================================================

    jobs = get_jobs(
        active_only=True
    )

    if not jobs:

        st.info(
            "There are currently no active jobs."
        )

        return

    applications = get_candidate_applications(
        candidate_id
    )

    applied_job_ids = {
        application["job_id"]
        for application in applications
    }

    for job in jobs:

        with st.container(border=True):

            col1, col2 = st.columns([
                4,
                1
            ])

            with col1:

                st.subheader(
                    job["title"]
                )

                description = job.get(
                    "description",
                    ""
                )

                if description:

                    st.write(
                        description[:600]
                    )

                required_skills = normalize_skill_list(
                    job.get("required_skills")
                )

                preferred_skills = normalize_skill_list(
                    job.get("preferred_skills")
                )

                if required_skills:

                    st.write(
                        "**Required Skills:** "
                        + ", ".join(
                            map(str, required_skills)
                        )
                    )

                if preferred_skills:

                    st.caption(
                        "Preferred: "
                        + ", ".join(
                            map(str, preferred_skills)
                        )
                    )

                st.caption(
                    f"Minimum AI score: "
                    f"{job.get('minimum_score', 70)}%"
                )

            with col2:

                if job["job_id"] in applied_job_ids:

                    st.success(
                        "Applied"
                    )

                else:

                    if st.button(
                        "Apply",
                        key=f"apply_{job['job_id']}",
                        use_container_width=True
                    ):

                        if not candidate["resume_path"]:

                            st.error(
                                "Please upload your resume first."
                            )

                            continue

                        # ------------------------------------
                        # AI EVALUATION
                        # ------------------------------------

                        with st.spinner(
                            "AI is screening your resume..."
                        ):

                            try:

                                result = evaluate_candidate(
                                    candidate["resume_path"],
                                    job["description"]
                                )

                            except Exception as error:

                                st.error(
                                    "AI evaluation failed."
                                )

                                st.exception(error)

                                continue

                        score = float(
                            result.get(
                                "final_score",
                                0
                            ) or 0
                        )

                        minimum_score = float(
                            job.get(
                                "minimum_score",
                                70
                            ) or 70
                        )

                        if score >= minimum_score:

                            application_status = "Shortlisted"

                        else:

                            application_status = "Under Review"

                        # ------------------------------------
                        # CREATE APPLICATION
                        # ------------------------------------

                        application_id = create_application(
                            job_id=job["job_id"],
                            candidate_id=candidate_id,
                            status=application_status,
                            overall_score=score
                        )

                        # ------------------------------------
                        # SAVE AI EVALUATION
                        # ------------------------------------

                        try:

                            save_evaluation(
                                application_id,
                                result
                            )

                        except Exception as error:

                            st.warning(
                                "Application submitted, "
                                "but evaluation data could not "
                                "be saved."
                            )

                            st.exception(error)

                        st.success(
                            "Application submitted successfully!"
                        )

                        if application_status == "Shortlisted":

                            st.balloons()

                            st.success(
                                "🎉 Congratulations! "
                                "You have been shortlisted."
                            )

                        st.rerun()


# ============================================================
# MY APPLICATIONS
# ============================================================

def show_my_applications():

    user = st.session_state.candidate_user

    applications = get_candidate_applications(
        user["candidate_id"]
    )

    st.title("My Applications")

    if not applications:

        st.info(
            "You haven't submitted any applications yet."
        )

        return

    for application in applications:

        score = get_application_score(
            application
        )

        status = application["status"]

        with st.expander(
            f"{application['job_title']} "
            f"— {status}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "AI Match",
                    f"{score:.1f}%"
                )

            with col2:

                required_score = float(
                    application.get(
                        "required_skill_score",
                        0
                    ) or 0
                )

                st.metric(
                    "Required Skills",
                    f"{required_score:.1f}%"
                )

            with col3:

                st.write("**Application Status**")

                if status.lower() == "shortlisted":

                    st.success(status)

                elif status.lower() == "rejected":

                    st.error(status)

                else:

                    st.info(status)

            st.write(
                f"Applied on: "
                f"{application['created_at'][:10]}"
            )

            # =================================================
            # MATCHED SKILLS
            # =================================================

            matched_skills = normalize_skill_list(
                application.get("matched_skills")
            )

            if matched_skills:

                st.write("### Matched Skills")

                st.success(
                    ", ".join(
                        map(str, matched_skills)
                    )
                )

            # =================================================
            # MISSING SKILLS
            # =================================================

            missing_skills = normalize_skill_list(
                application.get("missing_skills")
            )

            if missing_skills:

                st.write("### Skills to Improve")

                st.warning(
                    ", ".join(
                        map(str, missing_skills)
                    )
                )

            # =================================================
            # INTERVIEW
            # =================================================

            interviews = get_interviews_for_application(
                application["application_id"]
            )

            if interviews:

                st.divider()

                st.subheader(
                    "📅 Interview"
                )

                for interview in interviews:

                    st.info(
                        f"**Date:** "
                        f"{interview['interview_date']}\n\n"
                        f"**Time:** "
                        f"{interview['interview_time']}\n\n"
                        f"**Type:** "
                        f"{interview['interview_type']}\n\n"
                        f"**Interviewer:** "
                        f"{interview['interviewer']}"
                    )

                    if interview.get("meeting_link"):

                        st.link_button(
                            "Join Interview",
                            interview["meeting_link"]
                        )


# ============================================================
# NOTIFICATIONS
# ============================================================

def show_notifications():

    user = st.session_state.candidate_user

    notifications = get_candidate_notifications(
        user["candidate_id"]
    )

    st.title("🔔 Notifications")

    if not notifications:

        st.info(
            "You don't have any notifications yet."
        )

        return

    for notification in notifications:

        if notification["is_read"]:

            with st.container(border=True):

                st.write(
                    f"**{notification['title']}**"
                )

                st.write(
                    notification["message"]
                )

                st.caption(
                    notification["created_at"]
                )

        else:

            with st.container(border=True):

                st.subheader(
                    notification["title"]
                )

                st.write(
                    notification["message"]
                )

                st.caption(
                    notification["created_at"]
                )

                if st.button(
                    "Mark as read",
                    key=(
                        f"read_"
                        f"{notification['notification_id']}"
                    )
                ):

                    mark_notification_read(
                        notification["notification_id"]
                    )

                    st.rerun()


# ============================================================
# AI IMPROVEMENT
# ============================================================

def show_ai_improvement():

    user = st.session_state.candidate_user

    applications = get_candidate_applications(
        user["candidate_id"]
    )

    st.title("🧠 AI Career Improvement")

    st.write(
        "Get AI-based suggestions based on your "
        "actual application results."
    )

    if not applications:

        st.info(
            "Apply for a job first so the AI can "
            "analyse your profile."
        )

        return

    selected_application = st.selectbox(
        "Select a job",
        applications,
        format_func=lambda application:
            application["job_title"]
    )

    score = get_application_score(
        selected_application
    )

    st.metric(
        "Current AI Match",
        f"{score:.1f}%"
    )

    st.divider()

    st.subheader(
        "AI Suggestions"
    )

    suggestions = generate_improvement_suggestions(
        selected_application
    )

    for suggestion in suggestions:

        priority = suggestion["priority"]

        if priority == "High":

            st.error(
                f"🔴 **{suggestion['title']}**\n\n"
                f"{suggestion['message']}"
            )

        elif priority == "Medium":

            st.warning(
                f"🟡 **{suggestion['title']}**\n\n"
                f"{suggestion['message']}"
            )

        else:

            st.success(
                f"🟢 **{suggestion['title']}**\n\n"
                f"{suggestion['message']}"
            )


# ============================================================
# RECOMMENDED JOBS
# ============================================================

def show_recommended_jobs():

    user = st.session_state.candidate_user

    st.subheader(
        "💼 Recommended Jobs"
    )

    recommendations = get_recommended_jobs(
        user["candidate_id"]
    )

    if not recommendations:

        st.info(
            "No additional job recommendations available yet."
        )

        return

    for recommendation in recommendations:

        job = recommendation["job"]

        score = recommendation["score"]

        matches = recommendation["matches"]

        with st.container(border=True):

            col1, col2 = st.columns([
                3,
                1
            ])

            with col1:

                st.write(
                    f"### {job['title']}"
                )

                if matches:

                    st.write(
                        "Matching skills: "
                        + ", ".join(
                            map(str, matches)
                        )
                    )

            with col2:

                st.metric(
                    "AI Match",
                    f"{score:.0f}%"
                )


# ============================================================
# FEEDBACK
# ============================================================

def show_feedback():

    user = st.session_state.candidate_user

    st.title("💬 Feedback")

    st.write(
        "We would love to hear your feedback "
        "about the Recruiter AI portal."
    )

    category = st.selectbox(
        "Feedback Type",
        [
            "General Feedback",
            "Bug Report",
            "Suggestion",
            "Application Issue",
            "Other"
        ]
    )

    message = st.text_area(
        "Your Feedback",
        height=180,
        placeholder=(
            "Tell us what you think..."
        )
    )

    if st.button(
        "Submit Feedback",
        use_container_width=True
    ):

        if not message.strip():

            st.warning(
                "Please enter your feedback."
            )

            return

        # --------------------------------------------
        # SAVE TO DATABASE
        # --------------------------------------------

        save_feedback(
            candidate_id=user["candidate_id"],
            candidate_email=user["email"],
            category=category,
            message=message.strip()
        )

        # --------------------------------------------
        # SEND EMAIL
        # --------------------------------------------

        sent, email_message = send_feedback_email(
            candidate_name=user["name"],
            candidate_email=user["email"],
            category=category,
            message=message.strip()
        )

        if sent:

            st.success(
                "Thank you! Your feedback has been sent successfully."
            )

        else:

            st.success(
                "Thank you! Your feedback has been saved."
            )

            st.info(
                email_message
            )


# ============================================================
# CHANGE PASSWORD
# ============================================================

def show_change_password():

    user = st.session_state.candidate_user

    st.title("🔐 Change Password")
    st.write("Update the password for your candidate account.")

    with st.form("change_password_form"):
        current_password = st.text_input(
            "Current Password",
            type="password",
            key="change_current_password",
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            key="change_new_password",
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            key="change_confirm_password",
        )

        submitted = st.form_submit_button(
            "Update Password",
            use_container_width=True,
        )

    if not submitted:
        return

    if not current_password or not new_password or not confirm_password:
        st.warning("Please fill in all password fields.")
        return

    if len(new_password) < 6:
        st.warning("Your new password must contain at least 6 characters.")
        return

    if new_password != confirm_password:
        st.error("The new passwords do not match.")
        return

    if current_password == new_password:
        st.warning("Choose a password different from your current password.")
        return

    try:
        changed = change_candidate_password(
            user["email"],
            current_password,
            new_password,
        )

        if changed:
            st.success("Your password has been changed successfully.")
            st.info("Use your new password the next time you log in.")
        else:
            st.error("Your current password is incorrect.")

    except Exception as error:
        st.error("Could not update your password. Please try again.")
        st.exception(error)


# ============================================================
# MAIN APPLICATION
# ============================================================

if not st.session_state.candidate_logged_in:

    show_login_page()

else:

    show_sidebar()

    page = st.session_state.candidate_page

    if page == "Dashboard":

        show_dashboard()

    elif page == "Find Jobs":

        show_find_jobs()

    elif page == "My Applications":

        show_my_applications()

    elif page == "Notifications":

        show_notifications()

    elif page == "AI Improvement":

        show_ai_improvement()

        st.divider()

        show_recommended_jobs()

    elif page == "Recommended Jobs":

        show_recommended_jobs()

    elif page == "Feedback":

        show_feedback()

    elif page == "Change Password":

        show_change_password()