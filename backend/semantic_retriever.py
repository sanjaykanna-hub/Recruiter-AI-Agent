import numpy as np

from sentence_transformers import SentenceTransformer

from resume_chunker import chunk_resume

from resume_parser import (
    extract_text_from_pdf,
    clean_text
)


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(
    MODEL_NAME
)


def retrieve_relevant_chunks(
    resume_text,
    job_description,
    top_k=3
):
    # -------------------------
    # Create resume chunks
    # -------------------------

    chunks = chunk_resume(
        resume_text
    )

    if not chunks:
        return []

    # -------------------------
    # Create embeddings
    # -------------------------

    chunk_texts = [
        chunk["text"]
        for chunk in chunks
    ]

    chunk_embeddings = model.encode(
        chunk_texts,
        normalize_embeddings=True
    )

    job_embedding = model.encode(
        job_description,
        normalize_embeddings=True
    )

    # -------------------------
    # Calculate similarity
    # -------------------------

    similarities = np.dot(
        chunk_embeddings,
        job_embedding
    )

    # -------------------------
    # Attach scores
    # -------------------------

    results = []

    for chunk, similarity in zip(
        chunks,
        similarities
    ):

        score = max(
            0,
            min(
                1,
                float(similarity)
            )
        ) * 100

        results.append({
            "section": chunk["section"],
            "text": chunk["text"],
            "score": round(
                score,
                2
            )
        })

    # -------------------------
    # Sort by relevance
    # -------------------------

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # -------------------------
    # Return top chunks
    # -------------------------

    return results[:top_k]


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
    # Read resume
    # -------------------------

    raw_text = extract_text_from_pdf(
        resume_path
    )

    resume_text = clean_text(
        raw_text
    )

    # -------------------------
    # Retrieve chunks
    # -------------------------

    results = retrieve_relevant_chunks(
        resume_text,
        job_description,
        top_k=3
    )

    # -------------------------
    # Display results
    # -------------------------

    print("\nRelevant Resume Sections")
    print("=========================")

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n{index}. "
            f"{result['section']}"
        )

        print(
            f"Relevance Score: "
            f"{result['score']}%"
        )

        print(
            "----------------"
        )

        print(
            result["text"]
        )