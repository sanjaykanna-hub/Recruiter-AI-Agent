def calculate_evidence_score(evidence):
    """
    Calculate an average semantic relevance score
    from retrieved resume evidence.
    """

    if not evidence:
        return 0.0

    scores = [
        item["semantic_score"]
        for item in evidence
    ]

    average_score = sum(scores) / len(scores)

    return round(average_score, 2)


if __name__ == "__main__":

    evidence = [
        {
            "section": "About me",
            "semantic_score": 52.13,
            "matched_skills": [
                "Python",
                "JavaScript"
            ]
        },
        {
            "section": "Skills",
            "semantic_score": 46.40,
            "matched_skills": [
                "Python",
                "JavaScript"
            ]
        },
        {
            "section": "Projects",
            "semantic_score": 38.69,
            "matched_skills": [
                "React",
                "MongoDB"
            ]
        }
    ]

    score = calculate_evidence_score(
        evidence
    )

    print(
        "Evidence Score:",
        score,
        "%"
    )