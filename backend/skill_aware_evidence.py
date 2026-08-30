def calculate_skill_aware_evidence_score(
    verified_evidence,
    required_skills,
    preferred_skills=None
):
    """
    Calculate evidence quality using:
    
    Required skill verification  -> 70%
    Semantic evidence quality    -> 30%

    Preferred skills are reported
    separately and do not increase
    required-skill evidence coverage.
    """

    if preferred_skills is None:
        preferred_skills = []

    if not required_skills:
        return 0.0

    required_set = {
        skill.lower().strip()
        for skill in required_skills
    }

    verified_required = []

    semantic_scores = []

    for item in verified_evidence:

        skill = item.get(
            "skill",
            ""
        ).lower().strip()

        # Only required skills
        if skill not in required_set:
            continue

        if item.get("verified", False):

            verified_required.append(
                skill
            )

            evidence = item.get(
                "evidence"
            )

            if evidence:

                score = evidence.get(
                    "score",
                    0
                )

                # Ignore artificial/invalid values
                if score > 0:

                    semantic_scores.append(
                        score
                    )

    # --------------------------------
    # Required skill coverage
    # --------------------------------

    unique_verified = set(
        verified_required
    )

    coverage_score = (
        len(unique_verified)
        / len(required_set)
    ) * 100

    coverage_score = min(
        max(
            coverage_score,
            0
        ),
        100
    )

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

    semantic_score = min(
        max(
            semantic_score,
            0
        ),
        100
    )

    # --------------------------------
    # Final evidence score
    # --------------------------------

    evidence_score = (
        (coverage_score * 0.70)
        +
        (semantic_score * 0.30)
    )

    evidence_score = min(
        max(
            evidence_score,
            0
        ),
        100
    )

    return round(
        evidence_score,
        2
    )


if __name__ == "__main__":

    required_skills = [
        "Python",
        "JavaScript",
        "React",
        "MongoDB",
        "Git",
        "Data Analysis"
    ]

    preferred_skills = [
        "HTML",
        "CSS",
        "SQL",
        "Machine Learning",
        "API"
    ]

    verified_evidence = [

        {
            "skill": "Python",
            "verified": True,
            "evidence": {
                "score": 35.49
            }
        },

        {
            "skill": "JavaScript",
            "verified": True,
            "evidence": {
                "score": 19.12
            }
        },

        {
            "skill": "React",
            "verified": True,
            "evidence": {
                "score": 16.39
            }
        },

        {
            "skill": "MongoDB",
            "verified": True,
            "evidence": {
                "score": 29.41
            }
        },

        {
            "skill": "Git",
            "verified": False,
            "evidence": None
        },

        {
            "skill": "Data Analysis",
            "verified": True,
            "evidence": {
                "score": 29.74
            }
        }
    ]

    score = calculate_skill_aware_evidence_score(
        verified_evidence,
        required_skills,
        preferred_skills
    )

    print(
        "\nSkill-Aware Evidence Score"
    )

    print(
        "=========================="
    )

    print(
        "Required Skills:",
        len(required_skills)
    )

    print(
        "Verified Required Skills:",
        5
    )

    print(
        "Evidence Score:",
        score,
        "%"
    )