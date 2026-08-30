import re
import numpy as np

from sentence_transformers import SentenceTransformer

from skill_retriever import (
    find_skill_evidence,
    extract_resume_sections
)


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(
    MODEL_NAME
)


SKILL_ALIASES = {

    "mongodb": [
        "mongodb",
        "mongo db"
    ],

    "javascript": [
        "javascript",
        "java script"
    ],

    "machine learning": [
        "machine learning"
    ],

    "data analysis": [
        "data analysis",
        "data analytics"
    ],

    "api": [
        "api",
        "apis"
    ],

    "git": [
        "git",
        "github"
    ]
}


def skill_exists_in_text(
    skill,
    text
):

    skill_key = skill.lower().strip()

    patterns = SKILL_ALIASES.get(
        skill_key,
        [skill_key]
    )

    for pattern in patterns:

        if re.search(
            r"\b"
            + re.escape(pattern)
            + r"\b",
            text.lower()
        ):

            return True

    return False


def calculate_semantic_score(
    skill,
    section_text
):
    """
    Calculate the actual semantic similarity
    between a skill and its supporting section.
    """

    skill_embedding = model.encode(
        skill,
        normalize_embeddings=True
    )

    section_embedding = model.encode(
        section_text,
        normalize_embeddings=True
    )

    similarity = float(
        np.dot(
            skill_embedding,
            section_embedding
        )
    )

    # Convert cosine similarity to percentage
    score = similarity * 100

    # Keep score within valid range
    score = max(
        0,
        min(
            score,
            100
        )
    )

    return round(
        score,
        2
    )


def find_best_exact_evidence(
    skill,
    exact_sections
):

    if not exact_sections:

        return None

    best = None

    best_score = -1

    for section in exact_sections:

        score = calculate_semantic_score(
            skill,
            section["text"]
        )

        if score > best_score:

            best_score = score

            best = {

                "section":
                    section["section"],

                "score":
                    score,

                "text":
                    section["text"]
            }

    return best


def build_verified_skill_evidence(
    resume_text,
    required_skills
):

    sections = extract_resume_sections(
        resume_text
    )

    # Retrieve semantic candidates
    retrieved = find_skill_evidence(
        resume_text,
        required_skills,
        top_k=3
    )

    results = []

    for item in retrieved:

        skill = item["skill"]

        # --------------------------------
        # Exact verification
        # --------------------------------

        exact_sections = []

        for section in sections:

            if skill_exists_in_text(
                skill,
                section["text"]
            ):

                exact_sections.append(
                    section
                )

        # --------------------------------
        # Not found anywhere
        # --------------------------------

        if not exact_sections:

            results.append({

                "skill":
                    skill,

                "verified":
                    False,

                "evidence":
                    None
            })

            continue

        # --------------------------------
        # Calculate real semantic score
        # for every exact section
        # --------------------------------

        best_evidence = (
            find_best_exact_evidence(
                skill,
                exact_sections
            )
        )

        results.append({

            "skill":
                skill,

            "verified":
                True,

            "evidence":
                best_evidence
        })

    return results


if __name__ == "__main__":

    from resume_parser import (
        extract_text_from_pdf,
        clean_text
    )

    resume_path = (
        "data/resumes/candidate2.pdf"
    )

    required_skills = [
        "Python",
        "JavaScript",
        "React",
        "MongoDB",
        "Git",
        "Data Analysis"
    ]

    raw_text = extract_text_from_pdf(
        resume_path
    )

    resume_text = clean_text(
        raw_text
    )

    results = build_verified_skill_evidence(
        resume_text,
        required_skills
    )

    print(
        "\nVerified Skill Evidence"
    )

    print(
        "======================="
    )

    for item in results:

        print(
            f"\nSkill: {item['skill']}"
        )

        if item["verified"]:

            evidence = item["evidence"]

            print(
                "Status: VERIFIED"
            )

            print(
                f"Section: "
                f"{evidence['section']}"
            )

            print(
                f"Semantic Score: "
                f"{evidence['score']}%"
            )

            print(
                "Evidence:"
            )

            print(
                evidence["text"]
            )

        else:

            print(
                "Status: NOT VERIFIED"
            )

        print(
            "-----------------------"
        )