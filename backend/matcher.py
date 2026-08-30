def match_candidate(candidate_skills, required_skills):
    # Convert skills to lowercase for case-insensitive comparison
    candidate_skills_lower = {
        skill.lower() for skill in candidate_skills
    }

    required_skills_lower = {
        skill.lower() for skill in required_skills
    }

    # Find matched and missing skills
    matched_skills = [
        skill for skill in required_skills
        if skill.lower() in candidate_skills_lower
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill.lower() not in candidate_skills_lower
    ]

    # Calculate match percentage
    if len(required_skills) == 0:
        match_percentage = 0
    else:
        match_percentage = (
            len(matched_skills) / len(required_skills)
        ) * 100

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_percentage": round(match_percentage, 2)
    }


if __name__ == "__main__":

    candidate_skills = [
        "Python",
        "Java",
        "JavaScript",
        "HTML",
        "CSS",
        "React",
        "Flutter",
        "Arduino",
        "IoT",
        "Canva",
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

    result = match_candidate(
        candidate_skills,
        required_skills
    )

    print("\nCandidate Matching")
    print("------------------")

    print("Matched Skills:", result["matched_skills"])
    print("Missing Skills:", result["missing_skills"])
    print("Match Percentage:", result["match_percentage"], "%")