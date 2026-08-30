from resume_parser import (
    extract_text_from_pdf,
    clean_text
)

from job_parser import parse_job_description

from matcher import match_candidate

from semantic_retriever import (
    retrieve_relevant_chunks
)

from evidence_matcher import (
    build_evidence
)

from evidence_scorer import (
    calculate_evidence_score
)


def calculate_hybrid_score(
    keyword_score,
    semantic_score,
    keyword_weight=0.70,
    semantic_weight=0.30
):
    """
    Combine keyword matching and semantic
    evidence into a hybrid matching score.
    """

    total_weight = (
        keyword_weight +
        semantic_weight
    )

    if total_weight == 0:
        return 0.0

    keyword_weight = (
        keyword_weight / total_weight
    )

    semantic_weight = (
        semantic_weight / total_weight
    )

    hybrid_score = (
        (keyword_score * keyword_weight)
        +
        (semantic_score * semantic_weight)
    )

    return round(
        hybrid_score,
        2
    )


if __name__ == "__main__":

    # -------------------------
    # Resume
    # -------------------------

    resume_path = (
        "data/resumes/sample_resume.pdf"
    )

    raw_text = extract_text_from_pdf(
        resume_path
    )

    resume_text = clean_text(
        raw_text
    )

    # -------------------------
    # Job Description
    # -------------------------

    job_description = """
    We are looking for a Python developer
    with experience in JavaScript, React,
    MongoDB, Git and Data Analysis.
    """

    # -------------------------
    # Keyword matching
    # -------------------------

    job = parse_job_description(
        job_description
    )

    required_skills = job[
        "required_skills"
    ]

    candidate_skills = match_candidate

    # Get candidate skills from resume
    from skill_extractor import extract_skills

    resume_skills = extract_skills(
        resume_text
    )

    match_result = match_candidate(
        resume_skills,
        required_skills
    )

    keyword_score = match_result[
        "match_percentage"
    ]

    # -------------------------
    # Semantic retrieval
    # -------------------------

    retrieved_chunks = (
        retrieve_relevant_chunks(
            resume_text,
            job_description,
            top_k=3
        )
    )

    # -------------------------
    # Evidence
    # -------------------------

    evidence = build_evidence(
        retrieved_chunks,
        required_skills
    )

    # -------------------------
    # Semantic evidence score
    # -------------------------

    semantic_score = (
        calculate_evidence_score(
            evidence
        )
    )

    # -------------------------
    # Hybrid score
    # -------------------------

    hybrid_score = calculate_hybrid_score(
        keyword_score,
        semantic_score
    )

    # -------------------------
    # Display
    # -------------------------

    print("\nHybrid Matching")
    print("================")

    print(
        "Keyword Score:",
        keyword_score,
        "%"
    )

    print(
        "Semantic Evidence Score:",
        semantic_score,
        "%"
    )

    print(
        "Hybrid Score:",
        hybrid_score,
        "%"
    )

    print("\nEvidence")
    print("--------")

    for item in evidence:

        print(
            f"{item['section']} "
            f"-> "
            f"{item['semantic_score']}%"
        )

        print(
            "Matched Skills:",
            item["matched_skills"]
        )