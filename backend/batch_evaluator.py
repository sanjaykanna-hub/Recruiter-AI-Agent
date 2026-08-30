import os

from candidate_evaluator import (
    evaluate_candidate
)

from ranker import rank_candidates

from ranking_report import (
    generate_ranking_report
)


RESUME_FOLDER = "data/resumes"


def evaluate_all_resumes(
    resume_folder,
    job_description
):

    candidates = []

    for filename in os.listdir(
        resume_folder
    ):

        if not filename.lower().endswith(
            ".pdf"
        ):
            continue

        resume_path = os.path.join(
            resume_folder,
            filename
        )

        try:

            result = evaluate_candidate(
                resume_path,
                job_description
            )

            result["resume_file"] = filename

            candidates.append(
                result
            )

        except Exception as error:

            print(
                f"Error processing "
                f"{filename}: {error}"
            )

    return candidates


if __name__ == "__main__":

    print("\nEnter Job Description")
    print("--------------------")

    job_description = input(
        "Job Description: "
    )

    if not job_description.strip():

        print(
            "Job description cannot be empty."
        )

        exit()

    candidates = evaluate_all_resumes(
        RESUME_FOLDER,
        job_description
    )

    ranked_candidates = rank_candidates(
        candidates
    )

    generate_ranking_report(
        ranked_candidates
    )  