import pymupdf
import re


EDUCATION_HEADINGS = [
    "education",
    "graduate education",
    "academic background",
    "academic qualifications",
    "educational qualification",
    "educational qualifications",
    "qualifications"
]


STOP_HEADINGS = [
    "skills",
    "languages",
    "experience",
    "work experience",
    "projects",
    "project",
    "certifications",
    "activities",
    "coursework",
    "summary",
    "profile",
    "interests",
    "achievements",
    "extra curricular activities",
    "extracurricular activities"
]


DEGREE_PATTERNS = [
    r"bachelor\s+of\s+technology",
    r"\bb\.?\s*tech\b",
    r"bachelor\s+of\s+engineering",
    r"\bb\.?\s*e\.?\b",
    r"bachelor\s+of\s+science",
    r"\bb\.?\s*sc\.?\b",
    r"master\s+of\s+technology",
    r"\bm\.?\s*tech\b",
    r"master\s+of\s+engineering",
    r"\bm\.?\s*e\.?\b",
    r"master\s+of\s+science",
    r"\bm\.?\s*sc\.?\b",
    r"\bbca\b",
    r"\bmca\b"
]


SCHOOL_PATTERNS = [
    r"higher\s+secondary",
    r"senior\s+secondary",
    r"secondary\s+school",
    r"high\s+school",
    r"\b12th\b",
    r"class\s+12"
]


def normalize_line(line):
    return re.sub(
        r"\s+",
        " ",
        line.strip().lower()
    )


def is_degree(line):
    for pattern in DEGREE_PATTERNS:
        if re.search(
            pattern,
            line,
            re.IGNORECASE
        ):
            return True

    return False


def is_school(line):
    for pattern in SCHOOL_PATTERNS:
        if re.search(
            pattern,
            line,
            re.IGNORECASE
        ):
            return True

    return False


def is_stop_heading(line):

    normalized = normalize_line(line)

    return normalized in STOP_HEADINGS


def find_education_section(lines):

    # -----------------------------------------
    # Case 1:
    # "Education" appears as a heading
    # -----------------------------------------

    for index, line in enumerate(lines):

        normalized = normalize_line(line)

        if normalized in EDUCATION_HEADINGS:

            return index

    # -----------------------------------------
    # Case 2:
    # "Graduate" + "Education" appear
    # separately
    # -----------------------------------------

    for index in range(
        len(lines) - 1
    ):

        first = normalize_line(
            lines[index]
        )

        second = normalize_line(
            lines[index + 1]
        )

        if (
            first == "graduate"
            and second == "education"
        ):
            return index

    return None


def extract_education(text):

    education = []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # -----------------------------------------
    # Find education section
    # -----------------------------------------

    education_index = (
        find_education_section(lines)
    )

    # -----------------------------------------
    # If a clear education heading exists
    # -----------------------------------------

    if education_index is not None:

        education_lines = lines[
            education_index + 1:
        ]

        current_entry = []

        for line in education_lines:

            if is_stop_heading(line):

                if current_entry:

                    education.append(
                        "\n".join(
                            current_entry
                        )
                    )

                break

            if (
                is_degree(line)
                or is_school(line)
            ):

                if current_entry:

                    education.append(
                        "\n".join(
                            current_entry
                        )
                    )

                current_entry = [
                    line
                ]

            else:

                if current_entry:
                    current_entry.append(
                        line
                    )

        if current_entry:

            education.append(
                "\n".join(
                    current_entry
                )
            )

    # -----------------------------------------
    # Fallback:
    # Some PDF layouts place the degree
    # before the "Education" heading.
    # -----------------------------------------

    if not education:

        current_entry = []

        for index, line in enumerate(lines):

            if is_degree(line):

                if current_entry:

                    education.append(
                        "\n".join(
                            current_entry
                        )
                    )

                current_entry = [
                    line
                ]

                # Collect a few nearby lines
                for next_line in lines[
                    index + 1:index + 5
                ]:

                    if is_stop_heading(
                        next_line
                    ):
                        break

                    current_entry.append(
                        next_line
                    )

                education.append(
                    "\n".join(
                        current_entry
                    )
                )

                current_entry = []

            elif is_school(line):

                current_entry = [
                    line
                ]

                for next_line in lines[
                    index + 1:index + 5
                ]:

                    if is_stop_heading(
                        next_line
                    ):
                        break

                    current_entry.append(
                        next_line
                    )

                education.append(
                    "\n".join(
                        current_entry
                    )
                )

    # -----------------------------------------
    # Remove duplicates
    # -----------------------------------------

    unique_education = []

    for item in education:

        item = item.strip()

        if (
            item
            and item not in unique_education
        ):
            unique_education.append(
                item
            )

    return unique_education


def calculate_education_score(
    education
):

    education_text = " ".join(
        education
    ).lower()

    # -----------------------------------------
    # Degree = 100
    # -----------------------------------------

    for pattern in DEGREE_PATTERNS:

        if re.search(
            pattern,
            education_text,
            re.IGNORECASE
        ):
            return 100

    # -----------------------------------------
    # Higher secondary = 60
    # -----------------------------------------

    for pattern in SCHOOL_PATTERNS:

        if re.search(
            pattern,
            education_text,
            re.IGNORECASE
        ):
            return 60

    return 0


if __name__ == "__main__":

    resume_path = (
        "data/resumes/sample_resume.pdf"
    )

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

    education_score = (
        calculate_education_score(
            education
        )
    )

    print("\nEducation")
    print("---------")

    if education:

        for item in education:

            print(item)
            print()

    else:

        print(
            "No education information detected."
        )

    print(
        "Education Score:",
        education_score
    )