import os
import sys
import json
from typing import Any


# ============================================================
# PATH SETUP
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(
    CURRENT_DIR
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT
    )

if CURRENT_DIR not in sys.path:
    sys.path.insert(
        0,
        CURRENT_DIR
    )


# ============================================================
# LANGCHAIN IMPORTS
# ============================================================

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# EXISTING BACKEND IMPORTS
# ============================================================

from candidate_evaluator import (
    evaluate_candidate
)


# ============================================================
# OPTIONAL JOB PARSER
# ============================================================

try:

    from job_parser import (
        parse_job_description
    )

except ImportError:

    parse_job_description = None


# ============================================================
# OPTIONAL EVIDENCE VERIFICATION
# ============================================================

try:

    from verified_skill_evidence import (
        build_verified_skill_evidence
    )

except ImportError:

    build_verified_skill_evidence = None


# ============================================================
# JSON HELPER
# ============================================================

def json_safe(value):

    try:

        json.dumps(
            value
        )

        return value

    except Exception:

        return str(value)


def format_result(result):

    return json.dumps(
        result,
        indent=2,
        default=json_safe
    )


# ============================================================
# TOOL 1
# PARSE RESUME
# ============================================================

@tool
def parse_resume(
    resume_path: str
) -> str:

    """
    Extract text from a candidate resume.

    The resume path is an internal server path.
    Candidates never need to provide this path themselves.
    """

    try:

        from resume_parser import (
            extract_text_from_pdf
        )

        text = extract_text_from_pdf(
            resume_path
        )

        if not text:

            return json.dumps({
                "success": False,
                "message": "No text could be extracted from resume."
            })

        return json.dumps({
            "success": True,
            "resume_path": resume_path,
            "text": text
        })

    except Exception as error:

        return json.dumps({
            "success": False,
            "error": str(error)
        })


# ============================================================
# TOOL 2
# ANALYZE JOB REQUIREMENTS
# ============================================================

@tool
def analyze_job_requirements(
    job_description: str
) -> str:

    """
    Analyze the job description and identify required and
    preferred skills and recruitment requirements.
    """

    try:

        if parse_job_description is None:

            return json.dumps({
                "success": False,
                "message": (
                    "Job parser is not available. "
                    "Use the job description directly "
                    "for evaluation."
                )
            })


        result = parse_job_description(
            job_description
        )


        return format_result(
            result
        )


    except Exception as error:

        return json.dumps({
            "success": False,
            "error": str(error)
        })


# ============================================================
# TOOL 3
# EVALUATE RESUME
# ============================================================

@tool
def evaluate_resume_against_job(
    resume_path: str,
    job_description: str
) -> str:

    """
    Run the existing AI candidate evaluation pipeline.

    This performs the detailed candidate evaluation including
    skills, evidence, experience, education and final score.
    """

    try:

        result = evaluate_candidate(
            resume_path,
            job_description
        )

        return format_result(
            result
        )

    except Exception as error:

        return json.dumps({
            "success": False,
            "error": str(error)
        })


# ============================================================
# TOOL 4
# VERIFY CANDIDATE SKILLS
# ============================================================

@tool
def verify_candidate_skills(
    resume_path: str,
    job_description: str
) -> str:

    """
    Verify candidate skill evidence using the existing
    semantic/evidence verification system.
    """

    try:

        if build_verified_skill_evidence is None:

            return json.dumps({
                "success": False,
                "message": (
                    "Verified skill evidence module "
                    "is not available."
                )
            })


        try:

            result = build_verified_skill_evidence(
                resume_path,
                job_description
            )

        except TypeError:

            result = build_verified_skill_evidence(
                resume_path
            )


        return format_result(
            result
        )


    except Exception as error:

        return json.dumps({
            "success": False,
            "error": str(error)
        })


# ============================================================
# TOOL 5
# RANK CANDIDATES
# ============================================================

@tool
def rank_candidates(
    resume_paths: str,
    job_description: str
) -> str:

    """
    Evaluate multiple resumes against the same job and return
    candidates ordered by their final candidate score.

    resume_paths must be a comma-separated list of internal
    resume paths.
    """

    try:

        paths = [
            path.strip()
            for path in resume_paths.split(",")
            if path.strip()
        ]


        if not paths:

            return json.dumps({
                "success": False,
                "message": "No resume paths were provided."
            })


        candidates = []


        for path in paths:

            result = evaluate_candidate(
                path,
                job_description
            )


            score = (
                result.get(
                    "final_candidate_score",
                    result.get(
                        "final_score",
                        result.get(
                            "score",
                            0
                        )
                    )
                )
                if isinstance(result, dict)
                else 0
            )


            try:

                score = float(
                    score
                )

            except Exception:

                score = 0.0


            candidates.append({

                "resume_path": path,

                "score": score,

                "result": result
            })


        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )


        for rank, candidate in enumerate(
            candidates,
            start=1
        ):

            candidate["rank"] = rank


        return format_result(
            candidates
        )


    except Exception as error:

        return json.dumps({
            "success": False,
            "error": str(error)
        })


