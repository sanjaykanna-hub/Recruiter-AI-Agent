
import json
import logging
from pathlib import Path

from langchain_core.tools import tool

from backend.database import (
    get_jobs,
    get_job,
    get_applications_for_job,
    get_application,
    save_agent_action,
    save_evaluation,
)
from backend.candidate_evaluator import evaluate_candidate


logger = logging.getLogger(__name__)


# --------------------------------------------------
# Helper
# --------------------------------------------------

def to_json(data):
    """Convert Python data into JSON-safe text."""
    return json.dumps(data, ensure_ascii=False, default=str)


def get_resume_path(application):
    """Find the resume path in common application/candidate fields."""

    resume_path = (
        application.get("resume_path")
        or application.get("resume_file")
        or application.get("file_path")
    )

    candidate = application.get("candidate")

    if isinstance(candidate, dict) and not resume_path:
        resume_path = (
            candidate.get("resume_path")
            or candidate.get("resume_file")
            or candidate.get("file_path")
        )

    return resume_path


# --------------------------------------------------
# Tool 1: List jobs
# --------------------------------------------------

@tool
def list_jobs(active_only: bool = True) -> str:
    """List available recruitment jobs and their requirements."""

    jobs = get_jobs(active_only=active_only)

    safe_jobs = [
        {
            "job_id": job["job_id"],
            "title": job["title"],
            "description": job["description"],
            "status": job["status"],
            "required_skills": job.get("required_skills", []),
            "preferred_skills": job.get("preferred_skills", []),
            "minimum_score": job.get("minimum_score", 70),
        }
        for job in jobs
    ]

    return to_json(safe_jobs)


# --------------------------------------------------
# Tool 2: Get job details
# --------------------------------------------------

@tool
def get_job_details(job_id: int) -> str:
    """Retrieve the description and requirements for a specific job."""

    job = get_job(job_id)

    if not job:
        return to_json({
            "error": f"Job ID {job_id} was not found."
        })

    return to_json({
        "job_id": job["job_id"],
        "title": job["title"],
        "description": job["description"],
        "status": job["status"],
        "required_skills": job.get("required_skills", []),
        "preferred_skills": job.get("preferred_skills", []),
        "minimum_score": job.get("minimum_score", 70),
    })


# --------------------------------------------------
# Tool 3: List applicants
# --------------------------------------------------

@tool
def list_job_applicants(job_id: int) -> str:
    """List applicants for a job with their stored evaluation scores."""

    job = get_job(job_id)

    if not job:
        return to_json({
            "error": f"Job ID {job_id} was not found."
        })

    applications = get_applications_for_job(job_id)
    applicants = []

    for app in applications:
        applicants.append({
            "application_id": app["application_id"],
            "candidate_id": app["candidate_id"],
            "candidate_name": app.get("name", "Unknown Candidate"),
            "application_status": app.get("status", "Under Review"),
            "final_score": app.get("final_score", 0),
            "required_skill_score": app.get("required_skill_score", 0),
            "experience_score": app.get("experience_score", 0),
            "education_score": app.get("education_score", 0),
            "matched_skills": app.get("matched_skills", []),
            "missing_skills": app.get("missing_skills", []),
        })

    return to_json({
        "job_id": job_id,
        "job_title": job["title"],
        "applicant_count": len(applicants),
        "applicants": applicants,
    })


# --------------------------------------------------
# Tool 4: Get application details
# --------------------------------------------------

@tool
def get_application_details(application_id: int) -> str:
    """Retrieve stored evaluation details for one application."""

    app = get_application(application_id)

    if not app:
        return to_json({
            "error": f"Application ID {application_id} was not found."
        })

    # Do not expose the complete evaluation JSON, which might contain
    # resume text or other personal information.
    return to_json({
        "application_id": app["application_id"],
        "job_id": app["job_id"],
        "candidate_id": app["candidate_id"],
        "candidate_name": app.get("name", "Unknown Candidate"),
        "status": app.get("status", "Under Review"),
        "final_score": app.get("final_score", 0),
        "matched_skills": app.get("matched_skills", []),
        "missing_skills": app.get("missing_skills", []),
        "evidence": app.get("evidence", []),
    })


# --------------------------------------------------
# Tool 5: Rank candidates
# --------------------------------------------------

@tool
def rank_candidates(job_id: int, top_n: int = 5) -> str:
    """
    Rank applicants using stored final evaluation scores.
    This tool does not evaluate new resumes.
    """

    job = get_job(job_id)

    if not job:
        return to_json({
            "error": f"Job ID {job_id} was not found."
        })

    top_n = max(1, min(int(top_n), 20))
    applications = get_applications_for_job(job_id)

    # Rank only applications with saved evaluations.
    evaluated = [
        app for app in applications
        if app.get("evaluation_id") is not None
        and app.get("final_score") is not None
    ]

    ranked = sorted(
        evaluated,
        key=lambda app: float(app.get("final_score") or 0),
        reverse=True,
    )

    results = []

    for position, app in enumerate(ranked[:top_n], start=1):
        results.append({
            "rank": position,
            "application_id": app["application_id"],
            "candidate_id": app["candidate_id"],
            "candidate_name": app.get("name", "Unknown Candidate"),
            "final_score": app.get("final_score", 0),
            "matched_skills": app.get("matched_skills", []),
            "missing_skills": app.get("missing_skills", []),
            "application_status": app.get("status", "Under Review"),
        })

    save_agent_action(
        job_id=job_id,
        action_type="candidate_ranking",
        action_result={
            "job_title": job["title"],
            "ranked_application_ids": [
                item["application_id"] for item in results
            ],
        },
        reasoning="Ranked applicants using stored final evaluation scores.",
    )

    return to_json({
        "job_id": job_id,
        "job_title": job["title"],
        "ranking_basis": "Stored final evaluation score, descending",
        "evaluated_applicant_count": len(evaluated),
        "ranked_candidates": results,
        "note": (
            "This ranking supports recruiter review and is not "
            "a hiring decision."
        ),
    })


