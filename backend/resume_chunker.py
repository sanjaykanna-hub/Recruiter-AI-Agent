import re

from resume_parser import (
    extract_text_from_pdf,
    clean_text
)


SECTION_HEADINGS = [
    "About me",
    "Education",
    "Skills",
    "Interests",
    "Extra curricular Activities",
    "Projects"
]


def normalize_heading(line):
    return re.sub(
        r"\s+",
        " ",
        line.strip().lower()
    )


def chunk_resume(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    chunks = []

    current_heading = None
    current_content = []

    normalized_headings = {
        normalize_heading(heading): heading
        for heading in SECTION_HEADINGS
    }

    for line in lines:

        normalized_line = normalize_heading(line)

        # Check whether this line is a section heading
        if normalized_line in normalized_headings:

            # Save previous section
            if current_heading is not None:

                content = "\n".join(
                    current_content
                ).strip()

                if content:
                    chunks.append({
                        "section": current_heading,
                        "text": content
                    })

            # Start new section
            current_heading = normalized_headings[
                normalized_line
            ]

            current_content = []

        else:

            if current_heading is not None:
                current_content.append(line)

    # Save final section
    if current_heading is not None:

        content = "\n".join(
            current_content
        ).strip()

        if content:
            chunks.append({
                "section": current_heading,
                "text": content
            })

    return chunks


if __name__ == "__main__":

    resume_path = (
        "data/resumes/sample_resume.pdf"
    )

    raw_text = extract_text_from_pdf(
        resume_path
    )

    cleaned_text = clean_text(
        raw_text
    )

    chunks = chunk_resume(
        cleaned_text
    )

    print("\nResume Chunks")
    print("=============")

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"\nChunk {index}"
        )

        print(
            f"Section: {chunk['section']}"
        )

        print(
            "----------------"
        )

        print(
            chunk["text"]
        )