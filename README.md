# Recruiter AI Agent

## About the Project

Recruiter AI Agent is an AI-powered recruitment assistant that helps recruiters screen and compare candidates based on a given job description.

The system takes a job description and candidate resumes as input, analyzes the resumes, matches candidate skills with the job requirements, verifies supporting evidence, and ranks the candidates based on their overall suitability.

## Problem Statement

Recruiters often spend a lot of time manually reviewing resumes and comparing candidates with job requirements. This becomes difficult when there are multiple applicants.

The aim of this project is to automate the initial candidate screening process and help recruiters identify suitable candidates faster.

## Current Features

- Resume parsing from PDF files
- Job requirement extraction
- Candidate information extraction
- Skill extraction
- Candidate-to-job matching
- Semantic skill matching
- Skill evidence verification
- Experience evaluation
- Education evaluation
- Candidate scoring
- Candidate ranking
- Multiple resume analysis
- Streamlit-based user interface

## How It Works

The current workflow is:

Job Description  
↓  
Job Requirement Extraction  
↓  
Resume Upload  
↓  
Resume Parsing  
↓  
Skill Extraction  
↓  
Candidate Matching  
↓  
Evidence Verification  
↓  
Candidate Scoring  
↓  
Candidate Ranking  
↓  
Recruiter Results

## Technology Used

- Python
- Streamlit
- spaCy
- pandas
- PyMuPDF
- Sentence Transformers
- SQLite (planned)
- LangChain (agent integration planned)

## Project Structure

Recruiter-AI-Agent-main/

├── app.py  
├── requirements.txt  
├── .gitignore  
│  
├── backend/  
│   ├── resume_parser.py  
│   ├── job_parser.py  
│   ├── matcher.py  
│   ├── scorer.py  
│   ├── ranker.py  
│   ├── skill_extractor.py  
│   ├── semantic_matcher.py  
│   ├── evidence_scorer.py  
│   ├── verified_skill_evidence.py  
│   ├── experience_extractor.py  
│   ├── education_extractor.py  
│   └── ...  
│  
└── data/  
    └── resumes/

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/sanjaykanna-hub/Recruiter-AI-Agent.git
cd Recruiter-AI-Agent-main
2. Create a virtual environment
python -m venv venv
3. Activate the virtual environment

For Windows:

venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
5. Run the Streamlit application
python -m streamlit run app.py

Open the local URL provided by Streamlit, usually:

http://localhost:8501
How to Use
Enter the job description in the application.
Upload one or more candidate resumes in PDF format.
Click Analyze Candidates.
The system processes the resumes.
Candidates are scored and ranked.
Review the matched skills, missing skills, scores, and verified evidence.
Example

For a React Frontend Developer role, the job description can contain requirements such as:

Required Skills
React.js
JavaScript
HTML
CSS
Git
REST APIs
Responsive Web Design
Preferred Skills
TypeScript
Redux
Next.js
Node.js
MongoDB
Jest

The system compares these requirements with the uploaded resumes and generates a candidate ranking.

Current Status

The core candidate screening and matching workflow has been implemented.

Completed
Resume parsing
Skill extraction
Job requirement extraction
Candidate matching
Semantic matching
Evidence verification
Experience and education evaluation
Candidate scoring
Candidate ranking
Streamlit screening interface
Planned
LangChain-based Recruiter AI Agent
Recruitment tools integration
Candidate pipeline management
Basic interview scheduling
Result export
Improved recruiter dashboard
Testing and deployment
Project Goal

The goal of this project is to build an AI-powered recruitment assistant that automates candidate screening, simplifies the recruitment workflow, and helps recruiters make faster and more informed hiring decisions.

Author

Sanjaykanna , Surendaran
