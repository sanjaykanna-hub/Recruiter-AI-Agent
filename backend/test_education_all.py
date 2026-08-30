import os
import pymupdf

from education_extractor import (
    extract_education,
    calculate_education_score
)


RESUME_FOLDER = "data/resumes"


for filename in os.listdir(RESUME_FOLDER):

    if not filename.lower().endswith(".pdf"):
        continue

    resume_path = os.path.join(
        RESUME_FOLDER,
        filename
    )

    print("\n")
    print("=" * 60)
    print(f"Resume: {filename}")
    print("=" * 60)

    document = pymupdf.open(
        resume_path
    )

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    education = extract_education(
        text
    )

    score = calculate_education_score(
        education
    )

    print("\nExtracted Education:")
    print("--------------------")

    if education:

        for item in education:
            print(item)
            print()

    else:

        print(
            "NO EDUCATION DETECTED"
        )

    print(
        "Education Score:",
        score
    )