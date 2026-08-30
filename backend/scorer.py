def calculate_candidate_score(
    skill_score,
    experience_score,
    education_score
):
    """
    Final candidate score.

    Weighting:
    Skill       = 60%
    Experience  = 20%
    Education   = 20%
    """

    final_score = (
        (skill_score * 0.60)
        +
        (experience_score * 0.20)
        +
        (education_score * 0.20)
    )

    return round(
        final_score,
        2
    )


if __name__ == "__main__":

    # Example values

    skill_score = 70.59

    experience = 0.0

    experience_score = 40

    education_score = 100

    final_score = calculate_candidate_score(
        skill_score,
        experience_score,
        education_score
    )

    print(
        "\nCandidate Score"
    )

    print(
        "----------------"
    )

    print(
        "Skill Score:",
        skill_score
    )

    print(
        "Experience:",
        experience,
        "years"
    )

    print(
        "Experience Score:",
        experience_score
    )

    print(
        "Education Score:",
        education_score
    )

    print(
        "Final Candidate Score:",
        final_score
    )