def calculate_skill_scores(
    candidate_skills,
    required_skills,
    preferred_skills
):
    """
    Calculate separate scores for required
    and preferred skills.
    """

    candidate_set = {
        skill.lower()
        for skill in candidate_skills
    }

    required_set = {
        skill.lower()
        for skill in required_skills
    }

    preferred_set = {
        skill.lower()
        for skill in preferred_skills
    }

    # -------------------------
    # Required skills
    # -------------------------

    matched_required = []

    for skill in required_skills:

        if skill.lower() in candidate_set:

            matched_required.append(
                skill
            )

    if required_skills:

        required_score = (
            len(matched_required)
            / len(required_skills)
        ) * 100

    else:

        required_score = 0.0

    # -------------------------
    # Preferred skills
    # -------------------------

    matched_preferred = []

    for skill in preferred_skills:

        if skill.lower() in candidate_set:

            matched_preferred.append(
                skill
            )

    if preferred_skills:

        preferred_score = (
            len(matched_preferred)
            / len(preferred_skills)
        ) * 100

    else:

        preferred_score = 0.0

    # -------------------------
    # Overall skill score
    # -------------------------

    # Required skills have higher importance
    # than preferred skills.

    overall_score = (
        (required_score * 0.75)
        +
        (preferred_score * 0.25)
    )

    return {
        "required_score": round(
            required_score,
            2
        ),

        "preferred_score": round(
            preferred_score,
            2
        ),

        "overall_score": round(
            overall_score,
            2
        ),

        "matched_required": matched_required,

        "matched_preferred": matched_preferred
    }


if __name__ == "__main__":

    candidate_skills = [
        "Python",
        "JavaScript",
        "HTML",
        "CSS",
        "React",
        "MongoDB",
        "Data Analysis"
    ]

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

    result = calculate_skill_scores(
        candidate_skills,
        required_skills,
        preferred_skills
    )

    print("\nAdvanced Skill Scoring")
    print("======================")

    print(
        "\nRequired Skill Score:",
        result["required_score"],
        "%"
    )

    print(
        "Matched Required:",
        result["matched_required"]
    )

    print(
        "\nPreferred Skill Score:",
        result["preferred_score"],
        "%"
    )

    print(
        "Matched Preferred:",
        result["matched_preferred"]
    )

    print(
        "\nOverall Skill Score:",
        result["overall_score"],
        "%"
    )