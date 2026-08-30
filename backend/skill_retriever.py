import re
import numpy as np
import pymupdf

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(
    MODEL_NAME
)


def extract_resume_sections(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    sections = []

    current_section = "General"
    current_text = []

    headings = [
        "about me",
        "summary",
        "profile",
        "education",
        "skills",
        "interests",
        "experience",
        "projects",
        "project",
        "activities",
        "extra curricular activities",
        "extracurricular activities",
        "certifications"
    ]

    for line in lines:

        normalized = line.lower().strip()

        if normalized in headings:

            if current_text:

                sections.append({
                    "section": current_section,
                    "text": " ".join(
                        current_text
                    )
                })

            current_section = line
            current_text = []

        else:

            current_text.append(line)

    if current_text:

        sections.append({
            "section": current_section,
            "text": " ".join(
                current_text
            )
        })

    return sections


def find_skill_evidence(
    resume_text,
    required_skills,
    top_k=1
):

    sections = extract_resume_sections(
        resume_text
    )

    if not sections:

        return []

    section_texts = [
        item["text"]
        for item in sections
    ]

    section_embeddings = model.encode(
        section_texts,
        normalize_embeddings=True
    )

    results = []

    for skill in required_skills:

        skill_embedding = model.encode(
            skill,
            normalize_embeddings=True
        )

        similarities = np.dot(
            section_embeddings,
            skill_embedding
        )

        indices = np.argsort(
            similarities
        )[::-1][:top_k]

        evidence = []

        for index in indices:

            score = float(
                similarities[index]
            ) * 100

            score = max(
                0,
                min(
                    score,
                    100
                )
            )

            evidence.append({

                "section":
                    sections[index]["section"],

                "score":
                    round(
                        score,
                        2
                    ),

                "text":
                    sections[index]["text"]
            })

        results.append({

            "skill": skill,

            "evidence": evidence
        })

    return results


if __name__ == "__main__":

    resume_path = (
        "data/resumes/sample_resume.pdf"
    )

    required_skills = [
        "Python",
        "JavaScript",
        "React",
        "MongoDB",
        "Git",
        "Data Analysis"
    ]

    document = pymupdf.open(
        resume_path
    )

    text = ""

    for page in document:

        text += page.get_text()

    document.close()

    results = find_skill_evidence(
        text,
        required_skills
    )

    print("\nSkill-Specific RAG Evidence")
    print("============================")

    for item in results:

        print(
            f"\nSkill: {item['skill']}"
        )

        if not item["evidence"]:

            print(
                "No evidence found."
            )

            continue

        for evidence in item[
            "evidence"
        ]:

            print(
                f"Section: "
                f"{evidence['section']}"
            )

            print(
                f"Relevance: "
                f"{evidence['score']}%"
            )

            print(
                "Evidence:"
            )

            print(
                evidence["text"]
            )

            print(
                "--------------------"
            )