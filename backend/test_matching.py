from resume_parser import extract_text_from_pdf, clean_text
from skill_extractor import extract_skills
from job_parser import parse_job_description
from matcher import match_candidate


# Resume
resume_path = "data/resumes/sample_resume.pdf"

raw_text = extract_text_from_pdf(resume_path)
cleaned_text = clean_text(raw_text)

candidate_skills = extract_skills(cleaned_text)


# Job Description
job_description = """
We are looking for a Python developer with experience in
JavaScript, React, MongoDB, Git and Data Analysis.
"""

job = parse_job_description(job_description)

required_skills = job["required_skills"]


# Match candidate with job
result = match_candidate(
    candidate_skills,
    required_skills
)


# Display result
print("\nCandidate Skills")
print("----------------")
print(candidate_skills)

print("\nRequired Skills")
print("----------------")
print(required_skills)

print("\nMatching Result")
print("----------------")
print("Matched Skills:", result["matched_skills"])
print("Missing Skills:", result["missing_skills"])
print("Match Percentage:", result["match_percentage"], "%")