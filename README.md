Recruiter AI Agent
Overview

Recruiter AI Agent is an AI-powered recruitment assistant designed to make the candidate screening process faster and easier for recruiters.

The project takes a job description and candidate resumes, analyzes them against the job requirements, and provides a ranking based on skills, experience, education, and supporting evidence. The current prototype uses a Streamlit interface so recruiters can upload multiple resumes and quickly compare candidates.

Problem Statement

Recruiters often have to manually go through many resumes and compare them with job requirements. This can take a lot of time and may make it difficult to consistently identify the most suitable candidates.

This project aims to automate the initial screening process by using AI to understand resumes and job requirements, match candidates, and provide a clear ranking for the recruiter.

Current Features
📄 Resume parsing from PDF files
🔍 Skill extraction from resumes
💼 Job requirement extraction
🤝 Candidate-to-job matching
🧠 Semantic skill matching
✅ Skill evidence verification
📊 Candidate scoring
🏆 Candidate ranking
👤 Candidate information extraction
🎓 Education evaluation
💻 Experience evaluation
📑 Support for analyzing multiple resumes
🌐 Streamlit-based recruiter interface
How It Works

The current workflow is:

Job Description
       ↓
Job Requirement Extraction
       ↓
Candidate Resume Upload
       ↓
Resume Parsing
       ↓
Skill & Information Extraction
       ↓
Candidate Matching
       ↓
Skill Evidence Verification
       ↓
Scoring
       ↓
Candidate Ranking
       ↓
Recruiter Dashboard

The system doesn't rely only on keyword matching. It also uses semantic similarity and evidence from the resume to provide a more meaningful candidate score.

Technology Stack
Frontend
Streamlit
Backend
Python
LangChain (planned/integration stage)
spaCy
pandas
PyMuPDF
AI / NLP
Sentence Transformers
all-MiniLM-L6-v2
Semantic similarity
Skill and evidence matching
Data
SQLite (planned)
PDF resumes
Project Structure
Recruiter-AI-Agent-main/
│
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
│   ├── skill_retriever.py
│   ├── semantic_matcher.py
│   ├── semantic_retriever.py
│   ├── verified_skill_evidence.py
│   ├── evidence_scorer.py
│   ├── experience_extractor.py
│   ├── education_extractor.py
│   └── ...
│
└── data/
    └── resumes/
Running the Project
1. Clone the repository
git clone https://github.com/sanjaykanna-hub/Recruiter-AI-Agent.git
cd Recruiter-AI-Agent-main
2. Create a virtual environment
python -m venv venv

Activate it on Windows:

venv\Scripts\activate
3. Install the dependencies
pip install -r requirements.txt

If any dependency is missing, it can also be installed using:

python -m pip install <package-name>
4. Start the Streamlit application
python -m streamlit run app.py

Then open the local Streamlit URL shown in the terminal, normally:

http://localhost:8501
Using the Application
Enter or paste a job description.
Upload one or more candidate resumes in PDF format.
Click Analyze Candidates.
The system processes each resume.
Candidates are scored and ranked.
Review the candidate details, matched skills, missing skills, and verified evidence.
Example

For a React Frontend Developer position, the recruiter can provide requirements such as:

Required:
- React.js
- JavaScript
- HTML
- CSS
- Git
- REST APIs

Preferred:
- TypeScript
- Redux
- Next.js
- Node.js

The system then compares the uploaded resumes with these requirements and produces a candidate ranking.

Project Status

The project is currently being developed as a Track A recruitment AI prototype.

Completed
Resume parsing
Job requirement extraction
Skill extraction
Candidate matching
Semantic matching
Evidence verification
Candidate scoring
Candidate ranking
Streamlit screening interface
Planned / Next Steps
Integrate the screening workflow with a LangChain-based recruitment agent
Add recruitment tools to the agent
Add candidate pipeline management
Add basic interview scheduling
Improve the Streamlit dashboard
Add report/export functionality
Testing and deployment
Future Agentic AI Workflow

The planned Recruiter AI Agent will use LangChain to connect the existing recruitment functions as tools.

Recruiter
    ↓
Streamlit
    ↓
Recruiter AI Agent
    ↓
┌───────────────────────┐
│ Recruitment Tools     │
├───────────────────────┤
│ Resume Parser         │
│ Job Analyzer          │
│ Candidate Matcher     │
│ Evidence Verifier     │
│ Candidate Evaluator   │
│ Candidate Ranker      │
└───────────────────────┘
    ↓
Recruitment Recommendation

The goal is to allow the agent to coordinate these tools instead of requiring the recruiter to perform each screening step manually.

Goal

The overall goal of Recruiter AI Agent is to automate candidate screening, simplify the hiring workflow, and help recruiters make faster and more informed decisions.

Author

Sanjaykanna,Surendaran

This project is being developed as an AI-powered recruitment assistant with a focus on practical resume screening and candidate matching.
