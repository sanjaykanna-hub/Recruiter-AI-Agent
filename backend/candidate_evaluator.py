# backend/candidate_evaluator.py
from backend.resume_parser import (
    extract_text_from_pdf,
    clean_text,
    extract_candidate_info,
)
from backend.job_parser import parse_job_description
from backend.matcher import match_candidate
from backend.skill_extractor import extract_skills
from backend.experience_extractor import (
    extract_experience,
    calculate_experience_score,
)
from backend.education_extractor import (
    extract_education,
    calculate_education_score,
)
from backend.verified_skill_evidence import (
    build_verified_skill_evidence,
)


def evaluate_candidate(resume_path, job_description):
    """
    Evaluate a candidate resume against a job description.

    Parameters
    ----------
    resume_path : str
        Path to the candidate resume.

    job_description : str
        Job description text.

    Returns
    -------
    dict
        Complete candidate evaluation result.
    """

    # =========================================================
    # 1. EXTRACT RESUME TEXT
    # =========================================================

    resume_text = extract_text_from_pdf(resume_path)

    if not resume_text:
        raise ValueError(
            "Could not extract text from the resume."
        )

    resume_text = clean_text(resume_text)

    # =========================================================
    # 2. EXTRACT CANDIDATE INFORMATION
    # =========================================================

    candidate_info = extract_candidate_info(
        resume_text
    )

    if not isinstance(candidate_info, dict):
        candidate_info = {}

    # =========================================================
    # 3. PARSE JOB DESCRIPTION
    # =========================================================

    job_info = parse_job_description(
        job_description
    )

    if not isinstance(job_info, dict):
        job_info = {}

    required_skills = job_info.get(
        "required_skills",
        []
    )

    preferred_skills = job_info.get(
        "preferred_skills",
        []
    )

    # Make sure skills are lists
    if not isinstance(required_skills, list):
        required_skills = []

    if not isinstance(preferred_skills, list):
        preferred_skills = []

    # =========================================================
    # 4. EXTRACT CANDIDATE SKILLS
    # =========================================================

    candidate_skills = extract_skills(
        resume_text
    )

    if not isinstance(candidate_skills, list):
        candidate_skills = []

    # =========================================================
    # 5. MATCH REQUIRED SKILLS
    # =========================================================

    match_result = match_candidate(
        candidate_skills,
        required_skills
    )

    if not isinstance(match_result, dict):
        match_result = {}

    matched_skills = match_result.get(
        "matched_skills",
        []
    )

    missing_skills = match_result.get(
        "missing_skills",
        []
    )

    required_skill_score = match_result.get(
        "match_percentage",
        0
    )

    # Safety conversion
    try:
        required_skill_score = float(
            required_skill_score
        )
    except (TypeError, ValueError):
        required_skill_score = 0.0

    # =========================================================
    # 6. MATCH PREFERRED SKILLS
    # =========================================================

    candidate_skills_lower = {
        str(skill).strip().lower()
        for skill in candidate_skills
    }

    matched_preferred_skills = []

    for skill in preferred_skills:

        if str(skill).strip().lower() in candidate_skills_lower:
            matched_preferred_skills.append(
                skill
            )

    if len(preferred_skills) > 0:

        preferred_skill_score = (
            len(matched_preferred_skills)
            / len(preferred_skills)
        ) * 100

    else:

        preferred_skill_score = 0

    # =========================================================
    # 7. OVERALL SKILL SCORE
    # =========================================================

    if required_skills and preferred_skills:

        overall_skill_score = (
            required_skill_score * 0.70
            + preferred_skill_score * 0.30
        )

    elif required_skills:

        overall_skill_score = (
            required_skill_score
        )

    elif preferred_skills:

        overall_skill_score = (
            preferred_skill_score
        )

    else:

        overall_skill_score = 0

    # =========================================================
    # 8. EXPERIENCE
    # =========================================================

    experience_result = extract_experience(
        resume_text
    )

    if isinstance(
        experience_result,
        dict
    ):

        experience_years = experience_result.get(
            "experience_years",
            experience_result.get(
                "total_experience",
                0
            )
        )

        experience_score = experience_result.get(
            "experience_score",
            0
        )

    else:

        # Your current extractor may return
        # a numeric value directly.
        experience_years = (
            experience_result
            if experience_result is not None
            else 0
        )

        try:
            experience_years = float(
                experience_years
            )
        except (
            TypeError,
            ValueError
        ):
            experience_years = 0

        # Basic experience scoring
        if experience_years <= 0:

            experience_score = 40

        elif experience_years < 1:

            experience_score = 60

        elif experience_years < 2:

            experience_score = 80

        else:

            experience_score = 100

        experience_result = {
            "experience_years":
                experience_years,

            "experience_score":
                experience_score
        }

    # Convert experience values safely

    try:
        experience_years = float(
            experience_years
        )
    except (
        TypeError,
        ValueError
    ):
        experience_years = 0

    try:
        experience_score = float(
            experience_score
        )
    except (
        TypeError,
        ValueError
    ):
        experience_score = 0

    # =========================================================
    # 9. EDUCATION
    # =========================================================

    education_result = extract_education(
        resume_text
    )

    if isinstance(
        education_result,
        dict
    ):

        education_score = education_result.get(
            "education_score",
            0
        )

    else:

        # Education extractor may return
        # a numeric score directly.
        education_score = (
            education_result
            if education_result is not None
            else 0
        )

        try:
            education_score = float(
                education_score
            )
        except (
            TypeError,
            ValueError
        ):
            education_score = 0

        education_result = {
            "education_score":
                education_score
        }

    try:
        education_score = float(
            education_score
        )
    except (
        TypeError,
        ValueError
    ):
        education_score = 0

    # =========================================================
    # 10. KEYWORD SCORE
    # =========================================================

    keyword_skill_score = (
        required_skill_score
    )

    # =========================================================
    # 11. SEMANTIC / EVIDENCE SCORE
    # =========================================================
    #
    # These values are kept in the result so that your existing
    # database and recruiter UI can continue to work.
    #
    # The current basic evaluator does not calculate semantic
    # evidence independently.
    #

    semantic_evidence_score = (
        required_skill_score
    )

    hybrid_skill_score = (
        overall_skill_score
    )

    # =========================================================
    # 12. FINAL CANDIDATE SCORE
    # =========================================================

    final_score = (
        overall_skill_score * 0.60
        + experience_score * 0.20
        + education_score * 0.20
    )

    # Keep between 0 and 100

    final_score = max(
        0,
        min(
            100,
            round(
                final_score,
                2
            )
        )
    )

    # =========================================================
    # 13. CANDIDATE NAME
    # =========================================================

    candidate_name = candidate_info.get(
        "name",
        candidate_info.get(
            "full_name",
            "Unknown"
        )
    )

    # =========================================================
    # 14. EMAIL
    # =========================================================

    candidate_email = candidate_info.get(
        "email",
        ""
    )

    # =========================================================
    # 15. PHONE
    # =========================================================

    candidate_phone = candidate_info.get(
        "phone",
        candidate_info.get(
            "phone_number",
            ""
        )
    )

    # =========================================================
    # 16. LINKEDIN
    # =========================================================

    linkedin = candidate_info.get(
        "linkedin",
        ""
    )

    # =========================================================
    # 17. GITHUB
    # =========================================================

    github = candidate_info.get(
        "github",
        ""
    )

    # =========================================================
    # 18. LOCATION
    # =========================================================

    location = candidate_info.get(
        "location",
        ""
    )

    # =========================================================
    # 19. FINAL RESULT
    # =========================================================

    result = {

        # -----------------------------------------------------
        # Candidate information
        # -----------------------------------------------------

        "name": candidate_name,

        "email": candidate_email,

        "phone": candidate_phone,

        "linkedin": linkedin,

        "github": github,

        "location": location,

        # -----------------------------------------------------
        # Skills
        # -----------------------------------------------------

        "skills": candidate_skills,

        "required_skills": required_skills,

        "preferred_skills": preferred_skills,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "matched_required_skills":
            matched_skills,

        "missing_required_skills":
            missing_skills,

        "matched_preferred_skills":
            matched_preferred_skills,

        # -----------------------------------------------------
        # Skill scores
        # -----------------------------------------------------

        "required_skill_score":
            round(
                required_skill_score,
                2
            ),

        "preferred_skill_score":
            round(
                preferred_skill_score,
                2
            ),

        "overall_skill_score":
            round(
                overall_skill_score,
                2
            ),

        "keyword_skill_score":
            round(
                keyword_skill_score,
                2
            ),

        # -----------------------------------------------------
        # Evidence / hybrid scores
        # -----------------------------------------------------

        "semantic_evidence_score":
            round(
                semantic_evidence_score,
                2
            ),

        "hybrid_skill_score":
            round(
                hybrid_skill_score,
                2
            ),

        "evidence": [],

        # -----------------------------------------------------
        # Experience
        # -----------------------------------------------------

        "experience":
            experience_years,

        "experience_years":
            experience_years,

        "experience_score":
            round(
                experience_score,
                2
            ),

        "experience_details":
            experience_result,

        # -----------------------------------------------------
        # Education
        # -----------------------------------------------------

        "education_score":
            round(
                education_score,
                2
            ),

        "education_details":
            education_result,

        # -----------------------------------------------------
        # Final score
        # -----------------------------------------------------

        "final_score":
            final_score,

        # -----------------------------------------------------
        # Additional information
        # -----------------------------------------------------

        "candidate_info":
            candidate_info,

        "job_info":
            job_info,

        "resume_text":
            resume_text
    }

    return result


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    print(
        "candidate_evaluator.py loaded successfully."
    )

    print(
        "evaluate_candidate function is available."
    )