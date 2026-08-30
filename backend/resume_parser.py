import pymupdf
import re


def extract_text_from_pdf(file_path):
    document = pymupdf.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


def clean_text(text):
    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove unnecessary spaces at line ends
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    text = "\n".join(lines)

    # Remove excessive blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()


def extract_candidate_info(text):

    candidate = {
        "name": None,
        "email": None,
        "phone": None,
        "linkedin": None,
        "location": None
    }

    # -------------------------
    # Email
    # -------------------------

    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    if email_match:
        candidate["email"] = email_match.group().strip()

    # -------------------------
    # Phone
    # -------------------------

    phone_match = re.search(
        r"\+?\d[\d\s-]{8,}\d",
        text
    )

    if phone_match:
        candidate["phone"] = phone_match.group().strip()

    # -------------------------
    # LinkedIn
    # -------------------------

    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s]+",
        text,
        re.IGNORECASE
    )

    if linkedin_match:
        candidate["linkedin"] = linkedin_match.group().strip()

    # -------------------------
    # Location
    # -------------------------

    location_match = re.search(
        r"([A-Za-z ]+,\s*[A-Za-z ]+)",
        text
    )

    if location_match:
        candidate["location"] = (
            location_match.group().strip()
        )

    # -------------------------
    # Name
    # -------------------------

    lines = text.splitlines()

    ignored_names = {
        "SKILLS",
        "LANGUAGES",
        "EDUCATION",
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "PROJECTS",
        "INTERESTS",
        "OBJECTIVE",
        "SUMMARY",
        "PROFILE",
        "ABOUT ME",
        "CONTACT",
        "CERTIFICATIONS",
        "ACHIEVEMENTS",
        "EXTRA CURRICULAR ACTIVITIES",
        "EXTRACURRICULAR ACTIVITIES",
        "HARD SKILLS",
        "SOFT SKILLS"
    }

    # Only inspect the beginning of the resume
    top_lines = [
        line.strip()
        for line in lines[:15]
        if line.strip()
    ]

    for line in top_lines:

        upper_line = line.upper()

        # Ignore known headings
        if upper_line in ignored_names:
            continue

        # Ignore email
        if "@" in line:
            continue

        # Ignore LinkedIn
        if "linkedin.com" in line.lower():
            continue

        # Ignore phone numbers
        if re.search(
            r"\+?\d[\d\s-]{8,}",
            line
        ):
            continue

        # Name should be short
        if len(line.split()) > 4:
            continue

        # Must contain letters
        if not re.search(
            r"[A-Za-z]",
            line
        ):
            continue

        # Ignore punctuation-heavy lines
        if re.search(
            r"[|:/]",
            line
        ):
            continue

        candidate["name"] = line
        break

    return candidate


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

    candidate = extract_candidate_info(
        cleaned_text
    )

    print("\nCandidate Information")
    print("---------------------")

    for key, value in candidate.items():
        print(
            f"{key}: {value}"
        )