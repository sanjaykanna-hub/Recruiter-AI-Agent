from resume_parser import (
    extract_text_from_pdf,
    clean_text
)

from job_parser import parse_job_description

from semantic_retriever import (
    retrieve_relevant_chunks
)

from evidence_matcher import (
    build_evidence
)


RESUME_PATH = "data/resumes/sample_resume.pdf"


JOB_DESCRIPTION = """
We are looking for a Python developer with experience in
JavaScript, React, MongoDB, Git and Data Analysis.
"""


# -------------------------
# Read resume
# -------------------------

raw_text = extract_text_from_pdf(
    RESUME_PATH
)

resume_text = clean_text(
    raw_text
)


# -------------------------
# Parse job
# -------------------------

job = parse_job_description(
    JOB_DESCRIPTION
)

required_skills = job[
    "required_skills"
]


# -------------------------
# Retrieve relevant chunks
# -------------------------

retrieved_chunks = retrieve_relevant_chunks(
    resume_text,
    JOB_DESCRIPTION,
    top_k=3
)


# -------------------------
# Build evidence
# -------------------------

evidence = build_evidence(
    retrieved_chunks,
    required_skills
)


# -------------------------
# Display
# -------------------------

print("\nRAG Evidence Pipeline")
print("=====================")

print("\nRequired Skills:")
print(required_skills)

print("\nRelevant Resume Evidence:")

for index, item in enumerate(
    evidence,
    start=1
):

    print(
        f"\n{index}. {item['section']}"
    )

    print(
        f"Semantic Score: "
        f"{item['semantic_score']}%"
    )

    print(
        f"Matched Skills: "
        f"{item['matched_skills']}"
    )

    print(
        "Evidence:"
    )

    print(
        item["text"]
    )