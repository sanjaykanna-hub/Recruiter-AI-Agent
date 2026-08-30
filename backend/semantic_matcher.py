import numpy as np
from sentence_transformers import SentenceTransformer

from resume_parser import (
    extract_text_from_pdf,
    clean_text
)


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def calculate_semantic_similarity(
    resume_text,
    job_description
):
    resume_embedding = model.encode(
        resume_text,
        normalize_embeddings=True
    )

    job_embedding = model.encode(
        job_description,
        normalize_embeddings=True
    )

    similarity = np.dot(
        resume_embedding,
        job_embedding
    )

    similarity_percentage = (
        max(0, min(1, similarity)) * 100
    )

    return round(
        float(similarity_percentage),
        2
    )


if __name__ == "__main__":

    resume_path = (
        "data/resumes/sample_resume.pdf"
    )

    job_description = """
    We are looking for a Python developer
    with experience in JavaScript, React,
    MongoDB, Git and Data Analysis.
    """

    # -------------------------
    # Read actual resume
    # -------------------------

    raw_text = extract_text_from_pdf(
        resume_path
    )

    resume_text = clean_text(
        raw_text
    )

    # -------------------------
    # Semantic matching
    # -------------------------

    score = calculate_semantic_similarity(
        resume_text,
        job_description
    )

    print("\nSemantic Matching")
    print("-----------------")
    print("Resume:", resume_path)
    print("Semantic Match Score:", score, "%")