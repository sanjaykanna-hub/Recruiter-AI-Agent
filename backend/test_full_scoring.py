import pymupdf

from skill_extractor import extract_skills
from job_parser import parse_job_description
from matcher import match_candidate

from experience_extractor import (
    extract_experience,
    calculate_experience_score
)

from education_extractor import (
    extract_education,
    calculate_education_score
)

from scorer import calculate_candidate_score


resume_path = "data/resumes/sample_resume.pdf"


# -------------------------
# Read resume
# -------------------------

document = pymupdf.open(resume_path)

resume_text = ""

for page in document:
    resume_text += page.get_text()

document.close()


# -------------------------
# Extract candidate skills
# -------------------------

candidate_skills = extract_skills(resume_text)


# -------------------------
# Parse job description
# -------------------------

job_description = """
We are looking for a Python developer with experience in
JavaScript, React, MongoDB, Git and Data Analysis.
"""

job = parse_job_description(job_description)

required_skills = job["required_skills"]


# -------------------------
# Match skills
# -------------------------

match_result = match_candidate(
    candidate_skills,
    required_skills
)

skill_score = match_result["match_percentage"]


# -------------------------
# Experience
# -------------------------

experience = extract_experience(resume_text)

experience_score = calculate_experience_score(
    experience
)


# -------------------------
# Education
# -------------------------

education = extract_education(resume_text)

education_score = calculate_education_score(
    education
)


# -------------------------
# Final score
# -------------------------

final_score = calculate_candidate_score(
    skill_score,
    experience_score,
    education_score
)


# -------------------------
# Display
# -------------------------

print("\nFull Candidate Evaluation")
print("--------------------------")

print("Candidate Skills:")
print(candidate_skills)

print("\nRequired Skills:")
print(required_skills)

print("\nMatched Skills:")
print(match_result["matched_skills"])

print("\nMissing Skills:")
print(match_result["missing_skills"])

print("\nSkill Score:", skill_score)

print("Experience:", experience, "years")

print("Experience Score:", experience_score)

print("Education Score:", education_score)

print("Final Candidate Score:", final_score)