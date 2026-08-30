import re


SKILL_LIST = [
    "Python",
    "Java",
    "JavaScript",
    "HTML",
    "CSS",
    "React",
    "Flutter",
    "MongoDB",
    "SQL",
    "Django",
    "Arduino",
    "IoT",
    "Canva",
    "C++",
    "C",
    "Git",
    "GitHub",
    "Machine Learning",
    "Data Analysis",
    "Artificial Intelligence",
]


def extract_skills(text):
    found_skills = []

    # Convert everything to lowercase
    normalized_text = text.lower()

    # Patterns allow common variations
    skill_patterns = {
        "Python": r"\bpython\b",

        "Java": r"\bjava\b",

        "JavaScript": r"\bjavascript\b",

        "HTML": r"\bhtml\b",

        "CSS": r"\bcss\b",

        "React": r"\breact\b",

        "Flutter": r"\bflutter\b",

        # Handles:
        # MongoDB
        # Mongo DB
        # mongo db
        "MongoDB": r"\bmongo\s*db\b",

        "SQL": r"\bsql\b",

        "Django": r"\bdjango\b",

        "Arduino": r"\barduino\b",

        # Handles:
        # IoT
        # IOT
        "IoT": r"\biot\b",

        "Canva": r"\bcanva\b",

        "C++": r"\bc\+\+\b",

        "C": r"\bc\b",

        "Git": r"\bgit\b",

        "GitHub": r"\bgithub\b",

        "Machine Learning":
            r"\bmachine\s+learning\b",

        "Data Analysis":
            r"\bdata\s+analysis\b",

        "Artificial Intelligence":
            r"\bartificial\s+intelligence\b"
    }

    for skill, pattern in skill_patterns.items():

        if re.search(
            pattern,
            normalized_text,
            re.IGNORECASE
        ):
            found_skills.append(skill)

    return found_skills


if __name__ == "__main__":

    sample_text = """
    I have experience with Python, JavaScript,
    HTML, CSS, Flutter, React and Mongo DB.

    I also worked with Arduino, IoT,
    Git and Data Analysis.
    """

    skills = extract_skills(
        sample_text
    )

    print("\nDetected Skills")
    print("----------------")

    for skill in skills:
        print("-", skill)