# --------------------------------------------------
# Tool 6: Evaluate and save an application
# --------------------------------------------------

@tool
def evaluate_application(application_id: int) -> dict:
    """
    Evaluate an application's resume against its associated job
    description and save the result using the existing database function.
    """

    try:
        application = get_application(application_id)

        if not application:
            return {
                "success": False,
                "error": f"Application ID {application_id} was not found.",
            }

        job_id = application.get("job_id")

        if not job_id:
            return {
                "success": False,
                "error": "No job ID was found for this application.",
            }

        job = get_job(job_id)

        if not job:
            return {
                "success": False,
                "error": f"Job ID {job_id} was not found.",
            }

        resume_path = get_resume_path(application)

        if not resume_path:
            return {
                "success": False,
                "error": (
                    "No resume path was found in the application record. "
                    "Check the actual resume-path field in database.py."
                ),
            }

        # Resolve relative paths from the project root.
        project_root = Path(__file__).resolve().parent.parent
        resume_path = Path(resume_path)

        if not resume_path.is_absolute():
            resume_path = project_root / resume_path

        resume_path = resume_path.resolve()

        if not resume_path.is_file():
            return {
                "success": False,
                "error": "The resume file could not be found.",
            }

        job_description = (
            job.get("description")
            or job.get("job_description")
            or job.get("requirements")
        )

        if not job_description:
            return {
                "success": False,
                "error": "The job description is empty.",
            }

        # Run the existing evaluator.
        result = evaluate_candidate(
            str(resume_path),
            str(job_description),
        )

        if not isinstance(result, dict):
            return {
                "success": False,
                "error": "The evaluator returned an unexpected result.",
            }

        # Save the result. This assumes the database function accepts
        # (application_id, result); verify its signature first.
        save_evaluation(application_id, result)

        # Return useful fields only; do not send the full resume text
        # or the entire evaluator result to the language model.
        allowed_fields = [
            "candidate_name",
            "final_score",
            "final_candidate_score",
            "matched_skills",
            "matched_required_skills",
            "missing_skills",
            "missing_required_skills",
            "skills",
            "experience",
            "education",
            "summary",
            "recommendation",
        ]

        safe_result = {
            key: result[key]
            for key in allowed_fields
            if key in result
        }

        return {
            "success": True,
            "message": "Evaluation completed and saved.",
            "application_id": application_id,
            "job_id": job_id,
            "job_title": job.get("title") or job.get("job_title"),
            "evaluation": safe_result,
        }

    except Exception:
        logger.exception(
            "Evaluation failed for application ID %s",
            application_id,
        )

        return {
            "success": False,
            "error": (
                "Resume evaluation or saving failed. "
                "Check the FastAPI terminal logs."
            ),
        }
    
# --------------------------------------------------
# Tool 7: Evaluate all applicants for a job
# --------------------------------------------------

@tool
def evaluate_all_applications(job_id: int) -> dict:
    """
    Evaluate every applicant for a job and save each evaluation.
    Report successful and failed evaluations separately.
    """

    job = get_job(job_id)

    if not job:
        return {
            "success": False,
            "error": f"Job ID {job_id} was not found.",
        }

    applications = get_applications_for_job(job_id)

    if not applications:
        return {
            "success": True,
            "job_id": job_id,
            "job_title": job.get("title", "Unknown Job"),
            "total_applications": 0,
            "evaluated": 0,
            "failed": 0,
            "results": [],
            "message": "No applications were found for this job.",
        }

    results = []

    for application in applications:
        application_id = application.get("application_id")

        if application_id is None:
            results.append({
                "success": False,
                "error": "An application has no application ID.",
            })
            continue

        try:
            result = evaluate_application.invoke({
                "application_id": application_id
            })

            # Handle either a dictionary or a JSON string response.
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    result = {
                        "success": False,
                        "error": result,
                    }

            if not isinstance(result, dict):
                result = {
                    "success": False,
                    "error": "Unexpected evaluation response.",
                }

            results.append({
                "application_id": application_id,
                "success": result.get("success", False),
                "evaluation": result.get("evaluation"),
                "error": result.get("error"),
            })

        except Exception:
            logger.exception(
                "Bulk evaluation failed for application %s",
                application_id,
            )
            results.append({
                "application_id": application_id,
                "success": False,
                "error": "Evaluation failed. Check the API terminal logs.",
            })

    evaluated_count = sum(
        1 for item in results if item.get("success")
    )

    return {
        "success": evaluated_count == len(applications),
        "job_id": job_id,
        "job_title": job.get("title", "Unknown Job"),
        "total_applications": len(applications),
        "evaluated": evaluated_count,
        "failed": len(applications) - evaluated_count,
        "results": results,
        "message": (
            "Bulk evaluation completed. Review the results before "
            "making recruitment decisions."
        ),
    }



# --------------------------------------------------
# Complete tool list
# --------------------------------------------------


recruitment_tools = [
    list_jobs,
    get_job_details,
    list_job_applicants,
    get_application_details,
    rank_candidates,
    evaluate_application,
    evaluate_all_applications,
]
