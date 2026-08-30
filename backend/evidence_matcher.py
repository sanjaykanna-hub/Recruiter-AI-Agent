from skill_extractor import extract_skills


def find_chunk_skills(chunk_text, required_skills):
    """
    Find which required job skills appear
    in a retrieved resume chunk.
    """

    chunk_skills = extract_skills(chunk_text)

    matched_skills = [
        skill
        for skill in chunk_skills
        if skill in required_skills
    ]

    return matched_skills


def build_evidence(
    retrieved_chunks,
    required_skills
):
    """
    Add matched job skills to every
    retrieved resume chunk.
    """

    evidence = []

    for chunk in retrieved_chunks:

        matched_skills = find_chunk_skills(
            chunk["text"],
            required_skills
        )

        evidence.append({
            "section": chunk["section"],
            "text": chunk["text"],
            "semantic_score": chunk["score"],
            "matched_skills": matched_skills
        })

    return evidence


if __name__ == "__main__":

    retrieved_chunks = [
        {
            "section": "About me",
            "text": """
            Passionate Information Technology student
            with a foundation in Python and JavaScript.
            """,
            "score": 52.13
        },
        {
            "section": "Skills",
            "text": """
            Java, JavaScript, Python, HTML, CSS,
            Arduino and IoT.
            """,
            "score": 46.40
        },
        {
            "section": "Projects",
            "text": """
            Developed a React farming assistant app
            and an e-commerce application using MongoDB.
            """,
            "score": 38.69
        }
    ]

    required_skills = [
        "Python",
        "JavaScript",
        "React",
        "MongoDB",
        "Git",
        "Data Analysis"
    ]

    evidence = build_evidence(
        retrieved_chunks,
        required_skills
    )

    print("\nResume Evidence")
    print("================")

    for item in evidence:

        print(
            f"\nSection: {item['section']}"
        )

        print(
            f"Semantic Score: "
            f"{item['semantic_score']}%"
        )

        print(
            f"Matched Skills: "
            f"{item['matched_skills']}"
        )
        