# ============================================================
# TOOL LIST
# ============================================================

RECRUITMENT_TOOLS = [

    parse_resume,

    analyze_job_requirements,

    evaluate_resume_against_job,

    verify_candidate_skills,

    rank_candidates
]


# ============================================================
# AGENT SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI Recruitment Screening Agent.

Your job is to assist with candidate screening.

For every candidate screening request:

1. Understand the job description.
2. Analyze the job requirements.
3. Analyze the uploaded resume.
4. Evaluate the candidate against the job.
5. Verify skill evidence when appropriate.
6. Use the existing evaluation tools instead of inventing scores.
7. Return the detailed evaluation produced by the evaluation tool.

IMPORTANT:

- Never invent candidate skills.
- Never invent experience.
- Never invent education.
- Never invent scores.
- Do not reject a candidate merely because a preferred skill is missing.
- Required skills and preferred skills must be treated separately.
- Use the evaluation tool for the actual numerical candidate score.
- The resume path is an internal application path.
- The candidate does not need to know or provide the file path.

For candidate screening, the main evaluation tool is:

evaluate_resume_against_job

Use it to obtain the actual candidate evaluation.
"""


# ============================================================
# CREATE AGENT
# ============================================================

def create_recruitment_agent(
    model=None
):

    api_key = os.getenv(
        "GOOGLE_API_KEY"
    )


    if not api_key:

        raise ValueError(
            "GOOGLE_API_KEY is not set. "
            "Set it in your environment before "
            "starting the recruitment agent."
        )


    if model is None:

        model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )


        model = ChatGoogleGenerativeAI(

            model=model_name,

            temperature=0,

            google_api_key=api_key
        )


    agent = create_agent(

        model=model,

        tools=RECRUITMENT_TOOLS,

        system_prompt=SYSTEM_PROMPT
    )


    return agent


# ============================================================
# EXTRACT EVALUATION FROM AGENT RESPONSE
# ============================================================

def extract_evaluation_from_agent_response(
    response
):

    """
    Extract the structured evaluation result returned by
    evaluate_resume_against_job from the LangChain agent
    response.
    """

    messages = []

    if isinstance(
        response,
        dict
    ):

        messages = response.get(
            "messages",
            []
        )


    # --------------------------------------------------------
    # First look for a ToolMessage belonging to the evaluation
    # tool.
    # --------------------------------------------------------

    for message in messages:

        message_name = getattr(
            message,
            "name",
            None
        )


        if message_name == (
            "evaluate_resume_against_job"
        ):

            content = getattr(
                message,
                "content",
                None
            )


            if not content:
                continue


            if isinstance(
                content,
                list
            ):

                content = "".join(
                    str(item)
                    for item in content
                )


            try:

                return json.loads(
                    content
                )

            except json.JSONDecodeError:

                pass


    # --------------------------------------------------------
    # Fallback: inspect all tool messages for JSON.
    # --------------------------------------------------------

    for message in messages:

        message_type = message.__class__.__name__


        if message_type != "ToolMessage":
            continue


        content = getattr(
            message,
            "content",
            None
        )


        if not content:
            continue


        if isinstance(
            content,
            list
        ):

            content = "".join(
                str(item)
                for item in content
            )


        try:

            data = json.loads(
                content
            )


            if isinstance(
                data,
                dict
            ):

                # Check whether this looks like a candidate
                # evaluation result.
                evaluation_keys = {

                    "final_candidate_score",

                    "final_score",

                    "required_skill_score",

                    "preferred_skill_score",

                    "matched_skills",

                    "missing_skills"
                }


                if evaluation_keys.intersection(
                    data.keys()
                ):

                    return data


        except Exception:

            continue


    return None


# ============================================================
# SCREEN CANDIDATE USING AGENT
# ============================================================

def screen_candidate_with_agent(
    resume_path,
    job_description
):

    """
    Main production screening function.

    Candidate upload
        ↓
    LangChain Recruitment Agent
        ↓
    Evaluation Tool
        ↓
    Structured candidate result
    """

    agent = create_recruitment_agent()


    prompt = f"""
Screen this candidate for the following job.

JOB DESCRIPTION:
{job_description}

INTERNAL RESUME PATH:
{resume_path}

Required workflow:

1. Analyze the job requirements.
2. Analyze the resume.
3. Evaluate the resume against the job.
4. Use the evaluate_resume_against_job tool.
5. Return the actual structured evaluation.

Do not invent scores or candidate information.
"""


    response = agent.invoke({

        "messages": [

            {
                "role": "user",

                "content": prompt
            }
        ]
    })


    evaluation = (
        extract_evaluation_from_agent_response(
            response
        )
    )


    if evaluation is None:

        raise RuntimeError(
            "The Recruitment Agent completed its response "
            "but did not return the structured candidate "
            "evaluation."
        )


    return evaluation


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\nRecruiter AI Agent"
    )

    print(
        "Agent module loaded successfully."
    )

    print(
        "Use screen_candidate_with_agent() "
        "to screen a candidate."
    )