from resume_parser import (
    extract_text_from_pdf,
    clean_text,
    extract_candidate_info
)

from skill_extractor import extract_skills

from job_parser import parse_job_description

from matcher import match_candidate

from experience_extractor import (
    extract_experience,
    calculate_experience_score
)

from education_extractor import (
    extract_education,
    calculate_education_score
)

from scorer import calculate_candidate_score

from verified_skill_evidence import (
    build_verified_skill_evidence
)

from advanced_skill_scorer import (
    calculate_skill_scores
)


def calculate_verified_evidence_score(
    verified_evidence,
    required_skills
):
    """
    Calculate evidence score using only
    verified required skills.
    """

    if not required_skills:
        return 0.0

    verified_count = 0

    semantic_scores = []

    for item in verified_evidence:

        if item["verified"]:

            verified_count += 1

            if item["evidence"]:

                semantic_scores.append(
                    item["evidence"]["score"]
                )

    # --------------------------------
    # Verified skill coverage
    # --------------------------------

    coverage_score = (
        verified_count
        / len(required_skills)
    ) * 100

    # --------------------------------
    # Semantic evidence quality
    # --------------------------------

    if semantic_scores:

        semantic_score = (
            sum(semantic_scores)
            / len(semantic_scores)
        )

    else:

        semantic_score = 0.0

    # --------------------------------
    # Combined evidence score
    # --------------------------------

    score = (
        (coverage_score * 0.70)
        +
        (semantic_score * 0.30)
    )

    return round(
        min(score, 100),
        2
    )


def calculate_hybrid_skill_score(
    overall_skill_score,
    evidence_score
):
    """
    Combine skill matching and verified
    RAG evidence.
    """

    score = (
        (overall_skill_score * 0.70)
        +
        (evidence_score * 0.30)
    )

    return round(
        min(score, 100),
        2
    )


def evaluate_candidate(
    resume_path,
    job_description
):

    # =================================
    # Resume
    # =================================

    raw_text = extract_text_from_pdf(
        resume_path
    )

    cleaned_text = clean_text(
        raw_text
    )

    # =================================
    # Candidate information
    # =================================

    candidate_info = extract_candidate_info(
        cleaned_text
    )

    # =================================
    # Candidate skills
    # =================================

    candidate_skills = extract_skills(
        cleaned_text
    )

    # =================================
    # Job requirements
    # =================================

    job = parse_job_description(
        job_description
    )

    required_skills = job[
        "required_skills"
    ]

    preferred_skills = job[
        "preferred_skills"
    ]

    # =================================
    # Advanced skill scoring
    # =================================

    skill_scores = calculate_skill_scores(
        candidate_skills,
        required_skills,
        preferred_skills
    )

    required_skill_score = (
        skill_scores["required_score"]
    )

    preferred_skill_score = (
        skill_scores["preferred_score"]
    )

    overall_skill_score = (
        skill_scores["overall_score"]
    )

    # =================================
    # Keyword baseline
    # =================================

    match_result = match_candidate(
        candidate_skills,
        required_skills
    )

    keyword_skill_score = (
        match_result["match_percentage"]
    )

    # =================================
    # VERIFIED RAG EVIDENCE
    # =================================

    verified_evidence = (
        build_verified_skill_evidence(
            cleaned_text,
            required_skills
        )
    )

    # =================================
    # Evidence score
    # =================================

    evidence_score = (
        calculate_verified_evidence_score(
            verified_evidence,
            required_skills
        )
    )

    # =================================
    # Hybrid skill score
    # =================================

    hybrid_skill_score = (
        calculate_hybrid_skill_score(
            overall_skill_score,
            evidence_score
        )
    )

    # =================================
    # Experience
    # =================================

    experience = extract_experience(
        cleaned_text
    )

    experience_score = (
        calculate_experience_score(
            experience
        )
    )

    # =================================
    # Education
    # =================================

    education = extract_education(
        cleaned_text
    )

    education_score = (
        calculate_education_score(
            education
        )
    )

    # =================================
    # Final score
    # =================================

    final_score = calculate_candidate_score(
        hybrid_skill_score,
        experience_score,
        education_score
    )

    # =================================
    # Return
    # =================================

    return {

        "name":
            candidate_info["name"],

        "email":
            candidate_info["email"],

        "phone":
            candidate_info["phone"],

        "linkedin":
            candidate_info["linkedin"],

        "location":
            candidate_info["location"],

        "skills":
            candidate_skills,

        "required_skills":
            required_skills,

        "preferred_skills":
            preferred_skills,

        "matched_skills":
            match_result["matched_skills"],

        "missing_skills":
            match_result["missing_skills"],

        "matched_required":
            skill_scores["matched_required"],

        "matched_preferred":
            skill_scores["matched_preferred"],

        "required_skill_score":
            required_skill_score,

        "preferred_skill_score":
            preferred_skill_score,

        "overall_skill_score":
            overall_skill_score,

        "keyword_skill_score":
            keyword_skill_score,

        "semantic_evidence_score":
            evidence_score,

        "hybrid_skill_score":
            hybrid_skill_score,

        "experience":
            experience,

        "experience_score":
            experience_score,

        "education_score":
            education_score,

        "evidence":
            verified_evidence,

        "final_score":
            final_score
    }


if __name__ == "__main__":

    resume_path = (
        "data/resumes/sample_resume.pdf"
    )

    job_description = """
    Python Developer with experience in
    JavaScript, React, MongoDB, Git and
    Data Analysis.

    Knowledge of HTML, CSS, SQL, APIs
    and database technologies is preferred.

    Experience with machine learning
    is an advantage.
    """

    result = evaluate_candidate(
        resume_path,
        job_description
    )

    print(
        "\nCandidate Evaluation"
    )

    print(
        "===================="
    )

    print(
        "Name:",
        result["name"]
    )

    print(
        "\nRequired Skill Score:",
        result["required_skill_score"],
        "%"
    )

    print(
        "Preferred Skill Score:",
        result["preferred_skill_score"],
        "%"
    )

    print(
        "Overall Skill Score:",
        result["overall_skill_score"],
        "%"
    )

    print(
        "\nKeyword Baseline:",
        result["keyword_skill_score"],
        "%"
    )

    print(
        "Verified Evidence Score:",
        result["semantic_evidence_score"],
        "%"
    )

    print(
        "Hybrid Skill Score:",
        result["hybrid_skill_score"],
        "%"
    )

    print(
        "\nExperience:",
        result["experience"],
        "years"
    )

    print(
        "Experience Score:",
        result["experience_score"]
    )

    print(
        "Education Score:",
        result["education_score"]
    )

    print(
        "Final Candidate Score:",
        result["final_score"],
        "%"
    )

    print(
        "\nMatched Required Skills:"
    )

    for skill in result[
        "matched_required"
    ]:

        print(
            "-",
            skill
        )

    print(
        "\nMissing Required Skills:"
    )

    for skill in result[
        "missing_skills"
    ]:

        print(
            "-",
            skill
        )

    print(
        "\nVerified Evidence:"
    )

    for item in result[
        "evidence"
    ]:

        status = (
            "VERIFIED"
            if item["verified"]
            else "NOT VERIFIED"
        )

        print(
            f"- {item['skill']}: "
            f"{status}"
        )

        if item["evidence"]:

            print(
                f"  {item['evidence']['section']} "
                f"({item['evidence']['score']}%)"
            )