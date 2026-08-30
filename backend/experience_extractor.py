import pymupdf
import re


def extract_text_from_pdf(file_path):
    document = pymupdf.open(file_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


def extract_experience(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return float(match.group(1))

    return 0.0


def calculate_experience_score(years):
    if years >= 5:
        return 100

    if years >= 3:
        return 80

    if years >= 1:
        return 60

    return 40


if __name__ == "__main__":

    resume_path = "data/resumes/sample_resume.pdf"

    resume_text = extract_text_from_pdf(resume_path)

    years = extract_experience(resume_text)

    score = calculate_experience_score(years)

    print("\nExperience Analysis")
    print("-------------------")
    print("Experience:", years, "years")
    print("Experience Score:", score)