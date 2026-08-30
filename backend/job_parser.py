import re


SKILL_PATTERNS = {
    "Python": r"\bpython\b",
    "Java": r"\bjava\b",
    "JavaScript": r"\bjavascript\b",
    "HTML": r"\bhtml\b",
    "CSS": r"\bcss\b",
    "React": r"\breact\b",
    "Flutter": r"\bflutter\b",
    "MongoDB": r"\bmongo\s*db\b",
    "SQL": r"\bsql\b",
    "Django": r"\bdjango\b",
    "Arduino": r"\barduino\b",
    "IoT": r"\biot\b",
    "Git": r"\bgit\b",
    "GitHub": r"\bgithub\b",
    "Machine Learning": r"\bmachine\s+learning\b",
    "Data Analysis": r"\bdata\s+analysis\b",
    "Artificial Intelligence":
        r"\bartificial\s+intelligence\b",
    "API": r"\bapis?\b",
}


def normalize_text(text):
    return re.sub(
        r"\s+",
        " ",
        text.lower()
    ).strip()


def extract_skills_from_text(text):

    found = []

    for skill, pattern in SKILL_PATTERNS.items():

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            found.append(skill)

    return found


def get_skill_context(
    text,
    skill,
    pattern
):
    """
    Get the sentence containing the skill.
    This helps determine whether the skill
    is required, preferred, or optional.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    for sentence in sentences:

        if re.search(
            pattern,
            sentence,
            re.IGNORECASE
        ):

            return sentence.lower()

    return ""


def classify_skill(
    skill,
    context
):
    """
    Classify a skill based on nearby wording.
    """

    # Strong optional / advantage indicators
    optional_words = [
        "advantage",
        "plus",
        "nice to have",
        "bonus",
        "optional",
        "preferred",
        "preferable",
        "desirable",
        "good to have"
    ]

    for word in optional_words:

        if word in context:

            return "preferred"

    # Required indicators
    required_words = [
        "required",
        "must",
        "need",
        "needed",
        "mandatory",
        "should have",
        "experience with",
        "experience in",
        "proficient",
        "strong"
    ]

    for word in required_words:

        if word in context:

            return "required"

    # Default
    return "required"


def parse_job_description(
    job_description
):

    text = normalize_text(
        job_description
    )

    required_skills = []
    preferred_skills = []

    for skill, pattern in SKILL_PATTERNS.items():

        if not re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            continue

        context = get_skill_context(
            text,
            skill,
            pattern
        )

        classification = classify_skill(
            skill,
            context
        )

        if classification == "preferred":

            preferred_skills.append(
                skill
            )

        else:

            required_skills.append(
                skill
            )

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills
    }


if __name__ == "__main__":

    print("\nJob Requirements")
    print("----------------")

    job_description = input(
        "Job Description: "
    )

    result = parse_job_description(
        job_description
    )

    print(
        "\nRequired Skills:"
    )

    print(
        result["required_skills"]
    )

    print(
        "\nPreferred Skills:"
    )

    print(
        result["preferred_skills"]
    )